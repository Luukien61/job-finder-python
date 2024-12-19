import fitz  # PyMuPDF
from pytesseract import image_to_data, Output
from PIL import Image
import io


# Hàm chuyển PDF sang hình ảnh và xử lý OCR từng block
def extract_text_from_pdf(pdf_path):
    full_text = ""
    # Mở file PDF
    with fitz.open(pdf_path) as pdf:
        for page_num in range(len(pdf)):
            # Render trang PDF thành hình ảnh
            page = pdf[page_num]
            pix = page.get_pixmap(dpi=600)  # Tăng DPI để tăng độ chính xác
            image = Image.open(io.BytesIO(pix.tobytes("png")))  # Chuyển sang đối tượng PIL.Image

            # Dùng pytesseract để phân tích văn bản theo block
            data = image_to_data(image, output_type=Output.DICT)
            for i in range(len(data['text'])):
                if int(data['level'][i]) == 2:  # Cấp độ 2 là block
                    text = data['text'][i].strip()
                    if text:  # Nếu block không trống
                        full_text += text + "\n"
    return full_text


# Đường dẫn tới file PDF
pdf_path = "Nguyễn-Lan-Anh-CV-marketing.pdf"

# Trích xuất văn bản từ PDF
text = extract_text_from_pdf(pdf_path)

# In kết quả
print("Kết quả trích xuất theo block:")
print(text)
