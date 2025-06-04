# import asyncio
# import requests  # Import inside the function to avoid issues

# async def initial_load():
    
#     url = 'http://localhost:8000/api/initial_load'
#     response = requests.get(url)

#     if response.status_code == 200:
#         data = response.json()
#         print("initial", response)
#         # Process the data here
#     else:
#         print("Error:", response.status_code)

# # async def get_filtered():
# #     await asyncio.sleep(0.1)

# #     url = 'http://localhost:8011/api/get_filtered_data'
# #     response = requests.get(url)

# #     if response.status_code == 200:
# #         data = response.json()
# #         print("get_filtered_data", response)
# #         # Process the data here
# #     else:
# #         print("Error:", response.status_code)




# async def main():
#     while True:
#         await initial_load()
#         # await get_filtered()
#         await asyncio.sleep(5)  # Adjust the delay as needed

# if __name__ == "__main__":
#     asyncio.run(main())

import aiohttp
import asyncio
import subprocess
from apscheduler.schedulers.asyncio import AsyncIOScheduler

url = 'http://localhost:8000'

# async def initial_load():
#     try:
#         async with aiohttp.ClientSession() as session:
#             async with session.get(f'{url}/api/initial_load') as response:
#                 if response.status == 200:
#                     data = await response.json()
#                     # print("Initial Load Response:", data)
#                     await cloud_storage_upload()
#                 else:
#                     print("Error PLEASE RUN :", response.status)
#     except aiohttp.ClientConnectorError as e:
#         print(f"Connection error: {e}")
#     except Exception as e:
#         print(f"An error occurred: {e}")

# async def cloud_storage_upload():
#     script_path = r"..\AlgoforceDashboard\storage\cloud_storage.py"
#     # print(f"Running script: {script_path}")
#     loop = asyncio.get_event_loop()
#     result = await loop.run_in_executor(None, lambda: subprocess.run(['python', script_path], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True))
#     if result.returncode == 0:
#         print("Script ran successfully.")
#         # print(result.stdout)
#     else:
#         print("Script encountered an error.")
#         # print(result.stderr)

def sql_live_data_scheduler():
    script_path = r"C:\Users\User\Documents\jonathan-dashboard\PINAKA_LATEST\financialDashboard\afdashboard\sql_live_data_3.py"
    # print(f"Running script: {script_path}")
    result = subprocess.run(['python', script_path], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if result.returncode == 0:
        print("Script ran successfully.")
        print(result.stdout)
    else:
        print("Script encountered an error.")
        print(result.stderr)
def binance_data_api_scheduler():
    script_path = r"C:\Users\User\Documents\jonathan-dashboard\PINAKA_LATEST\financialDashboard\afdashboard\binance_data.py"
    # print(f"Running script: {script_path}")
    result = subprocess.run(['python', script_path], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if result.returncode == 0:
        print("Script ran successfully.")
        print(result.stdout)
    else:
        print("Script encountered an error.")
        print(result.stderr)



async def main():
    scheduler = AsyncIOScheduler()
    # scheduler.add_job(initial_load, 'interval', seconds=15)
    scheduler.add_job(binance_data_api_scheduler, 'cron', hour='4,8,12,16,20,0', minute=6)
    await asyncio.sleep(1)
    scheduler.add_job(sql_live_data_scheduler, 'cron', hour='4,8,12,16,20,0', minute=6)


    scheduler.start()

    try:
        while True:
            await asyncio.sleep(1)
    except (KeyboardInterrupt, SystemExit):
        scheduler.shutdown()

if __name__ == "__main__":
    asyncio.run(main())
