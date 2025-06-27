import joblib
import numpy as np
import psycopg2
import scipy
from sentence_transformers import SentenceTransformer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

dict_map = {
    "òa": "oà",
    "Òa": "Oà",
    "ÒA": "OÀ",
    "óa": "oá",
    "Óa": "Oá",
    "ÓA": "OÁ",
    "ỏa": "oả",
    "Ỏa": "Oả",
    "ỎA": "OẢ",
    "õa": "oã",
    "Õa": "Oã",
    "ÕA": "OÃ",
    "ọa": "oạ",
    "Ọa": "Oạ",
    "ỌA": "OẠ",
    "òe": "oè",
    "Òe": "Oè",
    "ÒE": "OÈ",
    "óe": "oé",
    "Óe": "Oé",
    "ÓE": "OÉ",
    "ỏe": "oẻ",
    "Ỏe": "Oẻ",
    "ỎE": "OẺ",
    "õe": "oẽ",
    "Õe": "Oẽ",
    "ÕE": "OẼ",
    "ọe": "oẹ",
    "Ọe": "Oẹ",
    "ỌE": "OẸ",
    "ùy": "uỳ",
    "Ùy": "Uỳ",
    "ÙY": "UỲ",
    "úy": "uý",
    "Úy": "Uý",
    "ÚY": "UÝ",
    "ủy": "uỷ",
    "Ủy": "Uỷ",
    "ỦY": "UỶ",
    "ũy": "uỹ",
    "Ũy": "Uỹ",
    "ŨY": "UỸ",
    "ụy": "uỵ",
    "Ụy": "Uỵ",
    "ỤY": "UỴ",
}

embeddings_path = 'embeddings/word2vec_vi_words_100dims.joblib'
raw_file_path = '/home/luukien/Downloads/word2vec_vi_words_100dims.txt'


def replace_all(text, dict_map):
    for i, j in dict_map.items():
        text = text.replace(i, j)
    return text


def load_embeddings_with_phrases(file_path, vector_size=100):
    embeddings = {}
    with open(file_path, 'r', encoding='utf-8') as f:
        f.readline()  # Bỏ qua dòng đầu tiên

        for line in f:
            parts = line.strip().split()  # Tách các trường bằng khoảng trắng
            if len(parts) < vector_size + 1:  # Nếu không đủ dữ liệu, bỏ qua
                print(f"Bỏ qua dòng không hợp lệ: {line}")
                continue

            # Phần từ (word) là tất cả các từ trước vector
            word = " ".join(parts[:-vector_size])
            try:
                vector = list(map(float, parts[-vector_size:]))  # Lấy vector cuối
                embeddings[word] = vector
            except ValueError:
                print(f"Bỏ qua dòng có vector không hợp lệ: {line}")
                continue

    return embeddings


def save_embeddings_with_joblib(embeddings, output_path):
    joblib.dump(embeddings, output_path)
    print(f"Embeddings đã được lưu vào {output_path}")


def load_embeddings_with_joblib(file_path):
    return joblib.load(file_path)

def tf_idf(titles):
    vectorizer = TfidfVectorizer()
    tfidf_matrix = vectorizer.fit_transform(titles)
    feature_names = vectorizer.get_feature_names_out()
    tfidf_weights = tfidf_matrix.toarray()
    # Ví dụ: Câu đầu tiên
    print("Từ và trọng số TF-IDF cho câu 1:")
    for word, weight in zip(feature_names, tfidf_weights[0]):
        print(f"{word}: {weight}")

def sentences_embeddings():
    jobs = connect_db()
    titles = [job["title"] for job in jobs]
    embedder = SentenceTransformer('dangvantuan/vietnamese-embedding')
    corpus_embeddings = embedder.encode(titles)
    queries = ['Kỹ sư phát triển phần mềm', 'java', 'kế toán']
    query_embeddings = embedder.encode(queries)

    for query, query_embedding in zip(queries, query_embeddings):
        similarity = []
        vector_2 = np.array(query_embedding).reshape(1, -1)
        for embedding in corpus_embeddings:
            vector_1= np.array(embedding).reshape(1, -1)
            similarity.append(cosine_similarity(vector_1, vector_2)[0][0])
        print("Query: ", query)
        print("\n")
        sentences = list(zip(titles,similarity ))
        sentences = [job for job in sentences if 0.15 < job[1] < 0.9]
        sentences = sorted(sentences, key=lambda x: x[1], reverse=True)
        print(sentences)


def sentences_embeddings2():
    jobs = connect_db()
    titles = [job["title"] for job in jobs]
    embedder = SentenceTransformer('dangvantuan/vietnamese-embedding')
    corpus_embeddings = embedder.encode(titles)
    queries = ['Kỹ sư phát triển phần mềm', 'java developer', 'kế toán']
    query_embeddings = embedder.encode(queries)
    for query, query_embedding in zip(queries, query_embeddings):
        distances = scipy.spatial.distance.cdist([query_embedding], corpus_embeddings, "cosine")[0]
        print("Query: ", query)
        print("\n")
        sentences = list(zip(titles, distances))
        sentences = sorted(sentences, key=lambda x: x[1])
        print(sentences)

def connect_db():
    try:
        conn = psycopg2.connect(database="jobfinder",
                                user="postgres",
                                host='localhost',
                                password="Luudinhkien_2003",
                                port=5432)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT title "
            "FROM job where expire_date > current_date")
        datasets = cursor.fetchall()
        keys = ["title"]
        jobs = [dict(zip(keys, t)) for t in datasets]
        cursor.close()
        return jobs
    except Exception as e:
        print(e)


if __name__ == '__main__':
    sentences_embeddings()
