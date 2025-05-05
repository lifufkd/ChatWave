<!-- Language switch -->
[🇷🇺 Русский](README/readme.ru.md) | [🇬🇧 English](README.md)

<p align="center">
  <img src="assets/logo-dark.svg" alt="ChatWave logo" width="200"/>
</p>

# 💬 ChatWave

**ChatWave** is a modern, simple, and secure REST API for a self-hosted messenger — open source and licensed under **GPLv3**.  
This repository contains only the **backend**, built with **Python 3.11** and **FastAPI**.

## ✨ Features

- 🏠 Self-hosted backend
- 🔐 Secure auth (JWT Bearer HS256), TLSv3, password hashing
- 👤 Account & profile management
- 💬 Personal & group chats
- 🎙️ Media messages (voice, images, files)
- ⚡ Real-time message updates via WebSocket
- 🧹 Permanent deletion of messages

## 🛣️ Roadmap

- 🌐 Web frontend (already available, but still in active development: [chatwave-web](https://github.com/lifufkd/chatwave-web))
- 🎥 Video messages (real-time)
- 📞 Audio & video calls (1-on-1 and group)

## 🚀 Getting Started

### 🧑‍💻 1. Run from source

```bash
git clone https://github.com/lifufkd/ChatWave
pip install -r requirements.txt
cd ./src
nano .env (Fill in the env file according to the section "ENV configuration")
uvicorn main:app --host 0.0.0.0 --port 8000
```

### 🐳 2. Run with Docker

### 1. Standalone 
```bash
docker run \
--name chatwave \
-d \
-p 8080:8000 \
-v <PATH_TO_MEDIA_FOLDER>:/app/data \
--env-file <PATH-TO-ENV> \
ghcr.io/lifufkd/chatwave:latest
```
### 2. All in one

#### 1. HTTP (no ssl)
```bash
git clone https://github.com/lifufkd/ChatWave
cd ChatWave
docker-compose up -d
```


#### 2. HTTPS (ssl)
```bash
git clone https://github.com/lifufkd/ChatWave
cd ChatWave
docker-compose -f docker-compose.nginx.yml up -d
```

## ⚙️ ENV Configuration

```
# Required
MEDIA_FOLDER=<PATH> # Must be same in run command (-v chatwave_appdata:/app/data)

# Required for "Standalone" installation method
DB_HOST=<DOMAIN-OR-IP>
DB_USER=<USER>
DB_PASSWORD=<PASSWORD>
REDIS_HOST=<DOMAIN-OR-IP>

# Required for HTTPS (ssl)
SSL_CERT_PATH=/cert/cert.pem
SSL_CERT_KEY=/cert/cert.key
 
# Optionaly
DB_DATABASE=<DATABASE-NAME>
DB_PORT=<PORT>
DB_SCHEMA=chatwave
REDIS_PORT=<PORT>
REDIS_DATABASE=0
REDIS_USER=<USER>
REDIS_PASSWORD=<PASSWORD>
JWT_SECRET_KEY=09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7 # 256 bit random string
JWT_ACCESS_TOKEN_EXPIRES=1209600 # Token expire time in seconds
JWT_ALGORITHM=HS256
CHUNK_SIZE=16 # Decimal value in MB for streaming video
MAX_UPLOAD_IMAGE_SIZE=30 # Decimal value in MB
MAX_UPLOAD_VIDEO_SIZE=8192 # Decimal value in MB
MAX_UPLOAD_AUDIO_SIZE=512 # Decimal value in MB
MAX_UPLOAD_FILE_SIZE=16384 # Decimal value in MB
MAX_ITEMS_PER_REQUEST=100 # Decimal value
```

## ❤️ Contributing

You can help by testing, opening issues, or contributing code.
Also check out our frontend repo [ChatWave Web](https://github.com/lifufkd/chatwave-web)

## 📜 License
Distributed under the GPLv3 License. See [LICENSE](https://github.com/lifufkd/ChatWave/blob/main/LICENSE) for more information.
