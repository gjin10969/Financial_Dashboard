
from django import template
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse, FileResponse
from django.template import Context, loader
from django.urls import reverse
from django.shortcuts import render
from django.views.generic import View
from .models import *
import logging
import pandas as pd
from django.urls import reverse
from django.contrib.staticfiles import finders
import json
import requests
from datetime import datetime, timedelta, timezone
import datetime
import asyncio
from django.urls import path
import pytz
from ninja import NinjaAPI, Form, Query, UploadedFile, File
from pydantic import BaseModel
from .computation_data_app.computation_data import *
# from .sql_data import *
# from cachetools import cached, TTLCache, TLRUCache, LRUCache
# import diskcache
# from .models import ChartData
from .computation_data_app.cache_manager import *
# from .binance_data import *
from django.db.models import Q
from .models import ChartData
from django.contrib import admin
import orjson
from django.template.loader import render_to_string
from reportlab.lib.pagesizes import letter, landscape
from reportlab.pdfgen import canvas
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
from reportlab.lib import colors
import io
from ninja.responses import Response
from sqlalchemy.orm import Session
from backtest_implementation_ninja.database.models import backtest_data
from backtest_implementation_ninja.database.database_backtest import SessionLocal
# from .computation_data_app.cointegration_computation_test import *
# from ninja import Router

import tracemalloc
tracemalloc.start()

api = NinjaAPI()

@api.get("/index")
async def index(request):
    # data = Trades.objects.all()
    context = {'segment': 'index'} 

    html_template = loader.get_template('home/index.html')
    return HttpResponse(html_template.render(context, request))
@api.get("/dashboard")
async def dashboard(request):
    # data = Trades.objects.all()
    context = {'segment': 'dashboard'} 

    html_template = loader.get_template('home/dashboard.html')
    return HttpResponse(html_template.render(context, request))



@api.get("/pages")
async def pages(request):

    context = {}
    load_template = request.path.split('/')[-1]

    if load_template == 'admin':
        return HttpResponseRedirect(reverse('admin:index'))

    if load_template == 'favicon.ico':
        return HttpResponse(status=204)  

    context['segment'] = load_template

    if load_template == 'index':
        template_path = 'home/index.html'
    elif load_template == 'backtest':
        template_path = 'home/backtest.html'
    elif load_template == 'charts':
        template_path = 'home/charts.html'
    elif load_template == 'cointegration-dashboard':
        template_path = 'home/cointegration-dashboard.html'
    elif load_template == 'transaction_logs':
        template_path = 'home/transaction_logs.html'  
    elif load_template.endswith('.js'):
        # Handle .js files as static files
        static_file_path = finders.find('scripts/' + load_template)
        if static_file_path:
            return FileResponse(open(static_file_path, 'rb'), content_type='application/javascript')
        else:
            return HttpResponse(status=404)
    else:
        # Assume other templates are in the scripts folder within static
        template_path = 'home/scripts/' + load_template + '.html'
    return render(request, template_path, context)


async def bar_chart(request):
    return JsonResponse({'data': 'hello world'})

#########################ADDED###################ADDED###################ADDED###################ADDED###############
mirrorx_models = [mirrorx1, mirrorx2, mirrorx3, mirrorx4, mirrorx5, mirrorxfund]
mirrorx_accounts = None
# ph_timezone = pytz.timezone('Asia/Manila')
# # Get the current date in the specified time zone
# presentdate_ph = datetime.now(ph_timezone).date()
# # Calculate the date 7 days ago in the specified time zone
# last_7_days_ph = presentdate_ph - timedelta(weeks=40)
# # Calculate the end date (excluding today)
# end_date_ph = presentdate_ph
# # Convert the dates to strings in the desired format
# start_date_global = (last_7_days_ph + timedelta(days=1)).strftime('%Y-%m-%d')  # Adding one day to exclude it
# end_date_global = end_date_ph.strftime('%Y-%m-%d')
# print(start_date_global)


ph_timezone = pytz.timezone('Asia/Manila')

# Set the specific date (2024-12-12) instead of using the current date
presentdate_ph = datetime(2024, 12, 12).date()

# Calculate the date 7 days ago in the specified time zone
last_7_days_ph = presentdate_ph - timedelta(weeks=100)

# Calculate the end date (excluding today)
end_date_ph = presentdate_ph

# Convert the dates to strings in the desired format
start_date_global = (last_7_days_ph + timedelta(days=1)).strftime('%Y-%m-%d')  # Adding one day to exclude it
end_date_global = end_date_ph.strftime('%Y-%m-%d')

# presentdate = datetime.now()

# # Get the first day of the current month
# first_day_of_month = presentdate.replace(day=1)

# Format the start and end dates as 'YYYY-MM-DD'
# start_date_global = first_day_of_month.strftime('%Y-%m-%d')
# end_date_global = presentdate.strftime('%Y-%m-%d')
# import csv
#To get the data from from sql and store to cached! this is need to load for initial :)

# def csv_to_save(data):
#     # Define the filename with the current timestamp to avoid overwriting
#     filename = f"mirrorx_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    
#     # Define the header based on the data keys
#     if data:
#         header = data[0].keys()
        
#         # Write the data to a CSV file
#         with open(filename, mode='w', newline='') as file:
#             writer = csv.DictWriter(file, fieldnames=header)
#             writer.writeheader()
#             writer.writerows(data)
    
