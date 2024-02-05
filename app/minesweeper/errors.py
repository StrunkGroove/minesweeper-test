from abc import ABC
from os import getenv
from fastapi import HTTPException, status


class BaseGameException(HTTPException, ABC):
    def __init__(self, detail: str):
        headers = {'errors': detail}
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=detail, 
            headers=headers
        )


class GameNotFoundException(BaseGameException):
    def __init__(self):
        super().__init__(detail="Game not found")


class GameCompletedException(BaseGameException):
    def __init__(self):
        super().__init__(detail="Game is already completed")


class FieldOpenedException(BaseGameException):
    def __init__(self):
        super().__init__(detail="Field is already open")


class InvalidSizeException(BaseGameException):
    def __init__(self):
        max_width = int(getenv("MAX_WIDHT"))
        max_height = int(getenv("MAX_HEIGHT"))
        error_message = (
            f"Значение 'width' должно быть до {max_width}, " 
            f"'height'до {max_height} " 
            f"и mines_count до ('width' * 'height' - 1)."
        )
        super().__init__(detail=error_message)