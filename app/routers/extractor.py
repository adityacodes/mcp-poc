from fastapi import APIRouter, UploadFile, File
from pydantic import BaseModel
from fastapi.responses import JSONResponse
from app.services.infoextractor import DetailExtraction
from langchain_community.document_loaders import PyMuPDFLoader, UnstructuredPDFLoader
import os
router = APIRouter(tags=["Extractor"])

@router.post('/extract')
def funtionality(file: UploadFile = File(...)):
    if not file.filename.endswith('.pdf'):
        return JSONResponse(content={"error": "Only PDF files are allowed."}, status_code=400)
    
    os.makedirs("../pdfuploads", exist_ok=True)
    print("line 15 \n",file.filename)
    filePath = os.path.join("../pdfuploads", file.filename)
    text = ""
    # try:
    with open(filePath, 'wb') as rw:
        rw.write(file.file.read())
        
    loader = PyMuPDFLoader(filePath)
    docs = loader.load()
    print(docs)
    for doc in docs:
        text += doc.page_content
    # if text == "":
    #     loader = UnstructuredPDFLoader(filePath, strategy="ocr_only")
    #     docss = loader.load()
    #     for doc in docss:
    #         text += doc.page_content
    print(text)          
    extractr = DetailExtraction(text=text)
    aadhar, mobile = extractr.extractText()
    
    return {'Aadhar': aadhar, "Mobile": mobile}
    # except Exception as e:
    #     return JSONResponse(status_code=400,content={"error": str(e), "code": 400})

