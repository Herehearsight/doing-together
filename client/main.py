import re
import pyautogui
from datetime import datetime
from threading import Thread, Event

import json
import requests
from pynput import mouse
from PIL import Image
import pystray
from pystray import MenuItem as item
import tkinter as tk
from tkinter import filedialog
import os

folder_current_path = '\\'.join(os.path.abspath(__file__).split('\\')[:-1])
stop_event = Event()

with open('config.json', 'r') as file:
    conf = json.load(file)
    if not conf['pic_save_path']:
        conf['pic_save_path'] = folder_current_path + '\\pic'
    # print(conf)


class MouseMonitor:
    def __init__(self):
        self.mouse = mouse.Controller()
        self.xy = [(0, 0)]

    def scree(self):
        # 截取整个屏幕
        screenshot = pyautogui.screenshot()
        # print(screenshot)
        d = datetime.now()
        pic_name = conf['name'] + '-' + '-'.join(re.findall(r'\d+', str(d))[:-1]) + '.png'
        screenshot.save(conf['pic_save_path'] + '\\' + pic_name)

        # # 读取图片文件为二进制数据
        with open(conf['pic_save_path'] + '\\' + pic_name, "rb") as image_file:
            image_data = image_file.read()

        # 创建包含用户名和文件名的 JSON 数据
        data = {
            "username": conf['name'],
            "filename": pic_name
        }

        # 发送 POST 请求，包含图片文件和 JSON 数据
        response = requests.post("http://%s:%s/upload" % (conf['ip'], conf['port']), files={"image": image_data},
                                 data={"data": json.dumps(data)})

        print(response.text)

    def on_click(self, x, y, button, pressed):
        # 在鼠标点击时被调用
        if stop_event.is_set():
            return False
        # 这里可以添加你想要执行的代码
        action = "Pressed" if pressed else "Released"
        # print(f"Mouse {action} at ({x}, {y}) with {button}")
        # print(button.name, button.value)
        if button.name == 'left' and pressed:
            self.xy.append((x, y))
            # print(self.xy)
            if len(self.xy) >= 2:
                x1, y1 = self.xy[-1]
                x2, y2 = self.xy[-2]
                if abs(x1 - x2) < 5 and abs(y1 - y2) < 5:
                    self.xy = [(0, 0)]
                    self.scree()

    def join_mou(self):
        # 监听鼠标事件
        with mouse.Listener(on_click=self.on_click) as l:
            l.join()

    def start_mou(self):
        stop_event.clear()
        Thread(target=self.join_mou).start()

    def stop_mou(self):
        stop_event.set()


class TableUI:
    def __init__(self, master):
        self.bt_run = None
        self.mou = MouseMonitor()
        self.master = master
        self.master.title("表格布局示例")

        # 创建标签和输入框的列表
        self.labels = []
        self.entries = []
        self.pic_save_path = tk.StringVar()
        self.pic_save_path.set(conf['pic_save_path'])
        self.name = tk.StringVar()
        self.name.set(conf['name'])
        self.ip = tk.StringVar()
        self.ip.set(conf['ip'])
        self.port = tk.StringVar()
        self.port.set(conf['port'])

        self.layout()

    def layout(self):
        if not os.path.exists(self.pic_save_path.get()):
            try:
                os.mkdir(self.pic_save_path.get())
            except Exception as e:
                pass
        row = 0
        tk.Label(self.master, text='保存图片').grid(row=row, column=0)
        f_pic_save = tk.Frame(self.master)
        f_pic_save.grid(row=row, column=1, sticky=tk.W)
        tk.Entry(f_pic_save, textvariable=self.pic_save_path, width=50).grid(row=0, column=0, sticky=tk.W)
        tk.Button(f_pic_save, text="选择文件夹",
                  command=lambda: self.pic_save_path.set(filedialog.askdirectory())).grid(row=0, column=1, sticky=tk.W)

        row += 1
        tk.Label(self.master, text='用户名').grid(row=row, column=0)
        f_name = tk.Frame(self.master)
        f_name.grid(row=row, column=1, sticky=tk.W)
        tk.Entry(f_name, textvariable=self.name, width=20).grid(row=0, column=0, sticky=tk.W)

        row += 1
        tk.Label(self.master, text='连接服务器').grid(row=row, column=0)
        f_ip = tk.Frame(self.master)
        f_ip.grid(row=row, column=1, sticky=tk.W)
        tk.Entry(f_ip, textvariable=self.ip, width=20).grid(row=0, column=0, sticky=tk.W)
        tk.Label(f_ip, text=' : ').grid(row=0, column=1)
        tk.Entry(f_ip, textvariable=self.port, width=10).grid(row=0, column=2)

        row += 1
        f_but = tk.Frame(self.master)
        f_but.grid(row=row, column=1, sticky=tk.W)
        tk.Button(f_but, text="更新配置", command=self.save_conf).grid(row=0, column=0)
        tk.Label(f_but, text='    ').grid(row=0, column=1)
        self.bt_run = tk.Button(f_but, text="点击启动", command=self.start_op)
        self.bt_run.grid(row=0, column=2)

    def save_conf(self):
        global conf
        data = {}
        data['pic_save_path'] = self.pic_save_path.get()
        data['name'] = self.name.get()
        data['ip'] = self.ip.get()
        data['port'] = self.port.get()
        with open('config.json', 'w') as file:
            json.dump(data, file, indent=4)
        with open('config.json', 'r') as file:
            conf = json.load(file)
        if not os.path.exists(self.pic_save_path.get()):
            try:
                os.mkdir(self.pic_save_path.get())
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


# 创建主窗口
def create_window():
    root = tk.Tk()
    root.title("Temperature Predictor")
    root.geometry("300x200")

    label = tk.Label(root, text="Temperature Prediction App")
    label.pack(pady=20)

    button = tk.Button(root, text="Close to Tray", command=hide_window)
    button.pack(pady=10)

    return root


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
    root.destroy()


# 创建系统托盘图标
def show_icon():
    image = Image.open("icon.png")  # 替换为你的图标路径
    menu = (item('Show', show_window), item('Exit', exit_app))
    icon = pystray.Icon("name", image, "Temperature Predictor", menu)
    icon.run()


# 主程序
if __name__ == "__main__":
    root = tk.Tk()
    app = TableUI(root)
    root.protocol("WM_DELETE_WINDOW", hide_window)  # 绑定关闭事件
    root.mainloop()
