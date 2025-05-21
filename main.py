# app/main.py
from fastapi import FastAPI, HTTPException, UploadFile, File
import os, tempfile, subprocess
import boto3
from settings import settings

app = FastAPI()
s3 = boto3.client("s3")
BUCKET = settings.S3_BUCKET

@app.post("/testing/")
async def testing():
    print("bucket name:" + BUCKET)
    return {"outputUrl": BUCKET}
    

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
    out_tmp = tempfile.mktemp(suffix=f"_proc{suffix}")
    cmd = ["python", "pipeline.py", "--input", in_tmp, "--output", out_tmp]
    proc = subprocess.run(cmd, capture_output=True)
    if proc.returncode != 0:
        raise HTTPException(500, detail=proc.stderr.decode())

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
