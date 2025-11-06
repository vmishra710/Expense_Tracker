import time
from fastapi import Request, HTTPException, status


# In-memory store : {"ip_address" : {"window_start" : float, "count" : int}}
RATE_LIMIT_STORE = {}

RATE_LIMIT = 3  # max requests
WINDOW_SIZE = 60  # seconds

async def rate_limiter(request: Request, call_next):
    if request.url.path == '/auth/token':
        client_ip = request.client.host
        current_time = time.time()
        record = RATE_LIMIT_STORE.get(client_ip)

        if record:
            window_start = record["window_start"]
            count = record["count"]

            # Check if windows expired
            if current_time - window_start < WINDOW_SIZE:
                # Same window
                if count >= RATE_LIMIT:
                    # Too many requests
                    raise HTTPException(
                        status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                        detail="Too many requests, please try again later.",
                        headers ={"Retry-After": str(int(WINDOW_SIZE-(current_time-window_start)))}
                    )
                else:
                    record["count"] += 1
                    RATE_LIMIT_STORE[client_ip] = record
            else:
                # Reset window
                RATE_LIMIT_STORE[client_ip] = {
                    "window_start": current_time,
                    "count": 1
                }

        else:
            # First request from this ip
            RATE_LIMIT_STORE[client_ip] = {
                "window_start": current_time,
                "count": 1
            }

    # Continue to next middleware or endpoint
    response = await call_next(request)
    return response
