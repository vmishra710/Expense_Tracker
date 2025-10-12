import time
import logging
from fastapi import Request, HTTPException
from starlette import status

import config
from jose import jwt, JWTError

# Configure Logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger("middleware")

# Middleware function
async def log_requests(request : Request, call_next):
    start_time = time.perf_counter()

    user_id = None

    # Extract token from Authorization header
    auth_header = request.headers.get("Authorization")
    if auth_header and auth_header.startswith("Bearer"):
        token = auth_header.split(" ")[1]
        try:
            # Decoding the JWT token
            payload = jwt.decode(token, config.SECRET_KEY, config.ALGORITHM)
            request.state.user_id = payload.get('id')
        except JWTError:
            # Token is invalid or expired
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired token")

    # Log the incoming request
    user_id = getattr(request.state, "user_id", None)
    user_part = f"[User: {user_id}]" if user_id else "[User: Anonymous]"
    logger.info(f"➡️ {user_part} {request.method} {request.url.path} - Incoming request")

    # Process the request and get the response
    response = await call_next(request)

    # Calculate how long it took
    process_time = time.perf_counter() - start_time

    # Log the response
    logger.info(
        f"⬅️ {user_part} {request.method} {request.url.path} - "
        f"Status: {response.status_code} - "
        f"Time: {process_time:.4f}s"
    )

    return response