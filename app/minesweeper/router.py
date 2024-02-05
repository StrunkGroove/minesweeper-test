import uuid
import json

from fastapi import APIRouter, Depends
from redis import Redis
from redis_init import get_redis
from .game_logic import (
    GenerateBoard, 
    GenerateEmptyBoard,
    CheckField,
    OpenFields,
)
from .schemas import (
    GameNewRequest,
    GameTurnRequest,
    GameInfoResponse,
)
from .errors import (
    FieldOpenedException,
    GameNotFoundException,
    GameCompletedException,
)

router = APIRouter()


@router.post("/new", response_model=GameInfoResponse)
async def new(data_game: GameNewRequest, rd: Redis = Depends(get_redis)):
    game_id = str(uuid.uuid4())

    empty_board = GenerateEmptyBoard().generate_empty_game_board(
        height=data_game.height, 
        width=data_game.width
    )
    empty_board = empty_board.tolist()

    game_data = {
        "width": data_game.width,
        "height": data_game.height,
        "mines_count": data_game.mines_count,
        "completed": False,
        "field_mines": GenerateBoard().generate_board(data_game),
        "field": empty_board,
    }

    rd.set(game_id, json.dumps(game_data))

    del game_data["field_mines"]
    
    return GameInfoResponse(game_id=game_id, **game_data)


@router.post("/turn", response_model=GameInfoResponse)
async def turn(turn: GameTurnRequest, rd: Redis = Depends(get_redis)):
    game_id = str(turn.game_id)
    game_data = rd.get(str(game_id))

    if game_data is None:
        raise GameNotFoundException()

    game_data = json.loads(game_data)
    field_mines = game_data.pop("field_mines")
    field = game_data.pop("field")

    if game_data["completed"] is True:
        raise GameCompletedException()

    is_open = CheckField().is_open(field, turn)
    if is_open is True:
        raise FieldOpenedException()
    
    game = OpenFields(field, field_mines)

    is_mine = CheckField().is_mine(field_mines, turn)
    if is_mine is True:
        game.open_all_fields()

        game_data["completed"] = True

        rd.set(game_id, json.dumps({
            **game_data, 
            "field_mines": field_mines,
            "field": game.playing_field
        }))

        return GameInfoResponse(**game_data, game_id=game_id, field=game.playing_field)

    game.open_fields(turn.row, turn.col)
    
    status = game.is_game_completed()
    
    if status is True:
        game_data["completed"] = True
        game.mark_empty_cells_as_M()
        
    rd.set(game_id, json.dumps({
        **game_data, 
        "field_mines": field_mines,
        "field": game.playing_field
    }))

    return GameInfoResponse(
        **game_data, 
        game_id=game_id, 
        field=game.playing_field
    )