#     print(f"Data saved to {filename}")
@cached(cache)
@api.get("/get_data")
async def get_data(request):
    try:
        await asyncio.sleep(0.01)
        # cache.clear()
        result_data = []
        
        async def fetch_data_from_model(mirrorx_model):
            return await asyncio.to_thread(list, mirrorx_model.objects.all().values())
        
        # Fetch data from all mirrorx models concurrently
        tasks = [asyncio.create_task(fetch_data_from_model(model)) for model in mirrorx_models]
        mirrorx_data_list = await asyncio.gather(*tasks)
        
        # Process the fetched data
        for mirrorx_model, mirrorx_data in zip(mirrorx_models, mirrorx_data_list):
            sorted_mirrorx_data = sorted(mirrorx_data, key=lambda x: x["date"])  # Sort by date or any other key as required
            for entry in sorted_mirrorx_data:
                entry_with_account = {
                    "mirrorx_account": mirrorx_model.__name__,
                    "date": entry["date"],
                    "symbol": entry["symbol"],
                    "id": entry["id"],
                    "orderId": entry["orderId"],
                    "side": entry["side"],
                    "price": entry["price"],
                    "qty": entry["qty"],
                    "realizedPnl": entry["realizedPnl"],
                    "marginAsset": entry["marginAsset"],
                    "quoteQty": entry["quoteQty"],
                    "commission": entry["commission"],
                    "commissionAsset": entry["commissionAsset"],
                    "time": entry["time"],
                    "positionSide": entry["positionSide"],
                    "buyer": entry["buyer"],
                    "maker": entry["maker"]
                }
                result_data.append(entry_with_account)

        # Set the data in the cache with a specific key
        cache["/api/get_data"] = result_data

        # Save the result data to a CSV file
        # csv_to_save(result_data)
        filename = r'..\AlgoforceDashboard\afdashboard\computation_data_app\historical_klines.csv'
        await asyncio.create_task(fetch_and_save_historical_klines(filename))
        await asyncio.create_task(get_all_data_view(request))
        await asyncio.create_task(get_initial_load(request))
        
        return JsonResponse("Data Loaded Successfully Sheesh!", status=200, safe=False)
    
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500, safe=False)

#to get the data from get_data endpoint and filtered by 7 days.
@api.get("/get_all_data")
async def get_all_data_view(request):
    try:
        # Execute time-consuming tasks concurrently
        cached_data = cache.get("/api/get_data")
        await asyncio.sleep(0.01) # To simulate async work
        global start_date_global, end_date_global
        # print("get_all_data", start_date_global, end_date_global)
        # if "data" not in cached_data:
        #     return {"error": "Data not available in cache or has an invalid format."}, 404
        # data = cached_data["data"]
        start_date = datetime.strptime(start_date_global, "%Y-%m-%d").date()
        end_date = datetime.strptime(end_date_global, "%Y-%m-%d").date()
        # Filter data based on the 'date' field within the specified range
        filtered_data = [
            {
                "mirrorx_account": item.get("mirrorx_account", ""),
                "date": item.get("date", ""),
                "symbol": item.get("symbol", ""),
                "id": item.get("id", ""),
                "orderId": item.get("orderId", ""),
                "side": item.get("side", ""),
                "price": item.get("price", ""),
                "qty": item.get("qty", ""),
                "realizedPnl": item.get("realizedPnl", ""),
                "marginAsset": item.get("marginAsset", ""),
                "quoteQty": item.get("quoteQty", ""),
                "commission": item.get("commission", ""),
                "commissionAsset": item.get("commissionAsset", ""),
                "time": item.get("time", ""),
                "positionSide": item.get("positionSide", ""),
                "buyer": item.get("buyer", ""),
                "maker": item.get("maker", "")
            }
            for item in cached_data
            if start_date <= item["date"].date() <= end_date
        ]
        # Sort the filtered data based on the 'date' field
        sorted_data = sorted(filtered_data, key=lambda item: item.get("date", ""))
        # Update cache with sorted data
        cache["/api/get_all_data"] = sorted_data
        return JsonResponse(sorted_data,safe=False, status=200)
    except Exception as e:
        raise JsonResponse(status_code=500, detail=str(e))

# import itertools
# request_counter = itertools.count()
#for filtering the mirror account


#for datefiltering
# lock = asyncio.Lock()
@api.get("/mirrorxaccount")
async def mirrorxaccount(request):
    # mirror_accounts: str = Form(mirrorx_accounts)):
    # async with lock:
    global mirrorx_accounts
    print(mirrorx_accounts)

