import time
import tkinter as tk

from PIL import ImageTk, Image

from path_config import repo_root
from experimentNao.chess_game.graphic_board.graphic_chess_pieces import GraphicPiece, PieceType
from lib.util import Point


class GraphicChessBoard:
    def __init__(self, my_chess_engine, dimensions, window):
        self.chess_engine = my_chess_engine
        self.ideal_move = None
        # Constants                                                       --> board positions - numbers and letters to
        self.board_position_letters, self.board_position_numbers = 'abcdefgh', '87654321'  # show the position of pieces
        self.light_color, self.dark_color = '#ffce9e', '#d18b47'        # --> color codes for board
        # Dimensions: size of each square is the largest int for which 8 squares fit in dimensions, minus a margin of 30
        self.canvas_dimensions = dimensions
        self.size_of_each_square = int((dimensions - 30) / 8)
        self.boundary_pixels = 1
        self.board_dimensions = self.size_of_each_square * 8   # actual dimension of board is 8 times the len of square
        # save window and canvas where board will be drawn
        self.main_window = window
        self.canvas = window.canvases[0]
        # grid and list to save all the figures objects, so that they don't disappear with tkinter
        self.list_of_graphic_pieces = []     # list of figures and buttons
        self.figures_grid = None             # create figures grid
        self.create_grid_for_figures()
        # draw the board
        self.draw_board()

    def draw_board(self):
        """ draws the chess board, including all the cells and name tags of positions

        """
        for i in range(8):
            for j in range(8):
                pos = Point(i, j)
                self.draw_cell(pos, fill=(self.light_color if self.get_color_of_square(pos) == 'l' else self.dark_color))
        self.draw_board_position_tags()

    def draw_cell(self, pos, fill='', outline='', bd=0, tags=''):
        """ draws the cell in position 'pos'

        Parameters
        ----------
        pos : lib.util.Point
            position of the cell in coordinates of the screen (x, y)
        fill : str
            background color of cell
        outline : str
            outline color of cell - in case it is needed to highlight the cell
        bd : int
            size of outline of cell - in case it is needed to highlight the cell
        tags : str
            tag of cell; useful in order to delete the cell later
        """
        self.canvas.create_rectangle(pos.x * self.size_of_each_square,
                                     pos.y * self.size_of_each_square,
                                     (pos.x + 1) * self.size_of_each_square - 1,
                                     (pos.y + 1) * self.size_of_each_square - 1,
                                     fill=fill, outline=outline, width=bd, tags=tags)

    def draw_board_position_tags(self):
        """ draws the name tags of the positions: the numbers (vertical), and letters (horizontal)

        """
        pixel_line_of_pos_tags = (self.board_dimensions + self.canvas_dimensions) / 2   # position of 2 lines with tags
        font_, color_ = 'Helvetica 15', '#7c644c'
        for i in range(8):      # draws the numbers (vertical) and letters (horizontal) in parallel
            next_position_pixel = (i + 0.5) * self.size_of_each_square
            next_char = (i if not self.chess_engine.computer_color_white else 7 - i)    # next position tag to draw
            self.canvas.create_text(pixel_line_of_pos_tags, next_position_pixel,
                                    text=self.board_position_numbers[next_char], font=font_, fill=color_)
            self.canvas.create_text(next_position_pixel, pixel_line_of_pos_tags,
                                    text=self.board_position_letters[next_char], font=font_, fill=color_)

    def draw_pieces_from_fen(self, fen):
        """ adds the pieces to the board given a FEN configuration.

        Parameters
        ----------
        fen : str
        """
        i, j = 0, 0
        for char in fen:
            if char == ' ':           # Reached the end of board configuration in fen
                break
            elif char == '/':         # Next line (aka row)
                i = 0
                j += 1
            elif char.isnumeric():    # Stay in the row and skip a number of cells
                i += int(char)
            else:                     # Stay in the row and draw a piece; at the end, move to next square (aka column)
                piece_position = (Point(i, j) if not self.chess_engine.computer_color_white else Point(7 - i, 7 - j))
                self.draw_piece_in_position(char.lower(), piece_position, 'l' if char.isupper() else 'd')
                i += 1

    def draw_pieces_from_board_engine(self):
        """ adds (draws) the pieces to the board given what is saved in the board of self.my_chess_engine

        """
        for i in range(8):
            for j in range(8):
                chess_position = self.convert_board_index_into_chess_pos(Point(i, j))
                in_position = self.chess_engine.stockfish.get_what_is_on_square(chess_position)
                if in_position is not None:
                    piece = str(in_position).lower()
                    piece_name = piece[13] if 'knight' in piece else piece[12]
                    self.draw_piece_in_position(piece_name, Point(i, j), 'l' if piece[6] == 'w' else 'd')

    def draw_pieces_before_1st_move_from_board_engine(self, first_move):
        """ adds (draws) the pieces to the board given what is saved in the board of self.my_chess_engine before
        the first move of the opponent

        """
        old_pos, new_pos = first_move[0:2], first_move[2:4]
        piece_moved = self.chess_engine.stockfish.get_what_is_on_square(new_pos)
        for i in range(8):
            for j in range(8):
                chess_position = self.convert_board_index_into_chess_pos(Point(i, j))
                in_position = self.chess_engine.stockfish.get_what_is_on_square(chess_position)
                if chess_position == new_pos:   # do not draw the moved_piece in the new position
                    assert in_position == piece_moved
                    in_position = self.chess_engine.piece_taken_before_puzzle_start
                if chess_position == old_pos:
                    in_position = piece_moved
                if in_position is not None:
                    piece = str(in_position).lower()
                    piece_name = piece[13] if 'knight' in piece else piece[12]
                    self.draw_piece_in_position(piece_name, Point(i, j), 'l' if piece[6] == 'w' else 'd')

    def draw_piece_in_position(self, piece_name, position, piece_color):
        """ draws a piece in its position. It is drawn as a button if it is the player's turn and the color of the piece
        corresponds to the players color. Otherwise, it is drawn as an image

        Parameters
        ----------
        piece_name : Union[str, List[str]]
        position : lib.util.Point
        piece_color : str
        """
        figure_name = 'Chess_' + piece_name + piece_color + self.get_color_of_square(position) + '45.svg.png'
        if self.chess_engine.computer_color_white == (piece_color == 'd') and self.chess_engine.is_humans_turn():
            img = self.create_image_for_cell(figure_name=figure_name)       # if it is player's piece, and player's turn
            self.draw_button_w_image_in_cell(position, img, PieceType.OWN_PIECE,         # --> draw button
                                             command=lambda: self.button_select_piece(position))
        else:                                                  # if the piece belongs to the computer or computer's turn
            self.draw_image_in_cell(position, self.create_image_for_cell(figure_name))   # --> just draw the piece

    def draw_button_w_image_in_cell(self, position, img, piece_type, command, bd=0, bg_color='white'):
        """ draw a button with an image in a cell of the chess board

        Parameters
        ----------
        position : lib.util.Point
            position of the cell in (x, y) coordinates
        img : PIL.ImageTk.PhotoImage
            image to be drawn in the button
        piece_type : Union[experimentNao.chess_game.graphic_board.graphic_chess_pieces.PieceType, str]
            type of piece or element that the button corresponds to
        command : function
            the function that is run where the button is clicked
        bd : int
            size of the border of the button
        bg_color : str
            color of the border of the button
        """
        button = tk.Button(self.canvas, image=img, command=command, bd=bd, bg=bg_color, disabledforeground='green')
        button.place(x=position.x * self.size_of_each_square, y=position.y * self.size_of_each_square)
        GraphicPiece(img, position, self, button, piece_type)  # save image and button in object

    def draw_image_in_cell(self, position, img, piece_type=PieceType.OPPONENT_PIECE):
        """ draw image in a cell of the chess board

        Parameters
        ----------
        position : lib.util.Point
            position of cell
        img : PIL.ImageTk.PhotoImage
        piece_type : Union[str, experimentNao.chess_game.graphic_board.graphic_chess_pieces.PieceType]
        """
        self.canvas.create_image(position.x * self.size_of_each_square + self.boundary_pixels,
                                 position.y * self.size_of_each_square + self.boundary_pixels, image=img, anchor=tk.NW)
        GraphicPiece(img, position, self, None, piece_type)  # save image (None for button) in grid

    def create_image_for_cell(self, figure_name, size_reduction=0):
        """ create and resize image to be placed in a cell of the chess board

        Parameters
        ----------
        figure_name : str
            name of the figure to be drawn. It is assumed that it is on the folder described by self.path4figs
        size_reduction : int
            if needed, number of pixels that the figure should be smaller than the predefined size to fit in the cell

        Returns
        -------
        PIL.ImageTk.PhotoImage
        """
        figs_size = int(self.size_of_each_square - self.boundary_pixels * 2 - size_reduction)
        img = ImageTk.PhotoImage(Image.open(self.main_window.path4img/figure_name).resize((figs_size, figs_size)))
        return img

    def button_select_piece(self, position_on_board):
        """ command of the button that is run when player clicks in a piece. Shows the possible next moves that start
        with that piece.

        Parameters
        ----------
        position_on_board : lib.util.Point
            position of the cell where the player clicked
        """
        # 1. Deactivate the other buttons that correspond to OWN PIECES
        for piece in self.list_of_graphic_pieces:
            if piece.type == PieceType.OWN_PIECE:
                self.toggle_button_function_of_own_piece(piece, position_on_board, tk.DISABLED)
        # 2. Show potential moves to player
        self.show_moves_to_be_made_from_selected_piece(position_on_board)

    def show_moves_to_be_made_from_selected_piece(self, position_on_board):
        """ Show moves that human can make from the piece that is currently selected

        Parameters
        ----------
        position_on_board : lib.util.Point
            position of the cell where the player clicked
        """
        #
        for move in self.chess_engine.board.legal_moves:  # from current legal moves in form 'pos1pos2'(eg: a3a4), check
            if str(move)[0:2] == self.convert_board_index_into_chess_pos(position_on_board):  # if pos1 = piece position
                new_pos = self.convert_move_into_board_indices(move, start=False)     # potential position after move
                ele_in_new_pos = self.get_piece_fig_from_grid(new_pos)
                if not isinstance(ele_in_new_pos, GraphicPiece):        # Case A: if move goes to an empty position
                    img = self.create_image_for_cell(figure_name='cross_' + self.get_color_of_square(new_pos) + '.png')
                    self.draw_button_w_image_in_cell(new_pos, img, PieceType.MOVE,
                                                     lambda m=move: self.button_make_move(m))
                elif ele_in_new_pos.button is None:                     # Case B: if move is a take
                    self.draw_button_w_image_in_cell(new_pos, ele_in_new_pos.image, PieceType.OPPONENT_PIECE,
                                                     lambda m=move: self.button_make_move(m), bd=1, bg_color='green')

    def button_unselect_piece(self, position_on_board):
        """ command of the button that is run when player clicks in a piece, once that piece was already selected.
        Erases the possible next moves that start with that piece, and resets the board to the state of the board
        before anything was clicked.

        Parameters
        ----------
        position_on_board : lib.util.Point
            position of the cell where the player clicked
        """
        for piece in self.list_of_graphic_pieces:
            if piece.button is not None:
                if piece.type == PieceType.OWN_PIECE:
                    self.toggle_button_function_of_own_piece(piece, position_on_board, tk.NORMAL)
                else:       # Remove all the buttons that show the possible moves or takes
                    piece.remove_button()                   # destroy button for move or take
                    if piece.type == PieceType.MOVE:        # delete PieceFigure for moves (but not for takes)
                        self.figures_grid[piece.position_in_board.x][piece.position_in_board.y] = None

    def toggle_button_function_of_own_piece(self, piece, position_on_board, new_state):
        """ changes that state of the cells with the piece of the player. If a piece is selected, then it disables
        all buttons and changes the command of that piece to 'unselect piece'. If a piece is being unselected, then it
        enabled all buttons with own pieces again, and changes the command of that piece to 'select piece'.

        Parameters
        ----------
        piece : experimentNao.chess_game.graphic_board.graphic_chess_pieces.GraphicPiece
        position_on_board : lib.util.Point
        new_state : str
        """
        if piece.position_in_board != position_on_board:    # Deactivate/Reactivate buttons of the other pieces
            piece.button["state"] = new_state               # Choose: NORMAL, DISABLED
        else:                                               # Configure command of button of selected position
            if new_state == tk.DISABLED:
                piece.button.configure(command=lambda: self.button_unselect_piece(position_on_board))
            elif new_state == tk.NORMAL:
                piece.button.configure(command=lambda: self.button_select_piece(position_on_board))

    def button_make_move(self, move):
        """ command of the button that is run when player clicks on a move (after a piece had been previously selected)

        Parameters
        ----------
        move : chess.Move
        """
        if str(move) == str(self.chess_engine.ideal_move):
            self.main_window.replace_instruction_in_side_screen('Well done')
            self.chess_engine.apply_move(move)
            self.re_draw_board()
            if self.chess_engine.board.outcome() is not None:       # if it's a checkmate
                if self.chess_engine.board.outcome().termination.name == 'CHECKMATE':
                    p = self.chess_engine.get_location_of_piece('k',
                                                                'w' if self.chess_engine.computer_color_white else 'b')
                    self.highlight_cell(self.convert_chess_pos_into_board_index(p), color='red')
        else:
            self.main_window.replace_instruction_in_side_screen('Try again! Choose your best move!')
            self.button_unselect_piece(self.convert_move_into_board_indices(move, end=False))
            self.chess_engine.number_wrong_attempts_in_move += 1

    def re_draw_board(self):
        """ draws the chess board again. To do that, removes all the buttons and images from the canvas, and draws
        the pieces from the board engine. Useful after performing a move.

        """
        self.remove_all_buttons()
        self.clear_all_images_and_buttons()     # clear current board
        self.draw_pieces_from_board_engine()    # draw board after the move

    def highlight_move(self, move, color='green'):
        """ highlights a move

        Parameters
        ----------
        move : str
        color: str
        """
        start_position, end_position = self.convert_move_into_board_indices(move)
        self.highlight_cell(start_position, color=color)                       # show highlight on current pos
        self.delete_highlights(time_=0.5)                                   # hold for a bit, and delete
        self.highlight_cell(start_position, time_delay=0.2, color=color)  # hold for a bit & show again: to create flashy effect
        self.delete_highlights(time_=0.2, show_immediately=False)           # hold for a bit, and delete
        self.highlight_cell(end_position, show_immediately=False, color=color)

    def highlight_cell(self, cell_position, show_immediately=True, color='green', time_delay=None):
        """ Highlights a cell with a green contour. Can be shown immediately or not, and.

        Parameters
        ----------
        time_delay : Union[float, None]
            in case there is the need to delay drawing the cell
        cell_position : Union[str, lib.util.Point]
        show_immediately : bool
            whether the highlight is shown immediately, or only once window is updated again
        color: str
            color of the highlight
        """
        if time_delay is None:      # default
            self.draw_cell(cell_position, fill='', outline=color, bd=3, tags='highlight')
        else:
            self.canvas.after(int(time_delay*1000),
                              self.draw_cell(cell_position, fill='', outline=color, bd=3, tags='highlight'))
        if show_immediately:
            self.main_window.update()

    def delete_highlights(self, show_immediately=True, time_=0.5):
        """ Deletes all the highlights after 'time_' seconds

        Parameters
        ----------
        time_ : float
            time before highlight is deleted
        show_immediately : bool
            whether the highlight is shown immediately, or only once window is updated again
        """
        # time.sleep(time_)
        self.canvas.after(int(time_*1000), self.canvas.delete('highlight'))     # time should be in ms
        if show_immediately:
            self.main_window.update()

    @staticmethod
    def get_color_of_square(position):
        """ get color of square based on the index (x, y)

        Parameters
        ----------
        position : position of square

        Returns
        -------
        string that defined whether cell should be light ('l') or dark ('d')
        """
        return 'l' if (position.x + position.y) % 2 == 0 else 'd'

    def remove_all_buttons(self):
        """ removes all the buttons from the board, according to the list of graphic pieces

        """
        for piece in self.list_of_graphic_pieces:
            if piece.button is not None:
                piece.remove_button()

    def clear_all_images_and_buttons(self):
        """ clears all images and buttons from the canvas

        """
        self.create_grid_for_figures()
        self.list_of_graphic_pieces = []

    def get_piece_fig_from_grid(self, position):
        """ returns a GraphicPiece from the grid of pieces in their position on the board

        Parameters
        ----------
        position : lib.util.Point

        Returns
        -------
        Union[List, experimentNao.chess_game.graphic_board.graphic_chess_pieces.GraphicPiece]
        """
        return self.figures_grid[position.x][position.y]

    def create_grid_for_figures(self):
        """ creates the grid to save all the figures objects according to their location on the board.
        This is necessary to preventing the images and buttons to disappear with tkinter. Thank you tkinter.

        """
        self.figures_grid = []
        for i in range(8):
            self.figures_grid.append([])
            for j in range(8):
                self.figures_grid[i].append([])

    def convert_board_index_into_chess_pos(self, indices):
        """ converts a position with the indices (x, y) into a chess position (e.g. 'a3' or 'g7')

        Parameters
        ----------
        indices : lib.util.Point

        Returns
        -------
        str
        """
        if self.chess_engine.computer_color_white:       # player plays with black
            return self.board_position_letters[7-indices.x] + self.board_position_numbers[7-indices.y]
        else:                                               # player plays with white
            return self.board_position_letters[indices.x] + self.board_position_numbers[indices.y]

    def convert_chess_pos_into_board_index(self, chess_position):
        """ converts a chess position (e.g. 'a3' or 'g7') into the board position with the indices (x, y) that is used
        to draw the board

        Parameters
        ----------
        chess_position : str

        Returns
        -------
        lib.util.Point
        """
        x = self.board_position_letters.index(chess_position[0])      # position[0] == letter of position
        y = self.board_position_numbers.index(chess_position[1])      # position[1] == number of position
        if self.chess_engine.computer_color_white:   # player plays with black
            return Point(7-x, 7-y)
        else:                                           # player plays with white
            return Point(x, y)

    def convert_move_into_board_indices(self, move, start=True, end=True):
        """ converts a chess move (e.g. 'a3a4' or 'g7g8') into the two board positions with the indices (x, y)
        correspondent to the starting and ending position of the move

        Parameters
        ----------
        move : chess.Move
        start : bool
        end : bool

        Returns
        -------
        lib.util.Point
        """
        if start:
            starting_pos = self.convert_chess_pos_into_board_index(str(move)[0:2])
        if end:
            ending_pos = self.convert_chess_pos_into_board_index(str(move)[2:4])
        if start and end:
            return starting_pos, ending_pos
        elif start:
            return starting_pos
        else:
            return ending_pos
