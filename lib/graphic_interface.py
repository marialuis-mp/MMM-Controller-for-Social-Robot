from tkinter import *
from PIL import ImageTk, Image

from experimentNao.chess_game.graphic_board import monitors_info
from lib import util
from tkinter import messagebox


class MainWindow:
    def __init__(self, window_size, screen_number=None, center=False):
        self.root = Tk()
        self.window_size = window_size
        self.default_font = 'Helvetica'
        self.default_font_size = '15'
        start_point = self.get_screen_coordinates(screen_number=screen_number, center=center)
        self.root.geometry(str(self.window_size.x) + 'x' + str(self.window_size.y) + '+' +
                           str(start_point.x) + '+' + str(start_point.y))
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.canvases = []
        self.frames = []
        self.texts = []
        self.buttons = []
        self.images = []
        self.message_box = None

    def update(self):
        self.root.update_idletasks()
        self.root.update()

    def clear_window(self):
        """ remove all the widgets from the window

        """
        for ele in self.root.winfo_children():
            ele.destroy()
        self.delete_all_lists()

    def close_window(self):
        self.root.destroy()

    def add_canvas(self, canvas_size, pack_side=LEFT, color='white', bd=0, border_len=0, border_colour='black'):
        my_canvas = Canvas(self.root, bg=color, width=canvas_size.x, height=canvas_size.y, bd=bd,
                           highlightthickness=border_len, highlightbackground=border_colour)
        my_canvas.pack(side=pack_side)
        self.canvases.append(my_canvas)
        return my_canvas

    def clear_canvas(self, canvas_id=-1):
        self.canvases[canvas_id].delete('all')

    def remove_canvas(self, canvas_id=-1):
        # for child in self.canvases[canvas_id].children.values():
        #     if isinstance(child, Button):
        #         child.place_forget()
        # self.canvases[canvas_id].delete('all')
        # self.canvases[canvas_id].pack_forget()
        self.canvases[canvas_id].destroy()
        del self.canvases[canvas_id]
        self.root.update()

    def add_text_to_canvas(self, canvas_id, text, position, font_=None, fill='black', bold=False):
        if font_ is None:
            font_ = self.default_font + ' ' + self.default_font_size
        if bold:
            font_ += ' bold'
        text = self.canvases[canvas_id].create_text(position.x, position.y, text=text, fill=fill, font=font_)
        self.texts.append(text)

    def add_button_to_canvas(self, canvas_id, text, position, bd=2, command=None, font_size=10, pad_x=0, pad_y=0,
                             bg_color='grey', active_bg_color='grey', foreground='black', disabled_foreground='white'):
        button = Button(self.canvases[canvas_id], text=text, bd=bd, padx=pad_x, pady=pad_y, command=command, bg=bg_color,
                        font=self.default_font + ' ' + str(font_size), activebackground=active_bg_color,
                        foreground=foreground, disabledforeground=disabled_foreground)
        button.place(x=position.x, y=position.y)
        self.buttons.append(button)
        return button

    def replace_text_in_canvas(self, canvas_id, text, position):
        self.clear_canvas(canvas_id)
        self.add_text_to_canvas(canvas_id, text, position)

    def add_frame(self, pack_side=None):
        frame = Frame(self.root)
        if pack_side is None:
            frame.pack()
        else:
            frame.pack(side=pack_side)
        self.frames.append(frame)
        return frame

    def add_label_to_frame(self, frame_number, text, pack_side=TOP, bg='white', font_=None):
        if font_ is None:
            font_ = self.default_font + ' ' + self.default_font_size
        text_label = Label(self.frames[frame_number], text=text, bd=1, font=font_, bg=bg, padx=0, pady=20)
        text_label.pack(side=pack_side, pady=20, padx=20)
        return text_label

    def draw_image_in_canvas(self, img_name, img_size, position_on_canvas, canvas_id):
        img = ImageTk.PhotoImage(Image.open(img_name).resize((img_size, img_size)))
        self.canvases[canvas_id].create_image(position_on_canvas.x, position_on_canvas.y, image=img)
        self.images.append(img)
        return img

    def draw_pop_up_canvas(self, canvas_proportion, bg_color, border_color, border_len=5):
        canvas_size = self.window_size * canvas_proportion
        canvas = self.add_canvas(canvas_size - util.Point(border_len, border_len)*2, color=bg_color, bd=0,
                                 border_len=border_len, border_colour=border_color)
        canvas_location = (self.window_size - canvas_size) * 0.5
        canvas.place(x=canvas_location.x, y=canvas_location.y)
        return canvas, canvas_size

    def make_message_box_for_request(self, title, message):
        self.message_box = messagebox.showinfo(title=title, message=message)
        return self.message_box

    def ask_question(self, title, message):
        self.message_box = messagebox.askyesno(title=title, message=message)
        return self.message_box

    def delete_all_lists(self):
        self.canvases = []
        self.frames = []
        self.texts = []
        self.buttons = []
        self.images = []

    def on_closing(self):
        if messagebox.askokcancel("Quit", "Do you want to quit?"):
            self.root.destroy()

    def get_screen_coordinates(self, screen_number=None, center=True):
        if screen_number is None:   # default screen
            screen_size = util.Point(self.root.winfo_screenwidth(), self.root.winfo_screenheight())
            start_point = util.Point(0, 0)
        else:
            screens = monitors_info.monitor_areas()
            screen = screens[screen_number]
            start_point = util.Point(screen[0], screen[1])
            screen_size = util.Point(screen[2] - screen[0], screen[3] - screen[1])
        self.window_size.x = min(self.window_size.x, screen_size.x)
        self.window_size.y = min(self.window_size.y, screen_size.y)
        if center:
            start_point += util.Point(int((screen_size.x - self.window_size.x) / 2),
                                      int((screen_size.y - self.window_size.y) / 2))
        return start_point
