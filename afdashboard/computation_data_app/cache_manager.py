from cachetools import cached, TTLCache, LRUCache
import diskcache
import asyncio


# testing and diskcached storage no need to run http://localhost:8000/api/get_data. because it load on cachefile storage!zzyy
# cache = diskcache.Cache(r"/home/gjin/Documents/jonathan_project/AlgoforceDashboard/AlgoforceDashboard/afdashboard/cachefile")

# ramcached needs to execute the URL in a browser using the following address: http://localhost:8000/api/get_data.
cache = LRUCache(maxsize=1000)

# cache = TTLCache(maxsize=10, ttl=timedelta(hours=4), timer=datetime.now)

async def fetch_get_data():
    return cache.get("/api/get_data") or {}

async def fetch_get_all_data():
    return cache.get("/api/get_all_data") or {}



result = asyncio.run(fetch_get_all_data())
# print(result)