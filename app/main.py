from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi import status

from redis_init import get_redis
from custom_openapi import app, custom_openapi
from minesweeper.router import router as minesweeper_router
from minesweeper.schemas import ErrorResponse


@app.on_event("startup")
async def init_redis():
    get_redis()


app.openapi = custom_openapi


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class BaseGameException(Exception):
    def __init__(self, detail: str):
        self.detail = detail

        
@app.exception_handler(BaseGameException)
async def custom_exception_handler(request, exc: BaseGameException):
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={"errors": exc.detail}
    )


app.include_router(
    minesweeper_router,
    prefix="/api/v1/minesweeper",
    tags=["Minesweeper"],
    responses={
        400: {"model": ErrorResponse},
    },
)
