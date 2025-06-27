import re
import numpy as np
import psycopg2
from sentence_transformers import SentenceTransformer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from underthesea import word_tokenize
from collections import Counter
import os


backend_ip = os.getenv("BACKEND_IP")
database = os.getenv("DB")
db_user = os.getenv("DB_USER")
db_password = os.getenv("DB_PASSWORD")
db_port = os.getenv("DB_PORT")

print("Database: ", backend_ip)

embedder = SentenceTransformer('dangvantuan/vietnamese-embedding')



def get_connection():
    try:
        conn = psycopg2.connect(database=database,
                                user=db_user,
                                host=backend_ip,
                                password=db_password,
                                port=db_port)
        return conn
    except Exception as e:
        print(e)


def get_all_jobs():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT job_id, title, job.created_at, expire_date, job.field, location, max_salary, min_salary,"
        "company_id,province, company.name, company.logo, experience "
        "FROM job join company on job.company_id = company.id where expire_date > current_date and job.state= 'PENDING'")
    datasets = cursor.fetchall()
    keys = ["jobId", "title", "createdDate", "expireDate", "field", "location", "maxSalary", "minSalary",
            "companyId", "province", "companyName", "logo", "experience"]
    jobs = [dict(zip(keys, t)) for t in datasets]
    cursor.close()
    conn.close()
    return jobs


def cal_tfidf_without_save():
    jobs = get_all_jobs()
    titles = [job["title"] for job in jobs]
    if not titles:
        raise ValueError("Không có dữ liệu từ cơ sở dữ liệu!")
    vectorizer = TfidfVectorizer()
    tfidf_matrix = vectorizer.fit_transform(titles)
    return tfidf_matrix, vectorizer, jobs


def preprocess_text(text):
    text = text.lower()
    text = re.sub(r'[^\w\s]', '', text)
    # Tách từ
    tokens = word_tokenize(text)

    job_search_stopwords = [
        "tìm việc", "công việc", "việc làm", "tuyển", "tìm", "ứng tuyển", "tuyển dụng", "đăng ký", "đăng tuyển",
        "tìm kiếm", "việc", "nghề nghiệp", "lương", "hợp đồng", "phỏng vấn", "địa điểm",
        "giới thiệu", "cơ hội", "ứng viên", "mức lương", "nơi làm việc", "tìm", "đăng", "chọn",
        "xem", "tra cứu", "cập nhật", "gửi", "nhận", "mời", "xác nhận", "mới", "cũ", "hấp dẫn",
        "đầy đủ", "thích hợp", "phù hợp", "nhanh chóng", "tiện lợi", "dễ dàng", "toàn thời gian",
        "bán thời gian", "part-time", "full-time", "lương cao", "lương thấp", "lương hợp lý", "hỗ trợ",
        'và', 'của', 'theo', 'nhưng', 'hấp dẫn', 'tại', 'hay', 'có', 'từ', 'lên đến', 'up to'
    ]
    tokens = [word for word in tokens if word not in job_search_stopwords]
    return ' '.join(tokens)


def tf_idf_cal(text, tfidf_matrix, vectorizer, jobs):
    text = preprocess_text(text)
    input_vector = vectorizer.transform([text])
    cosine_similarities = cosine_similarity(input_vector, tfidf_matrix).flatten()
    for i, job in enumerate(jobs):
        job['similarity'] = cosine_similarities[i]
    filtered_jobs = [job for job in jobs if 0.5 < job['similarity'] < 0.9]
    sorted_jobs = sorted(filtered_jobs, key=lambda job: job['similarity'], reverse=True)
    return sorted_jobs


def sentences_embeddings(queries, jobs, jobs_similarities):
    titles = [job["title"] for job in jobs]
    corpus_embeddings = embedder.encode(titles)
    query_embeddings = embedder.encode(queries)
    titles_embeddings = []
    for embedding in corpus_embeddings:
        vector_1 = np.array(embedding).reshape(1, -1)
        titles_embeddings.append(vector_1)
    print("Input: ", queries)
    print("\n")
    for query, query_embedding in zip(queries, query_embeddings):
        jobs_copy = jobs
        vector_2 = np.array(query_embedding).reshape(1, -1)
        print("embedding: ", vector_2)
        for index, embedding in enumerate(titles_embeddings):
            similarity = cosine_similarity(embedding, vector_2)[0][0]
            jobs_copy[index]['similarity'] = similarity
            print("Title: ", jobs_copy[index]['title'])
            print("Similarity: ", jobs_copy[index]['similarity'])
            print("\n")
        jobs_copy = sorted(
            filter(lambda job: 0.45 < job['similarity'] < 0.9, jobs_copy),
            key=lambda job: job['similarity'],
            reverse=True)
        jobs_similarities.append(jobs_copy)



def recommend_jobs(input_text):
    tfidf_similarity = []
    jobs_similarities = []
    tfidf_matrix, vectorizer, jobs = cal_tfidf_without_save()
    for text in input_text:
        text = preprocess_text(text)
        tfidf_similarity.extend(tf_idf_cal(text, tfidf_matrix, vectorizer, jobs))
    sentences_embeddings(input_text, jobs, jobs_similarities)
    all_dicts = [d for sublist in jobs_similarities for d in sublist]
    id_counts = Counter(d['jobId'] for d in all_dicts)
    sorted_dicts = sorted(all_dicts, key=lambda d: id_counts[d['jobId']], reverse=True)
    tfidf_similarity.extend(sorted_dicts)
    seen_ids = []
    result=[]
    for d in tfidf_similarity:
        if d['jobId'] not in seen_ids:
            result.append(d)
            seen_ids.append(d['jobId'])
    return result


def get_user_search_keys(request):
    user_id = request.userId
    title = request.title
    history =[]
    if title is not None and title != '':
        history.append(title)
    if user_id is not None and user_id != '':
        connection = get_connection()
        cursor = connection.cursor()
        params = (user_id,)
        cursor.execute("SELECT * FROM user_entity_search_history u where u.user_entity_id= %s", params)
        sql_result = cursor.fetchall()
        if len(sql_result) == 0:
            return []
        for key in sql_result:
            history.append(key[1])
    if len(history) > 0:
        return recommend_jobs(history)
    else:
        return []


