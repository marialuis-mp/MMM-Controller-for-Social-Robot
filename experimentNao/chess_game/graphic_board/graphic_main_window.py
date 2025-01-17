import time

from experimentNao.chess_game.graphic_board import monitors_info
from lib import graphic_interface
from lib.util import Point
from path_config import repo_root


class MainWindowChess(graphic_interface.MainWindow):
    def __init__(self, window_size, chess_board_size, screen_number, center):
        super().__init__(window_size, screen_number, center)
        self.chess_board_size = chess_board_size
        self.side_panel_size = Point(self.window_size.x - self.chess_board_size.x, self.chess_board_size.y)
        self.colors = ColorPalette()
        self.path4img = repo_root/'experimentNao'/'chess_game'/'graphic_board'/'pieces_figures'
        # Types of texts:
        self.texts = [None] * 3       # 0: instruction    # 1: what colour to play    # 2: ask for help
        self.instruction = Instruction4Player('Helvetica 20 bold', 'Choose your best move!',
                                              y_pos=self.window_size.y * 0.2, tag=0)
        self.player_color = Instruction4Player('Helvetica 18', 'You play with ',
                                               y_pos=self.window_size.y * 0.4, tag=1)
        self.ask_for_help = Instruction4Player('Helvetica 18', 'You can ask for a hint!',
                                               y_pos=self.window_size.y * 0.8, tag=2)

    def draw_side_panel(self, chess_engine, puzzle_counter, button_mic_command=None, button_request_command=None,
                        canvas_id=1):
        self.add_canvas(self.side_panel_size, pack_side='left', color=self.colors.very_dark)
        self.add_counter(canvas_id, puzzle_counter, txt_color='white')
        player_color = 'black' if chess_engine.computer_color_white else 'white'
        self.add_instruction_to_side_screen(self.instruction)
        self.add_instruction_to_side_screen(self.player_color, 'You play with ' + player_color + '.', player_color)
        self.add_instruction_to_side_screen(self.ask_for_help)
        self.add_image_to_side_screen('Chess_k' + ('d' if player_color == 'black' else 'l') + 's45.svg.png',
                                      int(self.side_panel_size.x/5), self.player_color.y_pos * 1.3)
        button_pos = Point(self.side_panel_size.x * 0.75, self.window_size.y * 0.9)
        if button_request_command is not None:
            self.add_button_to_side_screen('Request', pos=button_pos, bd=5, command=button_request_command,
                                           font_size=13, bg_color='orange')
        elif button_mic_command is not None:
            self.add_button_to_side_screen('Reboot mic', pos=button_pos, bd=5, command=button_mic_command,
                                           font_size=13, bg_color='orange')

    def add_instruction_to_side_screen(self, text_type_, text=None, font_color='white'):
        if text is None:
            text = text_type_.text
        position = Point(self.side_panel_size.x/2, text_type_.y_pos)
        text = self.canvases[1].create_text(position.x, position.y, text=text, fill=font_color, font=text_type_.font)
        self.texts[text_type_.tag] = text

    def show_request_options(self, requests, button_function):
        cv, canvas_size = self.draw_pop_up_canvas(canvas_proportion=0.4)
        self.add_text_to_canvas(canvas_id=-1, text='Which request do you have?',
                                position=Point(canvas_size.x/2, canvas_size.y/3), fill='black')
        positions_buttons_x = self.equally_distribute_positions(len(requests) + 1, canvas_size.x, 0.2, 0.2)
        for i in range(len(requests)):
            self.add_button_to_canvas(-1, requests[i].txt_button, active_bg_color=self.colors.very_light,
                                      position=Point(positions_buttons_x[i] - 70, canvas_size.y * (2 / 3)),
                                      command=lambda id_=i: button_function(id_), font_size=13)
        # exit button
        self.add_button_to_canvas(-1, 'Cancel request', active_bg_color=self.colors.very_light,
                                  position=Point(positions_buttons_x[-1] - 40, canvas_size.y * (2 / 3)),
                                  command=lambda id_=None: button_function(id_), font_size=13)

    def add_button_to_side_screen(self, text, pos, bd=2, pad_x=0, command=None, font_size=10, bg_color='white',
                                  active_bg_color='grey'):
        return self.add_button_to_canvas(1, text, pos, bd, command, font_size, pad_x,
                                         bg_color=bg_color, active_bg_color=active_bg_color)

    def add_image_to_side_screen(self, img_name, img_size, y_pos):
        self.draw_image_in_canvas(self.path4img/img_name, img_size, Point(self.side_panel_size.x/2, y_pos), 1)

    def replace_instruction_in_side_screen(self, text, text_type=None):
        if text_type is None:
            text_type = self.instruction
        self.canvases[1].delete(self.texts[text_type.tag])
        self.add_instruction_to_side_screen(text_type, text)

    @staticmethod
    def equally_distribute_positions(number_of_objects, overall_size, pad_top_percentage=0.05,
                                     pad_bottom_percentage=0.05):
        positions = []
        pad_top = overall_size * pad_top_percentage             # default pad on top/left is 10% of size
        pad_bottom = overall_size * pad_bottom_percentage       # default pad on bottom/right is 0% of size
        for i in range(number_of_objects):
            positions.append((overall_size - pad_top - pad_bottom) * i / (number_of_objects - 1) + pad_top)
        return positions

    def delete_all_lists(self):
        super().delete_all_lists()
        self.texts = [None] * 3

    def add_counter(self, canvas_id, puzzle_counter, txt_color):
        counter_txt = 'Played puzzles: ' + str(puzzle_counter)
        self.add_text_to_canvas(canvas_id, counter_txt, Point(self.side_panel_size.x-len(counter_txt)*5-10, 30),
                                fill=txt_color)

    def draw_pop_up_canvas(self, canvas_proportion, bg_color=None, border_color=None, border_len=5):
        bg_color = self.colors.very_light if bg_color is None else bg_color
        border_color = self.colors.very_dark if border_color is None else border_color
        return super().draw_pop_up_canvas(canvas_proportion, bg_color, border_color, border_len)


class ColorPalette:
    def __init__(self):
        self.very_light = '#EDBB99'
        self.light = '#ffce9e'
        self.dark = '#d18b47'
        self.very_dark = '#7c644c'


class Instruction4Player:
    def __init__(self, font, text, y_pos, tag):
        self.font = font
        self.y_pos = y_pos
        self.tag = tag
        self.text = text
