from mcp.server.fastmcp import FastMCP
from app.services.infoextractor import DetailExtraction
from app.database.insertinSQL import validate_aadhar_mobile

# Create the server
server = FastMCP("Extractor")
# server = FastMCP("Extractor")

# Define the calculator tool
print("10")
@server.tool(name="extract_details_from_text", description="Extracts Aadhar and mobile numbers from raw input text")
def extract_details_from_text(text: str):
    try:
        print("Received input:", text)
        # text = input_data.get("text", "")
        extractor = DetailExtraction(text=text)
        aadhar_list, mobile_list = extractor.extractText()
        print("Extracted Aadhar:", aadhar_list, "Mobiles:", mobile_list)
        return {
            "aadhar_numbers": aadhar_list,
            "mobile_numbers": mobile_list
        }
    except Exception as e:
        print("Error in tool:", e)
        return {
            "aadhar_numbers": [],
            "mobile_numbers": [],
            "error": str(e)
        }
    
@server.tool(name="validate_from_db", description="Validates aadhar and mobile number")
def validate_from_db(aadhar: str, mobile: str):
    validation_result = validate_aadhar_mobile(aadhar=aadhar, mobile=mobile)
    return {
        "aadhar_exists": validation_result["aadhar_exists"],
        "mobile_exists": validation_result["mobile_exists"]
    }

# Run the server over stdio
if __name__ == "__main__":
    server.run()