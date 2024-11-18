import shutil
from pathlib import Path
from typing import List

import uvicorn
from fastapi import FastAPI, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware

from crud import get_items, get_item, create_item
from database import get_connection
from handle_pdf import pymuf_pdf
from upload import upload_file_to_s3
from models import Item

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


@app.get("/items", response_model=List[Item])
def read_items():
    items = get_items(connection)
    return items


@app.get("/items/{item_id}", response_model=Item)
def read_item(item_id: int):
    item = get_item(connection, item_id)
    if item:
        return item
    raise HTTPException(status_code=404, detail="Item not found")

@app.get("/connect")
def get_connection():
    return {"status": "Connected"}

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


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
