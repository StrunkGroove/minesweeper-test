import dataclasses

from os import getenv
from typing import List
from uuid import UUID
from fastapi import HTTPException, status
from pydantic.dataclasses import dataclass
from .errors import InvalidSizeException

@dataclass
class ErrorResponse:
    error: str = dataclasses.field(
        metadata=dict(
            example="Произошла непредвиденная ошибка",
            description="Описание ошибки"
        ),
    )


@dataclass
class GameNewRequest:
    width: int = dataclasses.field(
        metadata=dict(
            example=10, 
            description="Ширина игрового поля",
        ),
    )
    height: int = dataclasses.field(
        metadata=dict(
            example=10, 
            description="Высота игрового поля",
        ),
    )
    mines_count: int = dataclasses.field(
        metadata=dict(
            example=10, 
            description="Количество мин на поле",
        ),
    )

    def __post_init__(self):
        self.validate_fields()

    def validate_fields(self):
        max_width = int(getenv("MAX_WIDHT"))
        max_height = int(getenv("MAX_HEIGHT"))
        max_mines = self.width * self.height - 1

        if self.width > max_width \
        or self.height > max_height \
        or self.mines_count > max_mines:
            raise InvalidSizeException()


@dataclass
class GameIdField:
    game_id: UUID = dataclasses.field(
        metadata=dict(
            example="01234567-89AB-CDEF-0123-456789ABCDEF",
            description="Идентификатор игры"
        ),
    )


@dataclass
class GameTurnRequest(GameIdField):
    col: int = dataclasses.field(
        metadata=dict(
            example=5,
            description="Колонка проверяемой ячейки (нумерация c нуля)"
        ),
    )
    row: int = dataclasses.field(
        metadata=dict(
            example=5, 
            description="Ряд проверяемой ячейки (нумерация c нуля)"
        ),
    )


@dataclass
class GameBoard:
    field: List[List[str]] = dataclasses.field(
        metadata=dict(
            description="Строки минного поля (количество равно высоте height)"),
    )


@dataclass
class GameInfoResponse(GameIdField, GameNewRequest, GameBoard):
    completed: bool = dataclasses.field(
        metadata=dict(
            example=False, 
            description="Завершена ли игра"
        ),
    )
