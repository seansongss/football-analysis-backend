# app/main.py
from fastapi import FastAPI, HTTPException, UploadFile, File
import os, tempfile
import boto3
from settings import settings
from pipeline import run_pipeline
import anyio

app = FastAPI()
s3 = boto3.client("s3")
BUCKET = settings.S3_BUCKET

@app.get("/debug-bucket")
def debug_bucket():
    return {"BUCKET": BUCKET}

@app.get("/buckets/")
async def list_buckets():
    names = [b["Name"] for b in s3.list_buckets()["Buckets"]]
    return {"buckets": names}

@app.post("/process/")
async def process_video(file: UploadFile = File(...)):
    if not file:
        return {"outputUrl": "testing succeed"}
    # 1) Save upload to a temp file
    suffix = os.path.splitext(file.filename)[1]
    in_tmp = tempfile.mktemp(suffix=suffix)
    with open(in_tmp, "wb") as f:
        f.write(await file.read())

    # 2) Run your pipeline
    out_tmp = tempfile.mktemp(suffix=f"_proc.mp4")
    try:
        await anyio.to_thread.run_sync(run_pipeline, in_tmp, out_tmp)
    except Exception as e:
        raise HTTPException(500, detail=str(e))

    # 3) Upload only the processed video
    out_key = f"output_videos/{os.path.basename(out_tmp)}"
    s3.upload_file(out_tmp, BUCKET, out_key)

    # 4) Return a presigned GET URL
    url = s3.generate_presigned_url(
        "get_object",
        Params={"Bucket": BUCKET, "Key": out_key},
        ExpiresIn=3600,
    )
    return {"outputUrl": url}
