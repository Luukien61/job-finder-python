import shutil
from datetime import datetime
from pathlib import Path
from typing import List, Optional

import uvicorn
from fastapi import FastAPI, UploadFile
from fastapi import HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from database import get_connection
from handle_pdf import pymuf_pdf
from recommendation import get_user_search_keys
from speech_to_text import transcribe_audio
from upload import upload_file_to_s3

app = FastAPI()
BUCKET_NAME = 'jobfinder-kienluu'
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Thêm domain frontend ở đây
    allow_credentials=True,
    allow_methods=["*"],  # Cho phép tất cả các phương thức (GET, POST, etc.)
    allow_headers=["*"],  # Cho phép tất cả các headers
)

connection = get_connection()
class UserRequest(BaseModel):
    userId: Optional[str] = None
    title: Optional[str] = None

class Job(BaseModel):
    jobId: int
    title: str
    createdDate: datetime
    expireDate: datetime
    field: str
    location: str
    maxSalary: int  # Có thể null
    minSalary: int  # Có thể null
    companyId: str
    province: Optional[str]
    companyName: str
    logo: str
    experience: Optional[int]
@app.get("/connect")
def get_connection():
    return {"status": "Connected"}

@app.post("/recommendations",response_model=List[Job])
def get_recommendations(request: UserRequest):
    print(request)
    jobs = get_user_search_keys(request)
    return jobs

@app.post("/cv")
def create_new_item(file: UploadFile):
    file_path = UPLOAD_DIR / file.filename
    # Lưu file PDF vào thư mục
    with file_path.open("wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    url = upload_file_to_s3(str(file_path), BUCKET_NAME)
    return {"url": url}


UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)  # Tạo thư mục nếu chưa tồn tại


@app.post("/upload")
def upload_file(file: UploadFile):
    # Đường dẫn lưu file
    file_path = UPLOAD_DIR / file.filename
    # Lưu file PDF vào thư mục
    with file_path.open("wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    try:
        result = pymuf_pdf(str(file_path))
    except Exception as e:
        return {"error": str(e)}
   # url = upload_file_to_s3(str(file_path), BUCKET_NAME)
    return result

class URLRequest(BaseModel):
    url: str
@app.post("/transcribe")
async def transcribe(request: URLRequest):
    try:
        text = transcribe_audio(request.url)
        return {
            "text": text,
        }
    except Exception as e:
        raise  HTTPException(status_code=400, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
