#    Copyright (C) 2020-2024  SWD Studio

#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#     any later version.

#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <https://www.gnu.org/licenses/>.
#    You can contact us on <http://swdstudio.github.com>.

# ui 快闪界面

from tkinter import *  # @UnusedWildImport
from tkinter.ttk import *  # @UnusedWildImport
from PIL import Image, ImageTk

def create():
    global splash_win, img_tk
    splash_win = Toplevel()  # 创建一个Tkinter窗口实例
    splash_win.title("启动画面范例")  # 设置窗口标题
    img_dir = './icons/snapshot.jpg'
    img_open = Image.open(img_dir)
    max_size = (767 // 2, 432 // 2)  # 设置最大尺寸
    img_open.thumbnail(max_size)  # 使用 thumbnail() 方法创建缩略图
    width, height = img_open.width, img_open.height  # 定义窗口或框架的大小
    screen_width = splash_win.winfo_screenwidth()
    screen_height = splash_win.winfo_screenheight()
    x = (screen_width - width) / 2
    y = (screen_height - height) / 2
    splash_win.geometry(f"{width}x{height}+{int(x)}+{int(y)}")
    splash_win.overrideredirect(True)  # 去除启动画面边框# 定义窗口内容
    # img_open.show()
    img_tk = ImageTk.PhotoImage(img_open)
    splash_label = Label(splash_win, image=img_tk)
    splash_label.place(x=-2, y=-2)
    splash_win.update()


# 启动画面计时器
# splash_win.after(5000, mainWin)
def delete() -> None:
    try:
        splash_win.destroy()
    except Exception:
        ...



if __name__ == '__main__':
    create()
    splash_win.mainloop()
else:
    create()