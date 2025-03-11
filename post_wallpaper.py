import requests
import json
from datetime import datetime
import os

# 从环境变量获取API Key
API_KEY = os.environ.get("MISSKEY_API_KEY")
MISSKEY_INSTANCE = "https://zhihupaw.com"

def get_bing_wallpaper_info():
    try:
        url = "https://www.bing.com/HPImageArchive.aspx?format=js&idx=0&n=1&mkt=en-US"
        response = requests.get(url)
        data = response.json()
        
        image_base = data["images"][0]["urlbase"]
        image_url = f"https://www.bing.com{image_base}_UHD.jpg"
        copyright = data["images"][0]["copyright"]
        location = copyright.split("(")[-1].rstrip(")")
        
        return image_url, location, copyright
    except Exception as e:
        print(f"获取壁纸信息失败: {e}")
        return None, None, None

def download_image(image_url):
    try:
        response = requests.get(image_url)
        if response.status_code == 200:
            filename = "bing_wallpaper.jpg"
            with open(filename, "wb") as f:
                f.write(response.content)
            return filename
        else:
            print(f"下载图片失败: {response.status_code}")
            return None
    except Exception as e:
        print(f"下载图片时出错: {e}")
        return None

def upload_to_misskey_drive(filename):
    try:
        endpoint = f"{MISSKEY_INSTANCE}/api/drive/files/create"
        
        with open(filename, "rb") as f:
            files = {
                "file": (filename, f, "image/jpeg"),
                "i": (None, API_KEY)
            }
            response = requests.post(endpoint, files=files)
            
        if response.status_code == 200:
            file_id = response.json()["id"]
            return file_id
        else:
            print(f"上传文件失败: {response.text}")
            return None
    except Exception as e:
        print(f"上传文件时出错: {e}")
        return None

def post_to_misskey(location, copyright, file_id):
    text = f"今日必应壁纸 ({datetime.now().strftime('%Y-%m-%d')}):\n"
    text += f"地点: {copyright}"

    endpoint = f"{MISSKEY_INSTANCE}/api/notes/create"
    
    payload = {
        "i": API_KEY,
        "text": text,
        "fileIds": [file_id],
        "visibility": "public"
    }
    
    try:
        response = requests.post(endpoint, json=payload)
        if response.status_code == 200:
            print("帖子发布成功!")
        else:
            print(f"发布失败: {response.text}")
    except Exception as e:
        print(f"发布帖子时出错: {e}")

def main():
    if not API_KEY:
        print("错误：未设置MISSKEY_API_KEY环境变量")
        return
        
    image_url, location, copyright = get_bing_wallpaper_info()
    
    if image_url and location:
        filename = download_image(image_url)
        if filename:
            file_id = upload_to_misskey_drive(filename)
            if file_id:
                post_to_misskey(location, copyright, file_id)
                os.remove(filename)
            else:
                print("文件上传失败")
        else:
            print("图片下载失败")
    else:
        print("无法获取壁纸信息")

if __name__ == "__main__":
    main()