from collections import defaultdict
@api.get("/initial_load")
async def get_initial_load(request):
    global start_date_global, end_date_global

    # Ensure global variables are initialized properly
    if not start_date_global or not end_date_global:
        return JsonResponse({"error": "Start and end dates must be initialized."}, status=400)

    print(start_date_global)
    print(end_date_global)

    mirror_accounts = None
    symbols = None

    await asyncio.sleep(0.1)

    cached_data = cache.get("/api/get_all_data")
    combined_data = []  # Initialize combined_data

    try:
        # Use the existing global variables for the date range
        start_date_global = start_date_global
        end_date_global = end_date_global

        # Fetch required data asynchronously
        metrics_data = await asyncio.create_task(all_metrics_json_data(start_date_global, end_date_global))
        cached_data = await asyncio.create_task(fetch_get_data())
        result = await asyncio.create_task(data_computations(
            cached_data, start_date_global, end_date_global, mirror_accounts, calculation_types, symbols
        ))

        if cached_data is None:
            return JsonResponse({"error": "Data not available in cache or invalid cache structure."}, status=404)

        if result is None:
            result = {}  # Ensure result is a dictionary

        start_date_dt = datetime.strptime(start_date_global, "%Y-%m-%d").date()
        end_date_dt = datetime.strptime(end_date_global, "%Y-%m-%d").date()

        # Aggregate data for all mirror accounts and treat it as "all_account"
        mirrorx_all_accounts = ["mirrorx1", "mirrorx2", "mirrorx3", "mirrorx4", "mirrorx5", "mirrorxfund"]

        filtered_data_all_account = [
            {
                "mirrorx_account": item["mirrorx_account"],
                "date": item["date"].date(),  # Convert to date
                "realizedPnl": item["realizedPnl"],
                "symbol": item["symbol"],
            }
            for item in cached_data
            if start_date_dt <= item["date"].date() <= end_date_dt  # Convert to date
            and item["mirrorx_account"] in mirrorx_all_accounts
            and (not symbols or item["symbol"] in symbols)
        ]

        aggregated_data_all_account = defaultdict(lambda: {
            'mirrorx_account': 'mirrorxtotal',
            'date': None,
            'realizedPnl': 0,
            'symbol': None
        })

        for item in filtered_data_all_account:
            key = (item['date'], item['symbol'])
            if aggregated_data_all_account[key]['date'] is None:
                aggregated_data_all_account[key]['date'] = item['date']
                aggregated_data_all_account[key]['symbol'] = item['symbol']
            aggregated_data_all_account[key]['realizedPnl'] += item['realizedPnl']

        # Update combined_data with the aggregated all_account data
        for aggregated_item in aggregated_data_all_account.values():
            # Try to find a matching item in combined_data
            matched_item = next(
                (item for item in combined_data if item['date'] == aggregated_item['date'] and item['symbol'] == aggregated_item['symbol']),
                None
            )
            if matched_item:
                # If found, update its realizedPnl
                matched_item['realizedPnl'] += aggregated_item['realizedPnl']
            else:
                # Otherwise, append the new aggregated item
                combined_data.append(aggregated_item)

        if not combined_data:
            return JsonResponse({"error": "No data available for the specified range or criteria."}, status=400)

        merged_results = sorted(
            combined_data,
            key=lambda x: (x['date'], x['symbol'], x['mirrorx_account'])
        )

        response_data = {
            'total_realized_pnl': float(result.get('fetch_csv_calculate_total_realized_pnl', 0)),
            'trading_days': float(result.get('calculate_trading_days', 0)),
            'winning_days': float(result.get('winning_days', 0)),
            'total_fees': float(result.get('calculate_total_fees', 0)),
            'max_draw': float(result.get('max_draw', 0)),
            'calculate_buy_sell': result.get('calculate_buy_sell', {})
        }

        overall = {k: float(v) for k, v in result.get("overall", {}).items()}
        trades = {k: float(v) for k, v in result.get("trades", {}).items()}
        winrates = {k: float(v) for k, v in result.get("winrate_per_symbol", {}).items()}
        mirror_winrates = {k: float(v) for k, v in result.get("mirror_winrates", {}).items()}
        profits_by_coin = {k: float(v) for k, v in result.get("profits_by_coin", {}).items()}
        mirror_total_trades_count = {k: float(v) for k, v in result.get("mirror_total_trades_count", {}).items()}

        json_data = {
            "filtered_data": merged_results,
            "response_data": response_data,
            "symbols_winrate": winrates,
            "winning_rate_acc": mirror_winrates,
            "overall": overall,
            "account_metrics": metrics_data,
            "trades_account": trades,
            "profits_by_coin": profits_by_coin,
            "mirror_total_trades_count": mirror_total_trades_count,
            "start_date": start_date_global,
            "end_date": end_date_global,
        }

        cache["/api/initial_load"] = json_data

        return JsonResponse(json_data, status=200)

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)

