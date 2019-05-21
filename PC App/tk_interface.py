import tkinter as tk
from tkinter import messagebox
from configuration import GUIConfig


class GUI:

    def __init__(self, title="MagicCube"):
        self.master = tk.Tk()
        self.master.title(title)
        self.master.configure(background=GUIConfig.WindowBG)
        #self.master.protocol('WM_DELETE_WINDOW',)

    def _return_master(self, passedValue):
        if passedValue is None:
            return self.master
        return passedValue

    def Button(self, text, func, master=None, bg=GUIConfig.ButtonBG, ActiveBG=GUIConfig.ButtonActiveBG,
               fg=GUIConfig.ButtonFG, ActiveFG=GUIConfig.ButtonActiveFG, bd=GUIConfig.ButtonBD, relief=GUIConfig.ButtonRelief):

        MainWindow = self._return_master(master)
        tmp = tk.Button(MainWindow, text=text, command=func)
        tmp.configure(background=bg,
                      activebackground=ActiveBG,
                      foreground=fg,
                      activeforeground=ActiveFG,
                      border=bd,
                      relief=relief)
        return tmp

    def Entry(self, master=None, bg=GUIConfig.EntryBG, fg=GUIConfig.EntryFG, bd=GUIConfig.EntryBD,
              relief=GUIConfig.EntryRelief, width=GUIConfig.EntryWidth):

        MainWindow = self._return_master(master)
        tmp = tk.Entry(MainWindow)
        tmp.configure(background=bg,
                      foreground=fg,
                      border=bd,
                      relief=relief,
                      width=width)
        return tmp

    def Lable(self, text, master=None, bg=GUIConfig.LabelBG, fg=GUIConfig.LabelFG, bd=GUIConfig.LabelBD,
              relief=GUIConfig.LabelRelief, width=GUIConfig.LabelWidth):

        MainWindow = self._return_master(master)
        tmp = tk.Label(master=MainWindow, text=text)
        tmp.configure(background=bg,
                      foreground=fg,
                      border=bd,
                      relief=relief,
                      width=width)
        return tmp

    @staticmethod
    def messagebox(title, message):
        messagebox.showinfo(title, message)


