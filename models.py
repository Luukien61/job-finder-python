from pydantic import BaseModel

# Mô hình dữ liệu
class Item(BaseModel):
    id: int = None
    name: str
    description: str = None