# queue = asyncio.Queue()
@api.post("/post_filtered")
async def post_filtered(request,
                        mirror_accounts: str = Form(''),
                        start_date: str = Form(start_date_global),
                        end_date: str = Form(end_date_global),
                        symbols: str = Form(None)):

    try:
        global start_date_global, end_date_global, mirrorx_accounts

        start_date_global = start_date
        end_date_global = end_date
        symbols = symbols.split(',') if symbols else None

        # Handle empty mirror_accounts
        mirror_accounts = mirror_accounts.strip()
        if mirror_accounts:
            mirror_accounts_list = mirror_accounts.split(',')
        else:
            mirror_accounts_list = []

        is_mirrorxtotal = "mirrorxtotal" in mirror_accounts_list

        metrics_data = await asyncio.create_task(all_metrics_json_data(start_date, end_date))
        cached_data = await asyncio.create_task(fetch_get_data())
        result = await asyncio.create_task(data_computations(cached_data, start_date_global, end_date_global, mirror_accounts, calculation_types, symbols))

        if cached_data is None:
            return JsonResponse({"error": "Data not available in cache or invalid cache structure."}, status=404)

        if result is None:
            result = {}  # Ensure result is a dictionary

        start_date_dt = datetime.strptime(start_date, "%Y-%m-%d").date()
        end_date_dt = datetime.strptime(end_date, "%Y-%m-%d").date()

        # Convert item['date'] to date object before filtering
        filtered_data = [
            {
                "mirrorx_account": item["mirrorx_account"],
                "date": item["date"].date(),  # Convert to date
                "realizedPnl": item["realizedPnl"],
                "symbol": item["symbol"],
            }
            for item in cached_data
            if start_date_dt <= item["date"].date() <= end_date_dt  # Convert to date
            and (not mirror_accounts_list or item["mirrorx_account"] in mirror_accounts_list)
            and (not symbols or item["symbol"] in symbols)
        ]

        combined_data = filtered_data

        if is_mirrorxtotal:
            # Aggregate data for all mirror accounts and treat it as "all_account"
            mirrorx_all_accounts = [mirrorx1, mirrorx2, mirrorx3, mirrorx4, mirrorx5, mirrorxfund]

            filtered_data_all_account = [
                {
                    "mirrorx_account": item["mirrorx_account"],
                    "date": item["date"].date(),  # Convert to date
                    "realizedPnl": item["realizedPnl"],
                    "symbol": item["symbol"],
                }
                for item in cached_data
                if start_date_dt <= item["date"].date() <= end_date_dt  # Convert to date
                and item["mirrorx_account"] in mirrorx_all_accounts
                and (not symbols or item["symbol"] in symbols)
            ]

            aggregated_data_all_account = defaultdict(lambda: {'mirrorx_account': 'mirrorxtotal', 'date': None, 'realizedPnl': 0, 'symbol': None})

            for item in filtered_data_all_account:
                key = (item['date'], item['symbol'])
                if aggregated_data_all_account[key]['date'] is None:
                    aggregated_data_all_account[key]['date'] = item['date']
                    aggregated_data_all_account[key]['symbol'] = item['symbol']
                aggregated_data_all_account[key]['realizedPnl'] += item['realizedPnl']

            # Update combined_data with the aggregated all_account data
            for aggregated_item in aggregated_data_all_account.values():
                # Try to find a matching item in combined_data
                matched_item = next(
                    (item for item in combined_data if item['date'] == aggregated_item['date'] and item['symbol'] == aggregated_item['symbol']),
                    None
                )
                if matched_item:
                    # If found, update its realizedPnl
                    matched_item['realizedPnl'] += aggregated_item['realizedPnl']
                else:
                    # Otherwise, append the new aggregated item
                    combined_data.append(aggregated_item)

        if not combined_data:
            return JsonResponse({"error": "No data available for the specified range or criteria."}, status=400)

        merged_results = sorted(
            combined_data,
            key=lambda x: (x['date'], x['symbol'], x['mirrorx_account'])
        )

        response_data = {
            'total_realized_pnl': float(result.get('fetch_csv_calculate_total_realized_pnl', 0)),
            'trading_days': float(result.get('calculate_trading_days', 0)),
            'winning_days': float(result.get('winning_days', 0)),
            'total_fees': float(result.get('calculate_total_fees', 0)),
            'max_draw': float(result.get('max_draw', 0)),
            'calculate_buy_sell': result.get('calculate_buy_sell', {})
        }

        overall = {k: float(v) for k, v in result.get("overall", {}).items()}
        trades = {k: float(v) for k, v in result.get("trades", {}).items()}
        winrates = {k: float(v) for k, v in result.get("winrate_per_symbol", {}).items()}
        mirror_winrates = {k: float(v) for k, v in result.get("mirror_winrates", {}).items()}
        profits_by_coin = {k: float(v) for k, v in result.get("profits_by_coin", {}).items()}
        mirror_total_trades_count = {k: float(v) for k, v in result.get("mirror_total_trades_count", {}).items()}

        json_data = {
            "filtered_data": merged_results,
            "response_data": response_data,
            "symbols_winrate": winrates,
            "winning_rate_acc": mirror_winrates,
            "overall": overall,
            "account_metrics": metrics_data,
            "trades_account": trades,
            "profits_by_coin": profits_by_coin,
            "mirror_total_trades_count": mirror_total_trades_count,
            "start_date": start_date_global,
            "end_date": end_date_global,
        }

        cache["/api/post_filtered_data"] = json_data

        return JsonResponse(json_data, status=200, safe=False)

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)

    
@api.get("/get_filtered_data")
async def get_filtered(request):
    data = cache.get("/api/post_filtered_data")
    if data is None:
        data = cache.get("/api/initial_load")
        if data:
            # Ensure data is serialized when storing in the cache
            cache["/api/get_filtered_data"] = orjson.dumps(data).decode('utf-8')
            return JsonResponse(data, safe=False)
        else:
            return JsonResponse({"error": "No data available"}, safe=False)
    else:
        # Convert data to JSON string and then bytes
        serialized_data = orjson.dumps(data).decode('utf-8')

        # Remove the post filtered data from the cache

        # Store the data in the get_filtered_data cache
        cache["/api/get_filtered_data"] = serialized_data
        cache.pop("/api/post_filtered_data")

        return JsonResponse(data, safe=False)

# @api.get("/test_get_filtered_data")
# async def test_get_filtered(request):
#     cached_data = cache.get("/api/get_filtered_data")
#     if cached_data is None:
#         return JsonResponse({"error": "No cached data available"}, safe=False)
#     else:
#         # Deserialize the cached data
#         data = orjson.loads(cached_data)
#         return JsonResponse(data, safe=False)








# @api.get("/get_filtered_data")
# async def get_filtered(request):
#     try:
#         # Fetch data from the queue
#         data = await queue.get()
#     except RuntimeError as e:
#         initial_load = cache.get("/api/initial_load")
#         if initial_load:
#             return JsonResponse(initial_load, safe=False)
#         else:
#             return JsonResponse({"error": "Initial load data not available."}, status=404)
#     except Exception as e:
#         print("error:", e)
#         return JsonResponse({"error": str(e)}, status=500)

#     data_json = orjson.dumps(data)  # Convert data to JSON string and then bytes
#     return HttpResponse(data_json, content_type="application/json")
        

#this is initial load for the home page to view the data.

    # json_data = {
    #     "filtered_data": cached_data,
    #     "response_data": response_data,
    #     "symbols_winrate": winrates,
    #     "winning_rate_acc": mirror_winrates,
    #     "overall": overall,
    #     "trades_account": trades,
    #     "account_metrics": metrics_data
    # } 

    # overall_data = json_data["overall"]  # Extracting just the "overall" data

    # # Serialize the "overall" data to JSON format
    # overall_data_string = json.dumps(overall_data, indent=4)

    # # Print the string representation of the "overall" data
    # print(json_data)

    # # Write the string representation of the "overall" data to a file
    # with open('data.json', 'w') as file:
    #     file.write(overall_data_string)

    # # Cache the json_data
    # cache["/api/initial_load"] = json_data

    # # Return the success response
    # return JsonResponse("success", safe=False, status=200)




