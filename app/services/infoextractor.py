import re
import logging
import requests
from fastapi import  HTTPException

class DetailExtraction:
    def __init__(self, text, log_file = 'extractor_errors.log'):
        logging.basicConfig(filename=log_file, level=logging.ERROR)
        self.file = text
    def extractText(self):
        aadhar_pattern = r'\b\d{4}[\s\-]?\d{4}[\s\-]?\d{4}\b'
        mobile_pattern = r'\b[6-9]\d{9}\b'
        try:
            aadhar_numbers = re.findall(aadhar_pattern, self.file)
            mobile_numbers = re.findall(mobile_pattern, self.file)
            return aadhar_numbers, mobile_numbers
        except requests.RequestException as e:
            raise HTTPException(status_code=503, detail=f"Extraction failed: {e}")
            
        
        