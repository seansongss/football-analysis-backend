import os, tempfile, subprocess
from fastapi import FastAPI, HTTPException, UploadFile, File
import boto3

app = FastAPI()
s3 = boto3.client("s3")
BUCKET = os.getenv("S3_BUCKET")

@app.post("/process/")
async def process_video(file: UploadFile = File(...)):
    # 1) Save upload locally
    tmp_in = tempfile.mktemp(suffix=".mp4")
    with open(tmp_in, "wb") as f:
        f.write(await file.read())
        
    print(f"Input video saved to {tmp_in}")

    # 2) Run your pipeline (assumes pipeline.py in root)
    tmp_out = tempfile.mktemp(suffix=".mp4")
    ret = subprocess.run(
        ["python", "pipeline.py", "--input", tmp_in, "--output", tmp_out],
        capture_output=True,
    )
    if ret.returncode != 0:
        raise HTTPException(500, detail=ret.stderr.decode())

    # 3) Upload result to S3
    key_out = f"output_videos/{file.filename}"
    s3.upload_file(tmp_out, BUCKET, key_out)
    url = s3.generate_presigned_url(
        "get_object", Params={"Bucket": BUCKET, "Key": key_out}, ExpiresIn=3600
    )
    return {"videoUrl": url}