# #datefiltering but 7d 1m 3m and 1year.
@api.get("/date_pages")
async def get_pagination(
    request,
    date_range: str = Query("last_7_days", regex="^(last_7_days|last_30_days|last_3_months|last_1_year)$"),
    mirror_accounts: str = Query("")
    
):
    symbols = None

    global start_date_global, end_date_global, mirrorx_accounts

    mirrorx_accounts = mirror_accounts


    print("mirror_accounts", mirror_accounts)

 



    try:
        await asyncio.sleep(0.01)
        # Retrieve data from the cache using the specific key
        ph_timezone = pytz.timezone('Asia/Manila')
        # Get the current date in the specified time zone
        end_date = datetime.now(ph_timezone).date()
        # end_date = datetime.now().date()
        if date_range == "last_7_days":
            last_7_days_ph = end_date - timedelta(days=7)
            start_date = (last_7_days_ph + timedelta(days=1))  

        elif date_range == "last_30_days":
            last_30_days_ph = end_date - timedelta(days=30)
            start_date = (last_30_days_ph + timedelta(days=1))  

        elif date_range == "last_3_months":
            last_90_days_ph = end_date - timedelta(days=90)
            start_date = (last_90_days_ph + timedelta(days=1))  

        elif date_range == "last_1_year":
            lastyear = end_date - timedelta(days=365)
            start_date = (lastyear + timedelta(days=1))  # Adding one day to exclude it
        
        # Retrieve data from the cache using the specific key
        # end_date = datetime.now().date()
        # if date_range == "last_7_days":
        #     start_date = end_date - timedelta(days=7)
        # elif date_range == "last_30_days":
        #     start_date = end_date - timedelta(days=30)
        # elif date_range == "last_3_months":
        #     start_date = end_date - timedelta(days=90)
        # elif date_range == "last_1_year":
        #     start_date = end_date - timedelta(days=365)

        


        cached_data = await asyncio.create_task(fetch_get_data())


        if cached_data is None:
            return JsonResponse({"error": "Data not available in cache or invalid cache structure."}, status=404)
        # data = cached_data["data"]

        # start_date = datetime.strptime(start_date, "%Y-%m-%d").date()
        # end_date = datetime.strptime(end_date, "%Y-%m-%d").date()
        # print(f"filtered {date_range}", start_date, end_date)

        start_date_global = start_date.strftime('%Y-%m-%d')
        end_date_global = end_date.strftime('%Y-%m-%d')
        # print("pages",start_date_global, end_date_global)
        result = await asyncio.create_task(data_computations(cached_data, start_date_global, end_date_global, mirror_accounts, calculation_types, symbols))

        filtered_data = [
            {
                "mirrorx_account": item["mirrorx_account"],
                "date": item["date"],  # Convert datetime to date
                "realizedPnl": item["realizedPnl"],
                "symbol": item["symbol"],
            }
            for item in cached_data
            if start_date <= item["date"].date() <= end_date
            and (not mirror_accounts or item["mirrorx_account"] in mirror_accounts)
            # and (not symbols or item["symbol"] in symbols)
        ]
        filtered_data = sorted(filtered_data, key=lambda item: (item['date'], item['symbol']))
        if not filtered_data:
            return JsonResponse({"error": "No data available for the specified range or criteria."}, status=400)


        # profit_dollar = await asyncio.to_thread(print_profits, clients, initial_balance, mirror_accounts)
        # print('profit_dollar', profit_dollar)
        response_data = {
            #'total_realized_pnl': float(result.get('total_realized_pnl', 0)),
            'total_realized_pnl': result.get('fetch_csv_calculate_total_realized_pnl')
,
            'trading_days': float(result.get('calculate_trading_days', 0)),
            'winning_days': float(result.get('winning_days', 0)),
            'total_fees': float(result.get('calculate_total_fees', 0)),
            'max_draw': float(result.get('max_draw', 0)),
            'calculate_buy_sell': result.get('calculate_buy_sell', 0)


        }
        print(response_data)

        overall = result.get("overall", {})
        trades = result.get("trades", {})
        winrates = result.get("winrate_per_symbol", {})
        mirror_winrates = result.get("mirror_winrates", {})

        # Convert dictionaries to integers
        overall = {k: float(v) for k, v in overall.items()}
        trades = {k: float(v) for k, v in trades.items()}
        winrates = {k: float(v) for k, v in winrates.items()}
        mirror_winrates = {k: float(v) for k, v in mirror_winrates.items()}


        if result is None or not all(calc_type in result for calc_type in calculation_types):
            raise ValueError("Calculation types are not available or incomplete.")

        json_data = {
            "filtered_data": filtered_data,
            "response_data": response_data,
            "symbols_winrate": winrates,
            "winning_rate_acc": mirror_winrates,
            "overall": overall,
            "trades_account": trades
        }

        cache_key = "/api/post_filtered_data"
        cache[cache_key] = json_data

        # Put the data into the queue
        # await queue.put(json_data)

        return JsonResponse("Success", status=200, safe=False)

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)
    
# @api.get("/getCointData")
# async def get_Coint_data(request):
#     """View to return trading data for your_account and FUND account."""
#     try:
#         # Ensure all data types can be JSON-serialized (e.g., float, int, strings)
#         data = compute_combined_metrics()
#         print(f"Data before sending response: {data}")  # Debugging

#         return JsonResponse(data, safe=False)
#     except Exception as e:
#         return JsonResponse({"error": str(e)}, status=500)

# @api.post("/postCoint")
# async def trading_data_view(request,
#                         account_name: str = Form(...),
#                         starting_date: str = Form(...),
#                         ending_date: str = Form(...)):
#     """View to return trading data for one or both accounts based on account name and date range."""

