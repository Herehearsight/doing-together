from pyautogui import screenshot
from datetime import datetime
from threading import Thread, Event
from json import load, dumps, dump
from requests import post
from pynput import mouse
from PIL import Image
from pystray import Icon
from pystray import MenuItem as item
from tkinter import filedialog, Tk, Label, Button, StringVar, Frame, Entry, W, PhotoImage
from os import path, mkdir
from sys import argv

folder_current_path = path.dirname(path.realpath(argv[0]))
stop_event = Event()

with open('config.json', 'r') as file:
    conf = load(file)
    if not conf['pic_save_path']:
        conf['pic_save_path'] = folder_current_path + '\\pic'
    if not path.exists(folder_current_path + '\\pic'):
        mkdir(folder_current_path + '\\pic')


class MouseMonitor:
    def __init__(self):
        self.mouse = mouse.Controller()
        self.last_click_time = 0
        self.TIME_THRESHOLD = 0.3

    def scree(self):
        def sub_scree():
            pic_name = conf['name'] + '-' + datetime.now().strftime("%Y%m%d-%H%M%S") + '.png'
            screenshot().save(conf['pic_save_path'] + '\\' + pic_name)

            with open(conf['pic_save_path'] + '\\' + pic_name, "rb") as image_file:
                image_data = image_file.read()

            data = {
                "username": conf['name'],
                "filename": pic_name
            }
            response = post("http://%s:%s/upload" % (conf['ip'], conf['port']), files={"image": image_data},
                                     data={"data": dumps(data)})
            # print(response.text)
        Thread(target=sub_scree).start()

    def on_double_click(self, x, y, button, pressed):
        if stop_event.is_set():
            return False
        if pressed and button == mouse.Button.left:
            current_time = datetime.now().timestamp()
            if current_time - self.last_click_time < self.TIME_THRESHOLD:
                self.scree()
            self.last_click_time = current_time

    def join_mou(self):
        l = mouse.Listener(on_click=self.on_double_click)
        l.start()
        # l.join()

    def start_mou(self):
        stop_event.clear()
        self.join_mou()

    def stop_mou(self):
        stop_event.set()

class TableUI:
    def __init__(self, master):
        self.bt_run = None
        self.mou = MouseMonitor()
        self.master = master
        self.master.title("Doing together client")
        self.master.wm_iconphoto(True, PhotoImage(file='icon.png'))

        self.labels = []
        self.entries = []
        self.pic_save_path = StringVar()
        self.pic_save_path.set(conf['pic_save_path'])
        self.name = StringVar()
        self.name.set(conf['name'])
        self.ip = StringVar()
        self.ip.set(conf['ip'])
        self.port = StringVar()
        self.port.set(conf['port'])

        self.layout()

    def layout(self):
        row = 0
        Label(self.master, text='保存图片').grid(row=row, column=0)
        f_pic_save = Frame(self.master)
        f_pic_save.grid(row=row, column=1, sticky=W)
        Entry(f_pic_save, textvariable=self.pic_save_path, width=50).grid(row=0, column=0, sticky=W)
        Button(f_pic_save, text="选择文件夹", command=lambda: self.pic_save_path.set(filedialog.askdirectory())).grid(row=0, column=1, sticky=W)

        row += 1
        Label(self.master, text='用户名').grid(row=row, column=0)
        f_name = Frame(self.master)
        f_name.grid(row=row, column=1, sticky=W)
        Entry(f_name, textvariable=self.name, width=20).grid(row=0, column=0, sticky=W)

        row += 1
        Label(self.master, text='连接服务器').grid(row=row, column=0)
        f_ip = Frame(self.master)
        f_ip.grid(row=row, column=1, sticky=W)
        Entry(f_ip, textvariable=self.ip, width=20).grid(row=0, column=0, sticky=W)
        Label(f_ip, text=' : ').grid(row=0, column=1)
        Entry(f_ip, textvariable=self.port, width=10).grid(row=0, column=2)

        row += 1
        f_but = Frame(self.master)
        f_but.grid(row=row, column=1, sticky=W)
        Button(f_but, text="更新配置", command=self.save_conf).grid(row=0, column=0)
        Label(f_but, text='', width=30).grid(row=0, column=1)
        self.bt_run = Button(f_but, text="点击启动", command=self.start_op)
        self.bt_run.grid(row=0, column=2)

    def save_conf(self):
        global conf
        conf['pic_save_path'] = self.pic_save_path.get()
        conf['name'] = self.name.get()
        conf['ip'] = self.ip.get()
        conf['port'] = self.port.get()
        with open('config.json', 'w') as file:
            dump(conf, file, indent=4)
        if not path.exists(self.pic_save_path.get()):
            try:
                mkdir(self.pic_save_path.get())
            except Exception as e:
                pass

    def start_op(self):
        t = self.bt_run.cget('text')
        if t == '点击启动':
            self.mou.start_mou()
            self.bt_run.config(text='点击停止')
        if t == '点击停止':
            self.mou.stop_mou()
            self.bt_run.config(text='点击启动')

# 最小化窗口到托盘
def hide_window():
    root.withdraw()
    show_icon()


# 从托盘显示窗口
def show_window(icon, item):
    icon.stop()
    root.deiconify()


# 退出应用程序
def exit_app(icon, item):
    icon.stop()
    stop_event.set()
    root.destroy()


# 创建系统托盘图标
def show_icon():
    image = Image.open("icon.png")
    menu = (item('Show', show_window), item('Exit', exit_app))
    icon = Icon("name", image, "Doing together", menu)
    icon.run()


if __name__ == "__main__":
    root = Tk()
    app = TableUI(root)
    root.protocol("WM_DELETE_WINDOW", hide_window)
    root.mainloop()
