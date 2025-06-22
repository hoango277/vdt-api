import os
from dotenv import load_dotenv
from fastapi import FastAPI, Request, Response
from slowapi import Limiter
from slowapi.util import get_remote_address
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.middleware.cors import CORSMiddleware
from starlette.responses import JSONResponse

from routers import student as student_router
from configs.database import Base, engine
from routers import authentication as auth_router
load_dotenv()
FRONTEND_ORIGIN = os.getenv("FRONTEND_ORIGIN")
from prometheus_client import Counter, generate_latest, CONTENT_TYPE_LATEST
from slowapi.errors import RateLimitExceeded

app = FastAPI()
limiter = Limiter(key_func=get_remote_address)


REQUEST_COUNTER = Counter(
    "fastapi_request_count",
    "Số lượng request",
    ["method", "endpoint", "status_code"]
)
@app.exception_handler(RateLimitExceeded)
async def rate_limit_handler(request: Request, exc: RateLimitExceeded):
    return JSONResponse(
        status_code=409,
        content={"detail": "Rate limit exceeded. Try again later."}
    )

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, rate_limit_handler)
@app.get("/")
@limiter.limit("10/minute")
async def root(request: Request):
    return {"message": "Hello Viettel Digital Talent 2025!"}

class MetricsMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        REQUEST_COUNTER.labels(
            method=request.method,
            endpoint=request.url.path,
            status_code=response.status_code
        ).inc()
        return response

app.add_middleware(MetricsMiddleware)

@app.get("/metrics")
def metrics():
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        FRONTEND_ORIGIN
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(student_router.router)
app.include_router(auth_router.router)

Base.metadata.create_all(bind=engine)