from tkinter import Tk, Label,PhotoImage,Button
import os
import sys
from subprocess import Popen
class TableUI:
    def __init__(self, master):
        self.bt_run = None
        self.master = master
        self.master.geometry("300x50")
        self.master.title("Doing together serve")
        self.master.wm_iconphoto(True, PhotoImage(file='icon.png'))
        self.layout()

    def layout(self):
        Label(self.master, text='服务器运行中...', width=30).grid(row=0, column=0)
        Button(self.master, text="用户管理", command=lambda: os.startfile(os.path.dirname(os.path.realpath(sys.argv[0])) + '/static/images')).grid(row=0, column=1)


if __name__ == "__main__":
    Popen(['cmd', '/c', 'python flasker.py'], )
    root = Tk()
    app = TableUI(root)
    root.mainloop()
