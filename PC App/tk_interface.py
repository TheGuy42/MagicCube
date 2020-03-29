import tkinter as tk
from tkinter import messagebox
from configuration import GUIConfig


class GUI:

    def __init__(self, title="MagicCube", TopLevel=False, exit_protocol=None):
        if TopLevel:
            self.master = tk.Toplevel()
        else:
            self.master = tk.Tk()
        self.master.title(title)
        self.master.configure(background=GUIConfig.WindowBG)
        if exit_protocol is not None:
            self.master.protocol('WM_DELETE_WINDOW', exit_protocol)

    def Button(self, text, func, **style):
        tmp = tk.Button(self.master, text=text, command=func)
        tmp.configure(style)

        return tmp

    def Entry(self, **style):
        tmp = tk.Entry(self.master)
        tmp.configure(style)
        return tmp

    def Label(self, text, **style):
        tmp = tk.Label(master=self.master, text=text)
        tmp.configure(style)
        return tmp

    def get_image(self, path):
        return tk.PhotoImage(file=path)

    # close the GUI
    def destroy(self):
        self.master.destroy()


