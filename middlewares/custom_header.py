import time
from fastapi import Request
# from starlette.middleware.base import BaseHTTPMiddleware
#
# class ProcessTimeHeaderMiddleware(BaseHTTPMiddleware):
#     async def dispatch(self, request, call_next):
#         start_time = time.perf_counter()
#         response = await call_next(request)
#         process_time = time.perf_counter() - start_time
#         #response.headers["X-Process-Time"] = f"{process_time : .4f}s"
#         return response


async def add_process_time_header(request : Request, call_next):
    start_time = time.perf_counter()
    response = await call_next(request)
    process_time = time.perf_counter() - start_time
    response.headers["X-Process-Time"] = f"{process_time : .4f}s"
    return response