Lỗi bạn gặp phải cho thấy Ubuntu 24.04 của bạn không tìm thấy các gói `python3.11`, `python3.11-dev`, và `python3.11-venv` trong nguồn phần mềm hiện tại.

Trên Ubuntu 24.04, Python mặc định thường là **Python 3.12**, vì vậy gói `python3.11` không còn trong repository mặc định nữa.

### Cách cài Python 3.11 trên Ubuntu 24.04

Bạn có hai hướng:

---

## ✅ **Cách 1: Dùng `deadsnakes PPA` (khuyến nghị)**

1. **Thêm PPA (Personal Package Archive):**

```bash
sudo add-apt-repository ppa:deadsnakes/ppa
sudo apt update
```

> ⚠️ Nếu bạn bị lỗi `add-apt-repository: command not found`, cài thêm:

```bash
sudo apt install software-properties-common
```

2. **Cài đặt Python 3.11 và các gói liên quan:**

```bash
sudo apt install python3.11 python3.11-venv python3.11-dev
```

3. **Kiểm tra phiên bản:**

```bash
python3.11 --version
```

---

## ✅ **Cách 2: Biên dịch Python 3.11 từ mã nguồn (khi không dùng PPA được)**

```bash
sudo apt update
sudo apt install -y build-essential zlib1g-dev libncurses5-dev libgdbm-dev \
  libnss3-dev libssl-dev libreadline-dev libffi-dev wget libbz2-dev

cd /usr/src
sudo wget https://www.python.org/ftp/python/3.11.9/Python-3.11.9.tgz
sudo tar -xf Python-3.11.9.tgz
cd Python-3.11.9
sudo ./configure --enable-optimizations
sudo make -j$(nproc)
sudo make altinstall
```

> Dùng `make altinstall` để tránh ghi đè `python3` mặc định.

Kiểm tra:

```bash
python3.11 --version
```

---

### 2. **Gỡ Python 3.11 global theo hệ điều hành**

#### **Trên Ubuntu/Linux**
Nếu bạn đã cài Python 3.11 qua `apt` (như hướng dẫn trước: `sudo apt install python3.11 python3.11-dev python3.11-venv`), bạn có thể gỡ nó như sau:

##### **Bước 1: Kiểm tra Python 3.11**
- Xác nhận Python 3.11 được cài:
  ```bash
  python3.11 --version
  ls /usr/bin/python3.11
  ```

##### **Bước 2: Gỡ các gói liên quan đến Python 3.11**
- Gỡ các gói Python 3.11:
  ```bash
  sudo apt remove --purge python3.11 python3.11-dev python3.11-venv
  ```
  - `--purge`: Xóa cả các file cấu hình liên quan.
- Kiểm tra và xóa các phụ thuộc không còn cần thiết:
  ```bash
  sudo apt autoremove
  ```
- Xóa các file cấu hình còn sót lại (nếu có):
  ```bash
  sudo find /etc -name '*python3.11*' -exec rm -rf {} +
  ```

##### **Bước 3: Xóa các file liên quan**
- Kiểm tra và xóa các file Python 3.11 còn sót trong `/usr/bin`, `/usr/lib`, hoặc `/usr/local`:
  ```bash
  sudo find /usr/bin -name 'python3.11*' -exec rm -f {} +
  sudo find /usr/lib -name 'python3.11*' -exec rm -rf {} +
  sudo find /usr/local -name 'python3.11*' -exec rm -rf {} +
  ```
- **Cảnh báo**: Hãy cẩn thận khi dùng `find` để xóa, kiểm tra kỹ output của `find` trước khi xóa:
  ```bash
  sudo find /usr/bin -name 'python3.11*'
  sudo find /usr/lib -name 'python3.11*'
  ```
---

### load_dotenv()


**Trong local dev, `os.getenv(...)` sẽ không đọc được file `.env` trừ khi bạn dùng `load_dotenv()` hoặc export biến môi trường thủ công.**

* `os.getenv(...)` **chỉ đọc biến môi trường từ hệ thống OS hoặc Docker, không đọc trực tiếp từ `.env` file**.
* Nếu bạn không dùng `load_dotenv()` thì file `.env` sẽ bị **bỏ qua** hoàn toàn.

---

### .env trong docker

Khi bạn chạy Docker với:

```bash
docker run --env-file .env myapp
```

Hoặc:

```bash
docker run -e DB=mydb -e DB_USER=admin myapp
```

Hoặc trong compose:
```yaml
    env_file:
      - .env
```


Docker sẽ:

> **Inject các biến môi trường đó trực tiếp vào môi trường hệ điều hành trong container.**

--- 

### 🧠 Sự khác nhau giữa:

#### 1. ✅ `COPY gender-weights/ gender-weights/`

* **Ý nghĩa:** Copy nội dung trong thư mục `gender-weights/` (trên máy host) vào thư mục `/app/gender-weights/` trong image.
* **Kết quả:**
  Nếu bạn có:

  ```
  gender-weights/
    ├── file1.txt
    └── file2.txt
  ```

  Thì trong image sẽ có:

  ```
  /app/gender-weights/file1.txt
  /app/gender-weights/file2.txt
  ```

---

#### 2. ✅ `COPY gender-weights/ .`

* **Ý nghĩa:** Copy nội dung trong thư mục `gender-weights/` (trên máy host) **vào thư mục hiện tại** (`WORKDIR`, ví dụ `/app`) trong image.
* **Kết quả:**
  Các file/folder bên trong `gender-weights/` sẽ nằm **trực tiếp trong `/app`**, không có thư mục `gender-weights`.

  Ví dụ:

  ```
  /app/file1.txt
  /app/file2.txt
  ```

---

###🧾 Tóm tắt sự khác biệt:

| Lệnh COPY                              | Trong image sẽ có gì                                                           |
| -------------------------------------- | ------------------------------------------------------------------------------ |
| `COPY gender-weights/ gender-weights/` | `/app/gender-weights/...`                                                      |
| `COPY gender-weights/ .`               | `/app/...` (các file bên trong `gender-weights` được rải trực tiếp vào `/app`) |


---
### 1 số commands
#### create venv
```shell
python3.11 -m venv myenv
source myenv/bin/activate
pip3.11 freeze > requirement.txt
pip3.11 install -r requirements.txt
python main.py
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"] # --reload	Tự động reload khi thay đổi code (chỉ nên dùng khi dev)
```

#### docker commands
```shell
docker exec -it myapp_container /bin/bash
docker cp path/to/local/file <container_name_or_id>:/path/in/container
docker cp ./my-folder myapp_container:/app/
docker container prune # delete all stopped containers
docker rm $(docker ps -a -f status=exited -q)
docker builder prune # delete all build cache 

```

#### curl
```shell
curl -X POST http://localhost:8000/recommendations \
  -H "Content-Type: application/json" \
  -d '{"userId": "user123", "title": "Software Engineer"}'

```
