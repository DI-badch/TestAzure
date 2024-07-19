import os
from fastapi import FastAPI, BackgroundTasks
from datetime import datetime, timezone
import time
from azure.storage.blob import BlobServiceClient
from dotenv import load_dotenv

load_dotenv()
app = FastAPI()

AZURE_STORAGE_CONNECTION_STRING = os.environ["AZURE_STORAGE_CONNECTION_STRING"]
# Thay bằng chuỗi kết nối của storage account của bạn
CONTAINER_NAME = "testcontainer"

# Khởi tạo BlobServiceClient
blob_service_client = BlobServiceClient.from_connection_string(
    AZURE_STORAGE_CONNECTION_STRING
)


def background_task():
    # Tạo tên tệp duy nhất dựa trên ngày và giờ hiện tại
    filename = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ.txt")
    blob_client = blob_service_client.get_blob_client(
        container=CONTAINER_NAME, blob=filename
    )

    # Tạo tệp và ghi dòng đầu tiên
    content = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ\n")
    blob_client.upload_blob(content, overwrite=True)

    # Lặp lại 29 lần (tổng cộng 30 lần bao gồm lần ghi ban đầu)
    for _ in range(29):
        time.sleep(10)  # Đợi 10 giây
        content += datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ\n")
        blob_client.upload_blob(content, overwrite=True)

    # Ghi thông báo dừng
    content += "Stop Task"
    blob_client.upload_blob(content, overwrite=True)


@app.get("/message")
async def root(background_tasks: BackgroundTasks):
    background_tasks.add_task(background_task)
    return "Hello World!"
