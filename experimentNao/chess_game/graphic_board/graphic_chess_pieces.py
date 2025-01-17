from lib import util
from enum import Enum


class PieceType(Enum):
    OWN_PIECE = 1
    OPPONENT_PIECE = 2
    MOVE = 3


class GraphicPiece:
    def __init__(self, image, position, graphic_board, button=None, type_=PieceType.OWN_PIECE):
        """ graphic piece of the chess board. Corresponds to an element of the game that has to be visually represented,
        and it can be either a piece (own or of the opponent) or a move. It can be represented by a button or a static
        image.


        Parameters
        ----------
        image : PIL.ImageTk.PhotoImage
            image that represent the element
        position : Union[str, lib.util.Point]
            position of the cell that is associated with the piece or move
        graphic_board : experimentNao.chess_game.graphic_board.graphic_chess_board.GraphicChessBoard
            the board where the graphic piece lives
        button : Union[None, tkinter.Button]
            button that is associated with the element. In case element is a static figure, button is 'None'
        type_ : Union[str, experimentNao.chess_game.graphic_board.graphic_chess_pieces.PieceType]
            type of the element
        """
        self.button = button
        self.image = image
        self.type = type_        # type 'own_piece', 'opponent_piece', 'move'
        self.position_in_board = position
        self.add_to_graphic_board(graphic_board)

    def add_button(self, button):
        """ add a button to the Figure element

        Parameters
        ----------
        button :
        """
        self.button = button

    def remove_button(self):
        """ destroy and remove the button of the Figure element

        """
        self.button.destroy()
        self.button = None

    def add_to_graphic_board(self, graphic_board):
        graphic_board.figures_grid[self.position_in_board.x][self.position_in_board.y] = self
        graphic_board.list_of_graphic_pieces.append(self)