#     try:
#         # Compute data based on account parameter
#         if account_name == 'both':
#             data = compute_for_both_accounts(starting_date, ending_date)
#         else:
#             data = compute_trading_data(account_name, starting_date, ending_date)

#         return JsonResponse(data)

#     except ValueError as e:
#         return JsonResponse({"error": f"Invalid date range format: {str(e)}"}, status=400)
#     except Exception as e:
#         return JsonResponse({"error": str(e)}, status=500)

@api.get("/generate_pdf")
async def print_report(request):
    cached_data = cache.get("/api/get_filtered_data")
    if cached_data is None:
        return JsonResponse({"message": "No data found for generating PDF"}, status=404, safe=False)
    
    json_data = orjson.loads(cached_data)

    # Extract the data needed for the PDF
    overall = json_data.get("overall", {})
    response_data = json_data.get("response_data", {})
    winning_rate_acc = json_data.get("winning_rate_acc", {})
    profits_by_coin = json_data.get("profits_by_coin", {})
    symbols_winrate = json_data.get("symbols_winrate", {})
    start_date = json_data.get("start_date", "N/A")
    end_date = json_data.get("end_date", "N/A")
    mirror_total_trades_count = json_data.get("mirror_total_trades_count", {})
    all_metrics_json_data_entry_data_only = json_data.get("all_metrics_json_data_entry_data_only", {}).get("total_balance_data", {})
    account_metrics = json_data.get("account_metrics", {}).get("total_balance_data", {})
    trades_account = json_data.get("trades_account", {})

    # Print extracted data for debugging
    # print("Overall Data:", overall)
    # print("Response Data:", response_data)
    # print("Winning Rate Acc:", winning_rate_acc)
    # print("Profits by Coin:", profits_by_coin)
    # print("Symbols Winrate:", symbols_winrate)
    # print("Trades Account:", trades_account)
    # print("Account Metrics:", account_metrics)

    # Create the HttpResponse object with the appropriate PDF headers.
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="report.pdf"'

    # Use landscape orientation for the PDF
    pdf = canvas.Canvas(response, pagesize=landscape(letter))
    page_width, page_height = landscape(letter)

    def add_page_header():
        # Add the image at the top right
        image_path = 'static/images/logo.png'
        image_width = 60
        image_height = 60
        image_x = page_width - image_width - 20
        image_y = page_height - image_height - 25
        pdf.drawImage(image_path, image_x, image_y, width=image_width, height=image_height)

        # Current date on the left
        current_date = datetime.now().strftime("%Y-%m-%d")
        date_x = 20
        date_y = image_y + 20
        pdf.setFont("Helvetica", 12)
        pdf.drawString(date_x, date_y, f"Date: {current_date}")

        # Centered text
        centered_text = "Summary of Report"
        pdf.setFont("Helvetica", 16)
        text_width = pdf.stringWidth(centered_text, "Helvetica", 16)
        centered_x = (page_width - text_width) / 2
        text_y = image_y - 20
        pdf.drawString(centered_x, text_y, centered_text)

        # Span date below the centered text
        span_date_text = f"Span date: {start_date} to {end_date}"
        pdf.setFont("Helvetica", 12)
        span_date_width = pdf.stringWidth(span_date_text, "Helvetica", 12)
        span_date_x = (page_width - span_date_width) / 2
        span_date_y = text_y - 20
        pdf.drawString(span_date_x, span_date_y, span_date_text)
        return span_date_y - 40

    current_y = add_page_header()

    def check_page_space(current_y, space_needed):
        nonlocal pdf
        if current_y - space_needed < 50:
            pdf.showPage()
            current_y = add_page_header()
        return current_y

    # Mapping of old keys to new names for overall
    overall_rename_map = {
        "total_trades": "Total Trades",
        "return_percentage": "Return Percentage",
        "overall_winrate": "Overall Winrate",
        "adjusted_winrate": "Adjusted Winrate",
        "total_balance_data": "Starting Balance",
        "total_balance": "Current Balance",
    }

    # Add percentage symbol for specific keys
    percentage_keys = {"Return Percentage", "Overall Winrate", "Adjusted Winrate"}

    # Rename the overall keys and format percentages
    renamed_overall = {
        overall_rename_map.get(k, k): (f"{v:.2f}%" if overall_rename_map.get(k, k) in percentage_keys else f"{v:.2f}" if isinstance(v, (int, float)) else str(v))
        for k, v in overall.items()
        if k != "total_unrealized_pnl" and k != "margin_total"  # Remove Estimated Unrealized Pnl and Margin Total
    }

    # Specifically extract MIRRORXTOTAL value if it exists
    # mirror_total_starting = all_metrics_json_data_entry_data_only.get("MIRRORXTOTAL")
    # if mirror_total_starting is not None:
    #     renamed_overall["Starting Balance"] = mirror_total_starting

    # Ensure Starting Balance comes before Current Balance
    overall_order = ["Total Trades", "Return Percentage", "Overall Winrate", "Adjusted Winrate", "Starting Balance", "Current Balance"]

    # Create the ordered overall data table
    overall_data = [
        [key, renamed_overall[key]] for key in overall_order if key in renamed_overall
    ]

    # Extract and handle the nested starting_balance_data
    starting_balance_data = response_data.get("total_balance_data", {})
    if isinstance(starting_balance_data, str):
        try:
            starting_balance_data = orjson.loads(starting_balance_data)
        except orjson.JSONDecodeError:
            starting_balance_data = {}

    # Mapping of old keys to new names for response data
    response_rename_map = {
        "total_realized_pnl": "Total Profit/Lost",
        "trading_days": "Trading Days",
        "winning_days": "Winning Days",
        "total_fees": "Total Fees",
        "max_draw": "Max Drawdown",
        "calculate_buy_sell": "Buy/Sell"
    }

    # Flatten the "calculate_buy_sell" data into the main dictionary
    if "calculate_buy_sell" in response_data:
        response_data.update(response_data.pop("calculate_buy_sell"))

    # Apply renaming map
    renamed_data = {response_rename_map.get(key, key): value for key, value in response_data.items()}

    # Keys that should be formatted as integers
    integer_keys = {"Trading Days", "Winning Days", "BUY/LONG", "SELL/SHORT"}

    # Rename the response data keys and format values
    percentage_keys = {"BUY/LONG Percentage", "SELL/SHORT Percentage"}
    renamed_response_data = {
        response_rename_map.get(k, k): (f"{int(v)}" if response_rename_map.get(k, k) in integer_keys else f"{v:.2f}%" if response_rename_map.get(k, k) in percentage_keys else f"{v:.2f}" if isinstance(v, (int, float)) else str(v))
        for k, v in response_data.items()
    }

    # Table data for Response Data
    response_data_table = [
        *[[k, v] for k, v in renamed_response_data.items()]
    ]

    # Extract and handle the nested calculate_buy_sell data
    calculate_buy_sell_data = response_data.get("calculate_buy_sell", {})
    if isinstance(calculate_buy_sell_data, str):
        try:
            calculate_buy_sell_data = orjson.loads(calculate_buy_sell_data)
        except orjson.JSONDecodeError:
            calculate_buy_sell_data = {}

    # Set table position for Overall and Response Data
    overall_table_x = 50
    response_data_table_x = overall_table_x + 300  # Adjust spacing as needed
    buy_sell_data_table_x = response_data_table_x + 300  # Adjust spacing for the BUY/LONG table
    table_y = current_y

    pdf.setFont("Helvetica", 8)

    for row_index in range(max(len(overall_data), len(response_data_table))):
        current_y = check_page_space(current_y, 15)
        if row_index < len(overall_data):
            for col_index, cell in enumerate(overall_data[row_index]):
                pdf.drawString(overall_table_x + col_index * 150, table_y - row_index * 15, str(cell))
        if row_index < len(response_data_table):
            for col_index, cell in enumerate(response_data_table[row_index]):
                pdf.drawString(response_data_table_x + col_index * 150, table_y - row_index * 15, str(cell))

    current_y -= max(len(overall_data), len(response_data_table)) * 15 + 20

    # Add the calculate_buy_sell data as a separate section next to response_data table
    for row_index, (key, value) in enumerate(calculate_buy_sell_data.items()):
        current_y = check_page_space(current_y, 15)
        pdf.drawString(buy_sell_data_table_x + 20, table_y - row_index * 15, f"{key}: {value}")

    current_y -= len(calculate_buy_sell_data) * 15 + 20
    # Winning Rate Acc Table
    account_rename_map = {
        "MIRRORX1": "mirrorx1",
        "MIRRORX2": "mirrorx2",
        "MIRRORX3": "mirrorx3",
        "MIRRORX4": "mirrorx4",
        "MIRRORX5": "mirrorx5",
        "MIRRORXFUND": "mirrorxfund",
        # "TEAM": "team",
        
        
    }

    if winning_rate_acc and mirror_total_trades_count and all_metrics_json_data_entry_data_only and account_metrics:
        account_headers = [account_rename_map.get(acc, acc) for acc in winning_rate_acc.keys()]
        print(account_metrics)

        winning_rate_values = [f"{value:.2f}%" if isinstance(value, (int, float)) else str(value) for value in winning_rate_acc.values()]
        mirror_values = [f"{mirror_total_trades_count.get(account, 'N/A')}" if isinstance(mirror_total_trades_count.get(account), int) else str(mirror_total_trades_count.get(account)) for account in winning_rate_acc.keys()]
        mirror_starting_balance = [
            f"{float(all_metrics_json_data_entry_data_only.get(account_rename_map.get(account.lower(), account), 'N/A')):.2f}"
            if isinstance(all_metrics_json_data_entry_data_only.get(account_rename_map.get(account.lower(), account)), (int, float))
            else str(all_metrics_json_data_entry_data_only.get(account_rename_map.get(account.lower(), account), 'N/A'))
            for account in winning_rate_acc.keys()
        ]
        mirror_current_balance = [
            f"{float(account_metrics.get(account_rename_map.get(account.lower(), account), 'N/A')):.2f}"
            if isinstance(account_metrics.get(account_rename_map.get(account.lower(), account)), (int, float))
            else str(account_metrics.get(account_rename_map.get(account.lower(), account), 'N/A'))
            for account in winning_rate_acc.keys()
        ]

        winning_rate_data = [
            ['Account'] + account_headers,
            ['Winning Rate'] + winning_rate_values,
            ['Total Trades'] + mirror_values,
            ['Starting Balance'] + mirror_starting_balance,
            ['Current Balance'] + mirror_current_balance
        ]
        print("account_headers", account_headers)

    else:
        # Check if there are any accounts to process
        if winning_rate_acc or mirror_total_trades_count or all_metrics_json_data_entry_data_only or account_metrics:
            account_headers = [account_rename_map.get(acc, acc) for acc in winning_rate_acc.keys()]
            
            winning_rate_values = [f"{value:.2f}%" if isinstance(value, (int, float)) else str(value) for value in winning_rate_acc.values()]
            mirror_values = [f"{mirror_total_trades_count.get(account, 'N/A')}" if isinstance(mirror_total_trades_count.get(account), int) else str(mirror_total_trades_count.get(account)) for account in winning_rate_acc.keys()]
            mirror_starting_balance = [
                f"{float(all_metrics_json_data_entry_data_only.get(account_rename_map.get(account.lower(), account), 'N/A')):.2f}"
                if isinstance(all_metrics_json_data_entry_data_only.get(account_rename_map.get(account.lower(), account)), (int, float))
                else str(all_metrics_json_data_entry_data_only.get(account_rename_map.get(account.lower(), account), 'N/A'))
                for account in winning_rate_acc.keys()
            ]
            mirror_current_balance = [
                f"{float(account_metrics.get(account_rename_map.get(account.lower(), account), 'N/A')):.2f}"
                if isinstance(account_metrics.get(account_rename_map.get(account.lower(), account)), (int, float))
                else str(account_metrics.get(account_rename_map.get(account.lower(), account), 'N/A'))
                for account in winning_rate_acc.keys()
            ]

            winning_rate_data = [
                ['Account'] + account_headers,
                ['Winning Rate'] + winning_rate_values,
                ['Total Trades'] + mirror_values,
                ['Starting Balance'] + mirror_starting_balance,
                ['Current Balance'] + mirror_current_balance
            ]
            print("account_headers", account_headers)
        else:
            winning_rate_data = [['Account', 'Winning Rate', 'Mirror Total Trades Profit', 'Mirror Starting Balance', 'Mirror Current Balance']]

    # Set table position for Winning Rate Acc
    winning_rate_table_x = 50
    winning_rate_table_y = current_y

    # Draw the Winning Rate Acc table
    pdf.setFont("Helvetica", 7)
    for row_index, row in enumerate(winning_rate_data):
        current_y = check_page_space(current_y, 15)
        for col_index, cell in enumerate(row):
            pdf.drawString(winning_rate_table_x + col_index * 65, winning_rate_table_y - row_index * 15, str(cell))

    current_y -= len(winning_rate_data) * 15 + 20

    # Combine Symbols Winrate with Profits by Coin
    if profits_by_coin and symbols_winrate and trades_account:
        coins = list(symbols_winrate.keys())  # Use keys from symbols_winrate for consistency
        
        combined_data = [
            ["", *coins],  # Empty string for the header row
            ["Profit/Loss", *[f"{float(profits_by_coin.get(coin, 'N/A')):.2f}" for coin in coins]],
            ["Winrate", *[f"{float(symbols_winrate.get(coin, 'N/A')):.2f}%" for coin in coins]],
            ["Total Trades", *[f"{int(trades_account.get(coin.replace('USDT', '_trades'), 'N/A'))}" for coin in coins]]
        ]
    else:
        combined_data = [
            ["", "N/A"],
            ["Profit/Loss", "N/A"],
            ["Winrate", "N/A"],
            ["Total Trades", "N/A"]
        ]


    # Debugging output for combined data
    # print("Combined Data:")
    for row in combined_data:
        # print(row)
        pass

    # Set table position for Combined data (Coin table)
    coin_table_x = 50
    coin_table_y = current_y

    # Draw the Coin data table with headers positioned vertically
    pdf.setFont("Helvetica", 7)
    row_height = 15

    for row_index, row_data in enumerate(combined_data):
        current_y = check_page_space(current_y, row_height)
        for col_index, cell_value in enumerate(row_data):
            x_position = coin_table_x + col_index * 50
            pdf.drawString(x_position, coin_table_y - row_index * row_height, str(cell_value))

    current_y -= len(combined_data) * row_height + 20  # Adjust for spacing between tables

    # Save the PDF
    pdf.showPage()
    pdf.save()

    return response

