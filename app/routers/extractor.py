from fastapi import APIRouter, UploadFile, File, Body
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from langchain_community.document_loaders import PyMuPDFLoader
from dotenv import load_dotenv
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
import openai
import asyncio
import os
import json
import sys
import logging
import fitz  # PyMuPDF
import pytesseract
from PIL import Image
from io import BytesIO
from app.database.insertinSQL import insert_data

# Fix import path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

# Load environment variables
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

# MCP tool registration server
server_params = StdioServerParameters(
    command="python",
    args=["-m","app.services.manualMCP"],
    env=None
)

# OpenAI function tool schema
tools_for_openai = [
    {
        "type": "function",
        "name": "extract_details_from_text",
        "function": {
            "name": "extract_details_from_text",
            "description": "Extracts Aadhar and mobile numbers from raw input text",
            "parameters": {
                "type": "object",
                "properties": {
                    "text": {
                        "type": "string",
                        "description": "The raw text that may contain Aadhar or mobile numbers"
                    }
                },
                "required": ["text"],
            },
        }
    },

    {
        "type": "function",
        "name": "validate_from_db",
        "function": {
            "name": "validate_from_db",
            "description": "Validates aadhar and mobile number",
            "parameters": {
                "type": "object",
                "properties": {
                    "aadhar": {
                        "type": "string",
                        "description": "Aadhar number to check"
                    },
                    "mobile": {
                        "type": "string",
                        "description": "Mobile number to check"
                    }
                },
                "required": ["aadhar", "mobile"]
            }
        }
    }
]

# FastAPI router
router = APIRouter(tags=["Extractor"])

@router.post('/mcp_extract')
async def extract_from_pdf(file: UploadFile = File(...)):
    if not file.filename.endswith('.pdf'):
        return JSONResponse(content={"error": "Only PDF files are allowed."}, status_code=400)

    # Save uploaded PDF
    os.makedirs("../pdfuploads", exist_ok=True)
    file_path = os.path.join("../pdfuploads", file.filename)
    with open(file_path, "wb") as f:
        f.write(file.file.read())

    # === Step 1: Try text extraction ===
    text = ""
    try:
        loader = PyMuPDFLoader(file_path)
        docs = loader.load()
        text = ''.join(doc.page_content for doc in docs)
    except Exception as e:
        logging.warning(f"Text loader failed: {e}")

    # === Step 2: If no text found, fallback to OCR using pytesseract ===
    if not text.strip():
        try:
            doc = fitz.open(file_path)
            ocr_text = ""
            for page_index in range(len(doc)):
                page = doc.load_page(page_index)
                images = page.get_images(full=True)
                for img_index, img in enumerate(images):
                    xref = img[0]
                    base_image = doc.extract_image(xref)
                    image_bytes = base_image["image"]
                    image = Image.open(BytesIO(image_bytes)).convert("L")  # grayscale for better OCR
                    ocr_text += pytesseract.image_to_string(image) + "\n"
            text = ocr_text
        except Exception as e:
            return JSONResponse(
                content={"error": f"OCR text extraction failed: {e}"},
                status_code=500
            )

    if not text.strip():
        return JSONResponse(content={"error": "No text could be extracted from the PDF."}, status_code=400)

    # === Step 3: MCP + OpenAI LLM Function Calling ===
    try:
        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()

                # Prepare prompt
                user_prompt = f"""Extract Aadhar and mobile numbers from this document. 
                Use tool 'extract_details_from_text' for actual extraction. Do not format or alter the text:\n{text}"""

                # Send to OpenAI
                response = openai.chat.completions.create(
                    model="gpt-4o",
                    messages=[{"role": "user", "content": user_prompt}],
                    tools=tools_for_openai,
                    tool_choice="auto"
                )
                tool_calls = response.choices[0].message.tool_calls
                if not tool_calls or not hasattr(tool_calls[0], "function"):
                    return JSONResponse(content={"error": "OpenAI did not trigger any tool."}, status_code=400)

                tool_call = tool_calls[0]
                tool_name = tool_call.function.name
                arguments = json.loads(tool_call.function.arguments)
                # Execute the tool
                result = await session.call_tool(tool_name, arguments=arguments)
                try:
                    result_dict = result.dict()
                except AttributeError:
                    try:
                        result_dict = json.loads(result.json())
                    except Exception:
                        result_dict = {"aadhar_numbers": [], "mobile_numbers": [], "error": str(result)}

                # Extract numbers
                print("line 136 \n",result_dict)
                # Extract raw tool output
                raw_tool_output = result_dict.get("content", [])[0].get("text", "")

                # Parse stringified JSON
                try:
                    result_dict = json.loads(raw_tool_output)
                except json.JSONDecodeError as e:
                    return JSONResponse(content={"error": f"Failed to parse tool output: {str(e)}"}, status_code=500)

                # Extract Aadhar and mobile numbers
                aadhars = result_dict.get("aadhar_numbers", [])
                mobiles = result_dict.get("mobile_numbers", [])
                # Format output
                aadhar_str = ", ".join(aadhars) if aadhars else "None"
                mobile_str = ", ".join(mobiles) if mobiles else "None"
                insert_data(aadhar_str.replace(" ", ""), mobile_str)
                print(aadhar_str,mobile_str)
               
                beautified_message = (
                    f"The Aadhar number(s) extracted: {aadhar_str}. "
                    f"The Mobile number(s) extracted: {mobile_str}"
                )

                # Return final response
                return JSONResponse(content={"result": beautified_message})

    except Exception as e:
        logging.exception("MCP/OpenAI integration failed.")
        return JSONResponse(status_code=500, content={"error": f"MCP/OpenAI integration failed: {e}"})
    

### Validation API###

class ValidationRequest(BaseModel):
    aadhar: str
    mobile: str

@router.post("/validate_data_llm")
async def validate_data_llm(payload: ValidationRequest = Body(...)):
    try:
        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()

                user_prompt = (
                    f"Validate if the Aadhar number {payload.aadhar} and mobile number {payload.mobile} exist in the database. "
                    f"Use 'validate_from_db' tool to perform the check."
                )

                response = openai.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": user_prompt}],
                tools=tools_for_openai,
                tool_choice="auto"
            )

            tool_calls = response.choices[0].message.tool_calls
            if not tool_calls:
                return JSONResponse(status_code=400, content={"error": "No tool called by OpenAI."})

            tool_call = tool_calls[0]
            tool_name = tool_call.function.name
            arguments = json.loads(tool_call.function.arguments)
            print(tool_name, arguments)

            # Call the MCP tool (validate_from_db should now return separate flags)
            result = await session.call_tool(tool_name, arguments=arguments)

            try:
                result_dict = result.dict()
            except AttributeError:
                try:
                    result_dict = json.loads(result.json())
                except Exception:
                    result_dict = {
                        "aadhar_exists": False,
                        "mobile_exists": False,
                        "error": str(result)
                    }

            return {
                "aadhar": payload.aadhar,
                "mobile": payload.mobile,
                "aadhar_exists_in_database": result_dict.get("aadhar_exists", False),
                "mobile_exists_in_database": result_dict.get("mobile_exists", False)
            }

    except Exception as e:
        logging.exception("Validation via MCP/OpenAI failed.")
        return JSONResponse(status_code=500, content={"error": f"MCP validation failed: {e}"})