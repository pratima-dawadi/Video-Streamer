# Video Streaming API

A FastAPI application that allows users to upload video files and stream them with support for byte-range requests (seekable video playback). Files are stored in an AWS S3 bucket.

---
## Setup 

### 1. Clone the repository

```bash
git clone https://github.com/pratima-dawadi/Video-Streamer.git
cd Video-Streamer
```
### 2. Create and activate virtual environment

```bash
python3 -m venv .venv
source .venv/bin/activate
```
### 3. Install dependencies

```bash
pip install -r requirements.txt
```
### 4.Configure `.env` file
Create a `.env` file in the project root similar to the provided `sample-env`.

### 5.Run the application
```bash
uvicorn main:app --reload
```

Access api documentation on [localhost:8000/docs/](http://localhost:8000/docs)