# Dependency to get the SQLAlchemy session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@api.get("/get_backtest_data")
async def show_backtest_history(request):
    # Create a new session
    db: Session = next(get_db())
    
    # Query all records from backtest_data table
    backtest_data_list = db.query(backtest_data).all()

    # Convert the SQLAlchemy objects to dictionaries
    data = [
        {
            "id": item.id,
            "symbol": item.symbol,
            "ver": item.ver,
            "interval": item.interval,
            "trade_start": item.trade_start.isoformat() if item.trade_start else None,
            "trade_end": item.trade_end.isoformat() if item.trade_end else None,
            "datetoday": item.datetoday.isoformat() if item.datetoday else None,
            "decision_boundary": item.decision_boundary,
            "svm_backtest": item.svm_backtest,
            "svm_backtest_one": item.svm_backtest_one,
            "tradesheet": item.tradesheet,
            "statistics": item.statistics,
        }
        for item in backtest_data_list
    ]

    # Return the list as JSON
    return JsonResponse(data, safe=False)
#from binance api getting the data from realized pnl.
# @api.get("/account_metrics") #from binance api
# async def get_live_data_from_binance_api(request):

#     global start_date_global
#     mirror_accounts = cache.get("/api/mirrorxaccount")
#     metrics_data = await asyncio.create_task(metrics(accounts))

#     try:

#         # cached_data = await fetch_get_data()

#         await asyncio.sleep(0.01)    
#         task2 = asyncio.create_task(computation2(mirror_accounts, start_date_global))
#         result2 = await task2
#         # overall_account = result2.get("overall")
#         # print(overall_account)

#         overall_account = {
#         'total_trades': int(result2.get("overall").get('total_trades')),
#         'return_percentage': result2.get("overall").get('return_percentage'),
#         'total_unrealized_pnl': result2.get("overall").get('total_unrealized_pnl'),
#         'overall_winrate': result2.get("overall").get('overall_winrate'),
#         'adjusted_winrate': result2.get("overall").get('adjusted_winrate'),
#         'total_balance': result2.get("overall").get('total_balance'),
#         'margin_total': result2.get("overall").get('margin_total'),
#         'metrics_data': metrics_data

#         }

#         cache["/api/account_metrics"] = overall_account
        
#         return JsonResponse(overall_account)

#     except Exception as e:
#         return JsonResponse({"error UPDATE YOUR TIME": str(e)}, status=500, safe=False)




    
    

    