import numpy as np

from abc import ABC
from .schemas import GameNewRequest, GameTurnRequest, GameBoard


class BaseGameClass(ABC):
    def __init__(self) -> None:
        """
        Initializes the class.
        """
        super().__init__()
        self.clear_field = " "
        self.mine_filed = "X"
        self.count_numbers = ["0", "1", "2", "3", "4", "5", "6", "7", "8"]


class GenerateEmptyBoard(BaseGameClass):
    def __init__(self) -> None:
        """
        Initializes the class.
        """
        super().__init__()

    def generate_empty_game_board(self, height: int, width: int) -> np.ndarray:
        """
        Generates an empty game board.

        :param height: The height of the game board.
        :param width: The width of the game board.
        :return: The generated empty game board.
        """
        return np.full((height, width), self.clear_field, dtype=str)


class GenerateBoard(GenerateEmptyBoard):
    def __init__(self) -> None:
        """
        Initializes the class.
        """
        super().__init__()

    def __place_mines(self, playing_field: np.ndarray, mines_count: int) -> None:
        """
        Places mines on the game board.

        :param playing_field: The game board.
        :param mines_count: The number of mines to place.
        """
        height, width = playing_field.shape
        mine_indices = np.random.choice(height * width, mines_count, replace=False)
        playing_field.flat[mine_indices] = self.mine_filed

    def generate_board(self, data_game: GameNewRequest) -> list:
        """
        Generates a game board with mines.

        :param data_game: Request data containing game parameters.
        :return: The generated game board.
        """
        playing_field = self.generate_empty_game_board(data_game.height, data_game.width)
        self.__place_mines(playing_field, data_game.mines_count)
        return playing_field.tolist()


class CheckField(BaseGameClass):
    def __init__(self) -> None:
        """
        Initializes the class.
        """
        super().__init__()

    def is_mine(self, playing_field: GameBoard, place_mine: GameTurnRequest) -> bool:
        """
        Checks if the specified field contains a mine.

        :param playing_field: The game board.
        :param place_mine: Coordinates of the cell to check.
        :return: True if the cell contains a mine, False otherwise.
        """
        field = playing_field[place_mine.row][place_mine.col]

        if field == self.mine_filed:
            return True
        return False

    def is_open(self, playing_field: GameBoard, place: GameTurnRequest) -> bool:
        """
        Checks if the specified field is open.

        :param playing_field: The game board.
        :param place: Coordinates of the cell to check.
        :return: True if the cell is open, False otherwise.
        """
        field = playing_field[place.row][place.col]

        if field in self.count_numbers or field == self.mine_filed:
            return True
        return False


class OpenFields(BaseGameClass):
    """
    Class for opening fields on the game board.
    """
    def __init__(self, playing_field: GameBoard, mines_field: GameBoard) -> None:
        """
        Initializes the class.

        :param playing_field: The game board.
        :param mines_field: The field with mine placements.
        """
        super().__init__()
        self.playing_field = playing_field
        self.mines_field = mines_field
        self.height, self.width = len(playing_field), len(playing_field[0])

    def count_mines_around(self, row: int, col: int) -> int:
        """
        Counts the number of mines around the selected cell.

        :param row: The row number of the cell.
        :param col: The column number of the cell.
        :return: The number of mines around the selected cell.
        """
        mines_count = 0
        for i in range(max(0, row - 1), min(self.height, row + 2)):
            for j in range(max(0, col - 1), min(self.width, col + 2)):
                if self.mines_field[i][j] == self.mine_filed:
                    mines_count += 1
        return mines_count

    def open_fields(self, row: int, col: int) -> None:
        """
        Opens the fields around the selected cell and places the number of mines nearby.

        :param row: The row number of the selected cell.
        :param col: The column number of the selected cell.
        """
        mines_count = self.count_mines_around(row, col)
        self.playing_field[row][col] = str(mines_count)

        if mines_count == 0:
            for i in range(max(0, row - 1), min(self.height, row + 2)):
                for j in range(max(0, col - 1), min(self.width, col + 2)):
                    if self.playing_field[i][j] == self.clear_field:
                        self.open_fields(i, j)

    def open_all_fields(self) -> None:
        """
        Opens all fields on the game board.
        """
        for i in range(self.height):
            for j in range(self.width):
                if self.mines_field[i][j] == self.mine_filed:
                    self.playing_field[i][j] = self.mine_filed
                else:
                    self.playing_field[i][j] = self.count_mines_around(i, j)

    def mark_empty_cells_as_M(self):
        """
        Marks all remaining empty cells with "M".
        """
        for i in range(self.height):
            for j in range(self.width):
                if self.playing_field[i][j] == self.clear_field:
                    self.playing_field[i][j] = "M"

    def is_game_completed(self) -> bool:
        """
        Checks if all non-mine cells on the game board are opened.

        :return: True if all non-mine cells are opened, False otherwise.
        """
        for i in range(self.height):
            for j in range(self.width):
                if self.playing_field[i][j] == self.clear_field \
                and self.mines_field[i][j] != self.mine_filed:
                    return False
        return True

