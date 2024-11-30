# import os
# import re
# from datetime import datetime
#
# import numpy as np
# from sentence_transformers import SentenceTransformer
# import joblib
# import psycopg2
# from sklearn.feature_extraction.text import TfidfVectorizer
# from sklearn.metrics.pairwise import cosine_similarity
# from underthesea import word_tokenize
#
# data_path = 'tf-idf'
#
#
# def connect_db():
#     try:
#         conn = psycopg2.connect(database="jobfinder",
#                                 user="postgres",
#                                 host='localhost',
#                                 password="Luudinhkien_2003",
#                                 port=5432)
#         cursor = conn.cursor()
#         cursor.execute(
#             "SELECT job_id, title, job.created_at, expire_date, job.field, location, max_salary, min_salary,"
#             "company_id,province, company.name, company.logo "
#             "FROM job join company on job.company_id = company.id where expire_date > current_date")
#         datasets = cursor.fetchall()
#         keys = ["jobId", "title", "createdDate", "expireDate", "field", "location", "maxSalary", "minSalary",
#                 "companyId", "province", "companyName", "logo"]
#         jobs = [dict(zip(keys, t)) for t in datasets]
#         cursor.close()
#         return jobs
#     except Exception as e:
#         print(e)
#
#
# def cal_tfidf_save():
#     check_directory(data_path)
#     current_date = datetime.now().strftime('%Y-%m-%d')
#     tfidf_matrix_file = f"tfidf_matrix{current_date}.pkl"
#     vectorizer_file = f"vectorizer{current_date}.pkl"
#     tfidf_matrix_path = os.path.join(data_path, tfidf_matrix_file)
#     vectorizer_path = os.path.join(data_path, vectorizer_file)
#     if not os.path.exists(tfidf_matrix_path):
#         titles = connect_db()
#         if not titles:
#             raise ValueError("Không có dữ liệu từ cơ sở dữ liệu!")
#         vectorizer = TfidfVectorizer()
#         tfidf_matrix = vectorizer.fit_transform(titles)
#         joblib.dump(tfidf_matrix, tfidf_matrix_path)
#         joblib.dump(vectorizer, vectorizer_path)
#     else:
#         tfidf_matrix = joblib.load(tfidf_matrix_path)
#         vectorizer = joblib.load(vectorizer_path)
#
#     return tfidf_matrix, vectorizer
#     # vocabulary = vectorizer.vocabulary_
#     # words = vectorizer.get_feature_names_out()
#     # word_index = words.tolist().index("java")
#     # tfidf_values = tfidf_matrix.toarray()[:, word_index]
#     # print(f"TF-IDF của từ 'java' trong các văn bản: {tfidf_values}")
#     # cosine_sim = cosine_similarity(tfidf_matrix, tfidf_matrix)
#     # print(cosine_sim)
#
#
# def cal_tfidf_without_save():
#     jobs = connect_db()
#     titles = [job["title"] for job in jobs]
#     if not titles:
#         raise ValueError("Không có dữ liệu từ cơ sở dữ liệu!")
#     vectorizer = TfidfVectorizer()
#     tfidf_matrix = vectorizer.fit_transform(titles)
#     return tfidf_matrix, vectorizer, jobs
#
#
# def check_directory(path):
#     if not os.path.exists(path):
#         os.makedirs(path)
#
#
#
# def preprocess_text(text):
#     text = text.lower()
#     text = re.sub(r'[^\w\s]', '', text)
#     # Tách từ
#     tokens = word_tokenize(text)
#
#     job_search_stopwords = [
#         "tìm việc", "công việc", "việc làm","tuyển","tìm", "ứng tuyển", "tuyển dụng", "đăng ký", "đăng tuyển",
#         "tìm kiếm", "việc", "nghề nghiệp", "lương", "hợp đồng", "phỏng vấn", "địa điểm",
#         "giới thiệu", "cơ hội", "ứng viên", "mức lương", "nơi làm việc", "tìm", "đăng", "chọn",
#         "xem", "tra cứu", "cập nhật", "gửi", "nhận", "mời", "xác nhận", "mới", "cũ", "hấp dẫn",
#         "đầy đủ", "thích hợp", "phù hợp", "nhanh chóng", "tiện lợi", "dễ dàng", "toàn thời gian",
#         "bán thời gian", "part-time", "full-time", "lương cao", "lương thấp", "lương hợp lý", "hỗ trợ",
#         'và', 'của', 'theo', 'nhưng', 'hấp dẫn', 'tại', 'hay', 'có', 'từ', 'lên đến','up to'
#     ]
#     tokens = [word for word in tokens if word not in job_search_stopwords]
#     return ' '.join(tokens)
#
#
# def recommend_jobs(input_text):
#     input_text = preprocess_text(input_text)
#     tfidf_matrix, vectorizer, jobs = cal_tfidf_without_save()
#     input_vector = vectorizer.transform([input_text])
#     cosine_similarities = cosine_similarity(input_vector, tfidf_matrix).flatten()
#
#     for i, job in enumerate(jobs):
#         job['similarity'] = cosine_similarities[i]
#
#     filtered_jobs = [job for job in jobs if 0.2 < job['similarity'] < 0.9]
#     sorted_jobs = sorted(filtered_jobs, key=lambda job: job['similarity'], reverse=True)
#     for job in sorted_jobs:
#         print(job['title'], job['similarity'])
#         print('\n')
#
# def sentences_embeddings():
#     jobs = connect_db()
#     titles = [job["title"] for job in jobs]
#     embedder = SentenceTransformer('dangvantuan/vietnamese-embedding')
#     corpus_embeddings = embedder.encode(titles)
#     queries = ['Kỹ sư phát triển phần mềm', 'java', 'kế toán']
#     query_embeddings = embedder.encode(queries)
#
#     for query, query_embedding in zip(queries, query_embeddings):
#         similarity = []
#         vector_2 = np.array(query_embedding).reshape(1, -1)
#         for embedding in corpus_embeddings:
#             vector_1= np.array(embedding).reshape(1, -1)
#             similarity.append(cosine_similarity(vector_1, vector_2)[0][0])
#         print("Query: ", query)
#         print("\n")
#         sentences = list(zip(titles,similarity ))
#         sentences = [job for job in sentences if 0.15 < job[1] < 0.9]
#         sentences = sorted(sentences, key=lambda x: x[1], reverse=True)
#         print(sentences)
#
# if __name__ == "__main__":
#     input_text = "Java"
#     recommend_jobs(input_text)
#     # print(jobs)
#     # connect_db()
# # preprocess_text("Lưu Đình Kiên là sinh viên nghành Công nghệ thông tin của Học viện kỹ thuật Mật Mã")
