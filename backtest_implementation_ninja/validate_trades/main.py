# from typing import List, Union
# from datetime import datetime
# import os
# from django.conf import settings
# from afdashboard.views import *
# from pydantic import BaseModel, ValidationError, ConfigDict
# from cachetools import cached, LRUCache
# import asyncio
# from django.http import JsonResponse
# from sqlalchemy.orm import Session
# from backtest_implementation_ninja.database.database_backtest import SessionLocal, engine, Base
# from backtest_implementation_ninja.database.models import *
# from .main_backtest2 import main

# # Initialize SQLAlchemy tables
# try:
#     print("Creating tables...")
#     Base.metadata.create_all(bind=engine)
#     print("Tables created successfully!")
# except Exception as e:
#     print(f"Error creating tables: {e}")

# # Define the static directory path
# static_dir = r"..\financialDashboard\backtest_implementation_ninja\validate_trades\models\ATOMUSDT\ATOMUSDT_P0501\ATOMUSDT_115"

# # Define the Pydantic model
# class Item(BaseModel):
#     symbol: str
#     ver: Union[str, None] = None
#     interval: str
#     model_config = ConfigDict(arbitrary_types_allowed=True)

# # Setup cache
# cache = LRUCache(maxsize=1000)

# # Dependency to get the DB session
# def get_db():
#     db = SessionLocal()
#     try:
#         yield db
#     finally:
#         db.close()

# # API Endpoints without using Router
# @cached(cache)
# @api.post("/items_post")
# async def create_item(
#     request,
#     symbol: str = Form('ATOMUSDT'), 
#     ver: str = Form('P0501'),
#     interval: str = Form('4h'),

    
#     trade_start: str = Form('2024-06-01'),  # Updated format
#     trade_end: str = Form(datetime.now().date()),
#     # db: Session = get_db
# ):

#     # Convert strings to date objects and validate
#     try:
#         datetoday = datetime.now().strftime('%Y-%m-%d %H:%M:%S')




#         trade_start_date = datetime.strptime(trade_start, '%Y-%m-%d').date()
#         trade_end_date = datetime.strptime(trade_end, '%Y-%m-%d').date()

#         if trade_start_date > trade_end_date:
#             return JsonResponse({"error": "trade_start cannot be after trade_end"}, status=400)

#         if trade_start_date > datetime.now().date():
#             return JsonResponse({"error": "trade_start cannot be in the future"}, status=400)

#     except ValueError as e:
#         return JsonResponse({"error": f"Invalid date format: {str(e)}"}, status=400)

#     # Manually get the session
#     db = next(get_db())
#     try:
#         # If validation passes, proceed
#         # new_item = backtest_data(symbol=symbol, ver=ver, interval=interval, trade_start=trade_start, trade_end=trade_end, datetoday=datetoday)
#         new_item = backtest_data(symbol=symbol, ver=ver, interval=interval, trade_start=trade_start, trade_end=trade_end, datetoday=datetoday)


#         json_data = {
#             'symbol': new_item.symbol,
#             'ver': new_item.ver,
#             'interval': new_item.interval,
#             'trade_start': new_item.trade_start,
#             'trade_end': new_item.trade_end,
#             'datetoday': new_item.datetoday
#         }
#         db.add(new_item)
#         db.commit()
#         db.refresh(new_item)
#         cache['items_post'] = json_data
#         return JsonResponse({"data": json_data}, status=200)
#     finally:
#         db.close()
# @api.get("/item_get")
# async def get_item(request):
#     # Manually get the session
#     db: Session = next(get_db())
#     try:
#         # Retrieve cached data
#         json_data = cache.get('items_post')
#         if not json_data:
#             return JsonResponse({"error": "No data found"}, status=400)

#         # Extract data
#         data_get = {
#             'symbol': json_data.get('symbol'),
#             'ver': json_data.get('ver'),
#             'interval': json_data.get('interval'),
#             'trade_start': json_data.get('trade_start'),
#             'trade_end': json_data.get('trade_end')
#         }

#         try:
#             # Call the main function that generates PNG and CSV files
#             generated_files = await asyncio.to_thread(
#                 main,
#                 data_get['symbol'],
#                 data_get['ver'],
#                 data_get['interval'],
#                 data_get['trade_start'],
#                 data_get['trade_end']
#             )

#             # Example: Assuming generated_files returns a dictionary with file paths
#             generated_files = {
#             "data": {
#                 "symbol": "ATOMUSDT",
#                 "ver": "P0501",
#                 "interval": "4h",
#                 "trade_start": "2024-06-01",
#                 "trade_end": "2024-09-03"
#             },
#             "generated_files": [
#                 "..\\static\\backtest_outputs\\ATOMUSDT_decision_boundary.png",
#                 "..\\static\\backtest_outputs\\ATOMUSDT_svm_backtest1.csv",
#                 "..\\static\\backtest_outputs\\ATOMUSDT_svm_backtest.csv",
#                 "..\\static\\backtest_outputs/tradesheet_ATOMUSDT.csv",
#                 "..\\static\\backtest_outputs/reports.png"
#             ]
#             }
#             decision_boundary = generated_files.get('generated_files')
#             # csv_path = generated_files.get('csv_file')

#             # Save the paths into the database
#             new_data = backtest_data(
#                 symbol=data_get['symbol'],
#                 ver=data_get['ver'],
#                 interval=data_get['interval'],
#                 trade_start=data_get['trade_start'],
#                 trade_end=data_get['trade_end'],
#                 decision_boundary=decision_boundary['decision_boundary']
#                 # csv_file=csv_path['csv_file']
#             )
#             db.add(new_data)
#             db.commit()

#             # Return the saved data and generated file paths
#             return JsonResponse({"data": data_get, "generated_files": generated_files}, status=200)
#         except Exception as e:
#             return JsonResponse({"error": "No database found or Network Connection Error!", "details": str(e)}, status=500)
#     finally:
#         db.close()