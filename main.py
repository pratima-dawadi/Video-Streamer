import os

from dotenv import load_dotenv
from fastapi import FastAPI, UploadFile, File, Request, HTTPException, status
from fastapi.responses import StreamingResponse
from utils import upload_to_s3, stream_from_s3, s3

app = FastAPI(
    title="Video Streaming API",
    description="An API to upload and stream video files",
)

load_dotenv()


@app.post("/video")
async def upload_video(request: Request, file: UploadFile = File(...)):
    content = await file.read()

    upload_to_s3(content, file.filename)

    base_url = str(request.base_url).rstrip("/")
    video_url = f"{base_url}/stream/{file.filename}"

    return {
        "filename": file.filename,
        "video_url": video_url,
    }


@app.get("/stream/{filename}")
async def stream_video(filename: str, request: Request):
    range_header = request.headers.get("range")

    if not range_header:
        raise HTTPException(
            status_code=status.HTTP_416_REQUESTED_RANGE_NOT_SATISFIABLE,
            detail="Range header required",
        )

    try:
        range_value = range_header.strip().split("=")[-1]
        byte1, byte2 = range_value.split("-")
        byte1 = int(byte1)
        byte2 = int(byte2) if byte2 else byte1 + 1024 * 1024

    except Exception:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid Range header"
        )

    byte_range = f"bytes={byte1}-{byte2}"

    try:
        s3_response = stream_from_s3(filename, byte_range)
        BUCKET_NAME = os.getenv("BUCKET_NAME")
        total_size = s3.head_object(Bucket=BUCKET_NAME, Key=filename)["ContentLength"]

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

    headers = {
        "Content-Range": f"bytes {byte1}-{byte2}/{total_size}",
        "Accept-Ranges": "bytes",
        "Content-Length": str(byte2 - byte1 + 1),
        "Content-Type": "video/mp4",
    }

    print(f"Streaming {filename} with range {byte_range}")

    return StreamingResponse(
        s3_response["Body"],
        status_code=status.HTTP_206_PARTIAL_CONTENT,
        headers=headers,
    )
