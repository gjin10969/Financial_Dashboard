import asyncio
from telethon import TelegramClient
import json
import os
import base64
from datetime import datetime
from django.http import JsonResponse
from afdashboard.views import *
from filelock import FileLock


API_ID = '26178962'
API_HASH = 'e137833889cdde3906decd0b915a92db'
PHONE_NUMBER = '+639452132785'
GROUP_USERNAME_1 = 'CoingraphNews'
GROUP_USERNAME = 'chain_alerts'

IMAGE_SAVE_PATH = 'images'
JSON_SAVE_PATH = r'C:\Users\User\Documents\financialDashboard_AUG\financialDashboard\afdashboard\static\news_output\accounts_binance.json'
JSON_SAVE_PATH_1 = r'C:\Users\User\Documents\financialDashboard_AUG\financialDashboard\afdashboard\static\news_output\coingraphnews.json'

async def start_client():
    client = TelegramClient('session_name', API_ID, API_HASH)
    await client.start(PHONE_NUMBER)
    return client

@api.get('/get_chain_alert_news')
def chain_alert_news(request):
    result = asyncio.run(handle_chain_alert_news())
    return JsonResponse(result)

async def handle_chain_alert_news():
    try:
        client = await start_client()
        group = await client.get_entity(GROUP_USERNAME)
        messages = await client.get_messages(group, limit=1)

        latest_message = messages[0].to_dict()

        if 'date' in latest_message:
            latest_message['date'] = latest_message['date'].isoformat()
        if 'edit_date' in latest_message and latest_message['edit_date']:
            latest_message['edit_date'] = latest_message['edit_date'].isoformat()

        if messages[0].media:
            if not os.path.exists(IMAGE_SAVE_PATH):
                os.makedirs(IMAGE_SAVE_PATH)

            file_name = await client.download_media(messages[0].media)
            file_path = os.path.join(IMAGE_SAVE_PATH, file_name)
            os.rename(file_name, file_path)
            print(f'Image saved to: {file_path}')

            with open(file_path, 'rb') as img_file:
                img_base64 = base64.b64encode(img_file.read()).decode('utf-8')
            latest_message['image_base64'] = img_base64

        def convert_non_serializable(obj):
            if isinstance(obj, dict):
                for key, value in obj.items():
                    if isinstance(value, bytes):
                        obj[key] = base64.b64encode(value).decode('utf-8')
                    elif isinstance(value, datetime):
                        obj[key] = value.isoformat()
                    elif isinstance(value, dict) or isinstance(value, list):
                        convert_non_serializable(value)
            elif isinstance(obj, list):
                for i in range(len(obj)):
                    if isinstance(obj[i], bytes):
                        obj[i] = base64.b64encode(obj[i]).decode('utf-8')
                    elif isinstance(obj[i], datetime):
                        obj[i] = obj[i].isoformat()
                    elif isinstance(obj[i], dict) or isinstance(obj[i], list):
                        convert_non_serializable(obj[i])

        convert_non_serializable(latest_message)

        with open(JSON_SAVE_PATH, 'w', encoding='utf-8') as f:
            json.dump(latest_message, f, indent=4, ensure_ascii=False)

        return {"status": "success", "message": "Data saved", "data": latest_message}

    except Exception as e:
        print(f"Error: {str(e)}")
        return {"status": "error", "message": str(e)}

@api.get('/get_coingraph_news')
def coingraphnews(request):
    result = asyncio.run(handle_coingraphnews())
    return JsonResponse(result)

async def handle_coingraphnews():
    try:
        client = await start_client()
        group = await client.get_entity(GROUP_USERNAME_1)
        messages = await client.get_messages(group, limit=1)

        latest_message = messages[0].to_dict()

        if 'date' in latest_message:
            latest_message['date'] = latest_message['date'].isoformat()
        if 'edit_date' in latest_message and latest_message['edit_date']:
            latest_message['edit_date'] = latest_message['edit_date'].isoformat()

        if messages[0].media:
            if not os.path.exists(IMAGE_SAVE_PATH):
                os.makedirs(IMAGE_SAVE_PATH)

            file_name = await client.download_media(messages[0].media)
            file_path = os.path.join(IMAGE_SAVE_PATH, file_name)
            os.rename(file_name, file_path)
            print(f'Image saved to: {file_path}')

            with open(file_path, 'rb') as img_file:
                img_base64 = base64.b64encode(img_file.read()).decode('utf-8')
            latest_message['image_base64'] = img_base64

        def convert_non_serializable(obj):
            if isinstance(obj, dict):
                for key, value in obj.items():
                    if isinstance(value, bytes):
                        obj[key] = base64.b64encode(value).decode('utf-8')
                    elif isinstance(value, datetime):
                        obj[key] = value.isoformat()
                    elif isinstance(value, dict) or isinstance(value, list):
                        convert_non_serializable(value)
            elif isinstance(obj, list):
                for i in range(len(obj)):
                    if isinstance(obj[i], bytes):
                        obj[i] = base64.b64encode(obj[i]).decode('utf-8')
                    elif isinstance(obj[i], datetime):
                        obj[i] = obj[i].isoformat()
                    elif isinstance(obj[i], dict) or isinstance(obj[i], list):
                        convert_non_serializable(obj[i])

        convert_non_serializable(latest_message)

        with open(JSON_SAVE_PATH_1, 'w', encoding='utf-8') as f:
            json.dump(latest_message, f, indent=4, ensure_ascii=False)

        return {"status": "success", "message": "Data saved", "data": latest_message}

    except Exception as e:
        print(f"Error: {str(e)}")
        return {"status": "error", "message": str(e)}