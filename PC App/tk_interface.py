import tkinter as tk
import tkinter.colorchooser as tkColor
from tkinter import messagebox
from configuration import GUIConfig


class GUI:

    def __init__(self, style=GUIConfig.Main_Window, title="MagicCube", TopLevel=False, exit_protocol=None):
        if TopLevel:
            self.master = tk.Toplevel()
        else:
            self.master = tk.Tk()

        self.Style = style
        self.master.title(title)
        self.master.configure(background=self.Style.WindowBG)
        if exit_protocol is not None:
            self.master.protocol('WM_DELETE_WINDOW', exit_protocol)

    # return master, or passed value if not none
    def _master(self, master):
        if master is None:
            return self.master
        return master

    # makes the window stretch correctly
    def make_stretchy(self, weight=1, master=None, make_row=True, make_column=True):
        column_num, row_num = self._master(master).grid_size()
        if make_row:
            for row in range(row_num):
                self._master(master).rowconfigure(row, weight=weight)
        if make_column:
            for column in range(column_num):
                self._master(master).columnconfigure(column, weight=weight)

    # return size of window, main by default
    def get_size(self, master=None):
        self.master.update()
        return self._master(master).winfo_width(), self._master(master).winfo_height()

    # return the grid size of the window(default) or container widget
    def get_grid_size(self, master=None):
        return self._master(master).grid_size()

    # set fixed size of the window(or widget)
    def fix_size(self, width=None, height=None):
        self.master.update()
        if width is None or height is None:
            self.master.minsize(self.master.winfo_width(), self.master.winfo_height())
        else:
            self.master.minsize(width, height)

    def Frame(self, master=None):
        tmp = tk.Frame(master=self._master(master))
        tmp.configure(**self.Style.Frame)
        return tmp

    def Button(self, text, func, master=None):
        tmp = tk.Button(self._master(master), text=text, command=func)
        tmp.configure(**self.Style.Button)

        return tmp

    def Entry(self, master=None):
        tmp = tk.Entry(self._master(master))
        tmp.configure(**self.Style.Entry)
        return tmp

    def Label(self, text, master=None):
        tmp = tk.Label(master=self._master(master), text=text)
        tmp.configure(**self.Style.Label)
        return tmp

    def Listbox(self, master=None):
        tmp = tk.Listbox(master=self._master(master))
        tmp.configure(**self.Style.Listbox)
        return tmp

    def DropDown(self, text, master=None):
        tmp = tk.Menubutton(master=self._master(master), text=text)
        tmp.configure(**self.Style.DropDown)
        return tmp

    def Menu(self, master=None):
        tmp = tk.Menu(master=self._master(master), tearoff=0)
        tmp.configure(**self.Style.DropDown)
        return tmp

    def Color_Picker(self, color, master=None):
        return tkColor.askcolor(color, parent=self._master(master))

    def get_image(self, path):
        return tk.PhotoImage(file=path)

    # close the GUI
    def destroy(self):
        self.master.destroy()
