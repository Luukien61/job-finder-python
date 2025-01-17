import base64
import io
import os
import re
import string

import cv2
import fitz  # PyMuPDF
from PIL import Image
from transformers import AutoTokenizer, AutoModelForTokenClassification
from transformers import pipeline

from FacialAttibute import predict_gender

output_dir = "extracted_images"
os.makedirs(output_dir, exist_ok=True)
tokenizer = AutoTokenizer.from_pretrained("NlpHUST/ner-vietnamese-electra-base")
model = AutoModelForTokenClassification.from_pretrained("NlpHUST/ner-vietnamese-electra-base")
person = []
loca = []
org = []


def pymuf_pdf(file: str):
    global gender
    person.clear()
    loca.clear()
    org.clear()
    full_text, ultimate_person, final_location, final_org, emails, phone, date, organization = "", "", "", "", [], "", "", ""
    try:
        with fitz.open(file) as pdf:
            for page_num in range(pdf.page_count):
                page = pdf[page_num]
                blocks = page.get_text("blocks")  # Lấy các block văn bản
                for block in blocks:
                    x0, y0, x1, y1, text, block_id, block_type = block
                    if block_type == 0:  # 0 là dạng văn bản, 1 là dạng ảnh
                        text = capitalize_all_caps(text)
                        full_text += text + ", "
                # get image
                if page_num == 0:
                    images = page.get_images(full=True)
                    for img_index, img in enumerate(images):
                        xref = img[0]
                        base_image = pdf.extract_image(xref)  # Trích xuất hình ảnh
                        image_bytes = base_image["image"]  # Dữ liệu nhị phân của ảnh
                        img_ext = base_image["ext"]  # Định dạng file (png, jpg, ...)
                        image = Image.open(io.BytesIO(image_bytes))  # Mở ảnh từ dữ liệu nhị phân
                        temp_path = f"{output_dir}/page_{page_num + 1}_img_{img_index + 1}.{img_ext}"
                        image.save(temp_path)
                        if not contains_face(temp_path):
                            os.remove(temp_path)
            full_text, email, phone, date = clean_text(full_text)
            emails.append(email)
            pattern = f"[{re.escape(string.punctuation.replace('@', ''))}]"
            full_text = re.sub(pattern, '', full_text)
            NlpHUST(full_text)
    except Exception as e:
        print(e)
    email = emails[0]
    poss_person = list(dict.fromkeys(person))
    if poss_person:
        ultimate_person = list(dict.fromkeys(person))[0]
    final_location = list(dict.fromkeys(loca))
    final_org = list(dict.fromkeys(org))
    if final_org:
        for orgs in final_org:
            if "đại học" in orgs.lower():
                organization = orgs
                break
            if "học viện" in orgs.lower():
                organization = orgs
                break
    os.remove(file)
    image_path = get_single_file_path(output_dir)
    encoded_image='not_found'
    gender = ''
    if image_path!='':
        encoded_image = encode_image_to_base64(image_path)
        try:
            gender = predict_gender(image_path)
            if gender == 'Male':
                gender = "Nam"
            elif gender == 'Female':
                gender = "Nữ"

        except Exception as e:
            print("Error: ", e)
        os.remove(image_path)
    result = {"name": ultimate_person,
            "email": email,
            "phone": phone,
            "date": date,
            "location": " ".join(final_location),
            "organization": organization,
            "gender": gender}
    print(result)
    return {"name": ultimate_person,
            "email": email,
            "phone": phone,
            "date": date,
            "location": " ".join(final_location),
            "organization": organization,
            "gender": gender,
            "image": encoded_image}


def get_gender(result):
    gender_diff = result['gender']
    diff = abs(gender_diff['Woman'] - gender_diff['Man'])
    if diff > 25:
        return True
    return False


def encode_image_to_base64(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')


def get_single_file_path(directory):
    files = os.listdir(directory)
    if(len(files) > 0):
        file_path = os.path.join(directory, files[0])
        if len(files) > 1:
            for index in range(1, len(files)):
                file_path = os.path.join(directory, files[index])
                os.remove(file_path)
        return file_path
    else: return ''


def clean_text(text: str):
    emails, phones, dates = "", "", ""
    url_pattern = r'((http|https):\/\/(www\.)?[a-zA-Z0-9@:%._\+~#=]{2,256}\.[a-z]{2,6}\b([-a-zA-Z0-9@:%_\+.~#?&//=]*))'
    text = re.sub(url_pattern, '', text)
    email_pattern = r'[\w\.-]+@[\w-]+\.[\w-]{2,3}'

    # Mẫu regex cho số điện thoại
    phone_pattern = r'\s(03|05|07|08|09|01[2689])[0-9]{8}'

    # Mẫu regex cho ngày sinh
    date_pattern = r'\b\d{2}[-/]\d{2}[-/]\d{4}\b'
    text = re.sub("[()]", "", text)

    email_match = re.search(email_pattern, text)
    phone_match = re.search(phone_pattern, text)
    date_match = re.search(date_pattern, text)
    if email_match:
        emails = email_match.group()
        text = re.sub(email_pattern, '', text)
    if phone_match:
        phones = phone_match.group().strip()
    if date_match:
        dates = date_match.group()
    return text, emails, phones, dates


def capitalize_all_caps(text):
    def capitalize_word(word):
        return word[0].upper() + word[1:].lower()

    words = text.split()
    text = ""
    for word in words:
        if word[0].isupper():
            word = capitalize_word(word)
        text += word + " "
    return text


def contains_face(image_path):
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
    image = cv2.imread(image_path)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))
    return len(faces) > 0


def NlpHUST(text: str):
    person_names = []
    location = []
    organize = []
    nlp = pipeline("ner", model=model, tokenizer=tokenizer)
    if len(text) > 512:
        mid = len(text) // 2
        part1 = text[:mid]
        NlpHUST(part1)
        part2 = text[mid:]
        NlpHUST(part2)
        return
    result = nlp(text)
    for item in result:
        entity = item['entity']
        if entity in ['B-PERSON', 'I-PERSON']:
            if entity == 'B-PERSON':
                person_names.append(",")
            person_names.append(item['word'])
        if entity in ['B-LOCATION', 'I-LOCATION']:
            if entity == 'B-LOCATION':
                location.append(",")
            location.append(item['word'])
        if entity in ['B-ORGANIZATION', 'I-ORGANIZATION']:
            if entity == 'B-ORGANIZATION':
                organize.append(",")
            organize.append(item['word'])
    person_names = refine_text(person_names)
    location = refine_text(location)
    organize = refine_text(organize)
    person.extend(person_names)
    loca.extend(location)
    org.extend(organize)


def refine_text(items):
    text = " ".join(items)
    text = re.sub(r'[#^%*&)(-+@$]', "", text)
    # text = text.lower()
    texts = text.split(',')
    new_texts = []
    for text in texts:
        text = text.strip()
        new_texts.append(text)
    text = list(dict.fromkeys(new_texts))
    if len(text) >= 1:
        text.pop(0)
    return text
