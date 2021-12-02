import struct
import socket
from PIL import ImageGrab
from cv2 import cv2
import numpy as np
import threading
import time
import pyautogui as ag
import mouse
from ._keyboard import getKeycodeMapping

# 画面周期
IDLE = 0.05

# 鼠标滚轮灵敏度
SCROLL_NUM = 5

bufsize = 1024

host = ('0.0.0.0', 80)
soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
soc.bind(host)
soc.listen(1)
# 压缩比 1-100 数值越小，压缩比越高，图片质量损失越严重
IMQUALITY = 50

lock = threading.Lock()

# if sys.platform == "win32":
#     from ._keyboard_win import keycodeMapping
# elif platform.system() == "Linux":
#     from ._keyboard_x11 import keycodeMapping
# elif sys.platform == "darwin":
#     from ._keyboard_osx import keycodeMapping


def ctrl(conn):
    '''
    读取控制命令，并在本机还原操作
    '''
    keycodeMapping = {}
    def Op(key, op, ox, oy):
        # print(key, op, ox, oy)
        if key == 4:
            # 鼠标移动
            mouse.move(ox, oy)
        elif key == 1:
            if op == 100:
                # 左键按下
                ag.mouseDown(button=ag.LEFT)
            elif op == 117:
                # 左键弹起
                ag.mouseUp(button=ag.LEFT)
        elif key == 2:
            # 滚轮事件
            if op == 0:
                # 向上
                ag.scroll(-SCROLL_NUM)
            else:
                # 向下
                ag.scroll(SCROLL_NUM)
        elif key == 3:
            # 鼠标右键
            if op == 100:
                # 右键按下
                ag.mouseDown(button=ag.RIGHT)
            elif op == 117:
                # 右键弹起
                ag.mouseUp(button=ag.RIGHT)
        else:
            k = keycodeMapping.get(key)
            if k is not None:
                if op == 100:
                    ag.keyDown(k)
                elif op == 117:
                    ag.keyUp(k)
    try:
        plat = b''
        while True:
            plat += conn.recv(3-len(plat))
            if len(plat) < 3:
                break
        print("Plat:", plat.decode())
        keycodeMapping = getKeycodeMapping(plat)
        base_len = 6
        while True:
            cmd = b''
            rest = base_len - 0
            while rest > 0:
                cmd += conn.recv(rest)
                rest -= len(cmd)
            key = cmd[0]
            op = cmd[1]
            x = struct.unpack('>H', cmd[2:4])[0]
            y = struct.unpack('>H', cmd[4:6])[0]
            Op(key, op, x, y)
    except:
        return


# 压缩后np图像
img = None
# 编码后的图像
imbyt = None


def handle(conn):
    global img, imbyt
    lock.acquire()
    if imbyt is None:
        imorg = np.asarray(ImageGrab.grab())
        _, imbyt = cv2.imencode(
            ".jpg", imorg, [cv2.IMWRITE_JPEG_QUALITY, IMQUALITY])
        imnp = np.asarray(imbyt, np.uint8)
        img = cv2.imdecode(imnp, cv2.IMREAD_COLOR)
    lock.release()
    lenb = struct.pack(">BI", 1, len(imbyt))
    conn.sendall(lenb)
    conn.sendall(imbyt)
    while True:
        # fix for linux
        time.sleep(IDLE)
        gb = ImageGrab.grab()
        imgnpn = np.asarray(gb)
        _, timbyt = cv2.imencode(
            ".jpg", imgnpn, [cv2.IMWRITE_JPEG_QUALITY, IMQUALITY])
        imnp = np.asarray(timbyt, np.uint8)
        imgnew = cv2.imdecode(imnp, cv2.IMREAD_COLOR)
        # 计算图像差值
        imgs = imgnew - img
        if (imgs != 0).any():
            # 画质改变
            pass
        else:
            continue
        imbyt = timbyt
        img = imgnew
        # 无损压缩
        _, imb = cv2.imencode(".png", imgs)
        l1 = len(imbyt)  # 原图像大小
        l2 = len(imb)  # 差异图像大小
        if l1 > l2:
            # 传差异化图像
            lenb = struct.pack(">BI", 0, l2)
            conn.sendall(lenb)
            conn.sendall(imb)
        else:
            # 传原编码图像
            lenb = struct.pack(">BI", 1, l1)
            conn.sendall(lenb)
            conn.sendall(imbyt)


while True:
    conn, addr = soc.accept()
    threading.Thread(target=handle, args=(conn,)).start()
    threading.Thread(target=ctrl, args=(conn,)).start()
