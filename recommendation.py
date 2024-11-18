import pandas as pd
import re
from underthesea import word_tokenize
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
# Đọc dữ liệu từ file CSV


from sqlalchemy import create_engine
from underthesea.pipeline.dependency_parse import dependency_parse

# Thay đổi thông tin kết nối cho phù hợp với cơ sở dữ liệu của bạn
#engine = create_engine('mysql+pymysql://username:password@localhost/db_name')

# Truy vấn dữ liệu từ bảng jobs
# data = pd.read_sql('SELECT job_id, title, skills FROM jobs', con=engine)

data = pd.read_csv('jobs.csv')
# Tiền xử lý mô tả công việc

def get_date(text):
    patterns = [
        # DD/MM/YYYY
        r'(\d{1,2})[/](\d{1,2})[/](\d{4})',
        # DD-MM-YYYY
        r'(\d{1,2})[-](\d{1,2})[-](\d{4})',
        # DD.MM.YYYY
        r'(\d{1,2})[.](\d{1,2})[.](\d{4})'
    ]
    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            day, month, year = match.groups()
            day = int(day)
            month = int(month)
            year = int(year)

            # Kiểm tra tính hợp lệ của ngày tháng
            if 1 <= day <= 31 and 1 <= month <= 12 and 1900 <= year <= 2024:
                print(f"{day:02d}/{month:02d}/{year}")
                return {
                    'day': day,
                    'month': month,
                    'year': year,
                    'full_date': f"{day:02d}/{month:02d}/{year}"
                }
    return None

def preprocess_text(text):
    # Chuyển về chữ thường
    text = text.lower()
    text = re.sub(r'[^\w\s]', '', text)
    # Tách từ
    tokens = word_tokenize(text)

    # Loại bỏ từ dừng (có thể thêm danh sách từ dừng riêng)
    stop_words = {'và', 'của', 'theo', 'nhưng','hấp dẫn','tại','hay', 'có', 'từ', 'lên đến', 'up to'}  # Bạn có thể mở rộng danh sách này
    tokens = [word for word in tokens if word not in stop_words]

    return ' '.join(tokens)

def preprocess_skills(skills):
    return [skill.strip() for skill in skills.split(',')]

data['processed_skills'] = data['skills'].apply(preprocess_skills)

data['processed_title'] = data['title'].apply(preprocess_text)

data['combined'] = data['processed_title'] + ' ' + data['processed_skills'].apply(lambda x: ' '.join(x))

# Tạo TF-IDF Vectorizer
vectorizer = TfidfVectorizer()
tfidf_matrix = vectorizer.fit_transform(data['combined'])

# Tính toán độ tương đồng cosine
cosine_sim = cosine_similarity(tfidf_matrix, tfidf_matrix)

# Hàm gợi ý công việc
def recommend_jobs(input_text):
    # Chuyển đổi văn bản đầu vào thành vector TF-IDF
    input_vector = vectorizer.transform([input_text])

    # Tính toán độ tương đồng cosine giữa vector đầu vào và ma trận TF-IDF
    cosine_similarities = cosine_similarity(input_vector, tfidf_matrix).flatten()

    # Thêm độ tương đồng vào DataFrame
    data['similarity'] = cosine_similarities

    # Sắp xếp theo độ tương đồng và lấy top_n công việc hàng đầu
    filtered_data = data[data['similarity'] >= 0.2]

    # Sắp xếp theo độ tương đồng và lấy top_n công việc hàng đầu
    recommended_jobs = filtered_data.sort_values(by='similarity', ascending=False)

    return recommended_jobs[['job_id', 'title', 'similarity']]

if __name__ == "__main__":
    input_text = "Tôi đang tìm kiếm một công việc liên quan đến java."
    jobs = recommend_jobs(input_text)
    print(jobs)