import struct
import socket
from PIL import ImageGrab
from cv2 import cv2
import numpy as np
import threading
import time
import pyautogui as ag

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

keyboardMapping = {
    0x08: 'backspace',  # VK_BACK
    0x5B: 'super',  # VK_LWIN
    0x09: 'tab',  # VK_TAB
    0x0c: 'clear',  # VK_CLEAR
    0x0d: 'enter',  # VK_RETURN
    0x0d: 'return',  # VK_RETURN
    0x10: 'shift',  # VK_SHIFT
    0x11: 'ctrl',  # VK_CONTROL
    0x12: 'alt',  # VK_MENU
    0x13: 'pause',  # VK_PAUSE
    0x14: 'capslock',  # VK_CAPITAL
    0x15: 'kana',  # VK_KANA
    0x17: 'junja',  # VK_JUNJA
    0x18: 'final',  # VK_FINAL
    0x19: 'hanja',  # VK_HANJA
    0x1b: 'esc',  # VK_ESCAPE
    0x1c: 'convert',  # VK_CONVERT
    0x1d: 'nonconvert',  # VK_NONCONVERT
    0x1e: 'accept',  # VK_ACCEPT
    0x1f: 'modechange',  # VK_MODECHANGE
    0x20: 'space',  # VK_SPACE
    0x21: 'pgup',  # VK_PRIOR
    0x22: 'pgdn',  # VK_NEXT
    0x23: 'end',  # VK_END
    0x24: 'home',  # VK_HOME
    0x25: 'left',  # VK_LEFT
    0x26: 'up',  # VK_UP
    0x27: 'right',  # VK_RIGHT
    0x28: 'down',  # VK_DOWN
    0x29: 'select',  # VK_SELECT
    0x2a: 'print',  # VK_PRINT
    0x2b: 'execute',  # VK_EXECUTE
    0x2c: 'prtsc',  # VK_SNAPSHOT
    0x2d: 'insert',  # VK_INSERT
    0x2e: 'del',  # VK_DELETE
    0x2f: 'help',  # VK_HELP
    0x30: '0',
    0x31: '1',
    0x32: '2',
    0x33: '3',
    0x34: '4',
    0x35: '5',
    0x36: '6',
    0x37: '7',
    0x38: '8',
    0x39: '9',
    0x41: 'a',
    0x42: 'b',
    0x43: 'c',
    0x44: 'd',
    0x45: 'e',
    0x46: 'f',
    0x47: 'g',
    0x48: 'h',
    0x49: 'i',
    0x4a: 'j',
    0x4b: 'k',
    0x4c: 'l',
    0x4d: 'm',
    0x4e: 'n',
    0x4f: 'o',
    0x50: 'p',
    0x51: 'q',
    0x52: 'r',
    0x53: 's',
    0x54: 't',
    0x55: 'u',
    0x56: 'v',
    0x57: 'w',
    0x58: 'x',
    0x59: 'y',
    0x5a: 'z',
    0x5b: 'win',  # VK_LWIN
    0x5c: 'winright',  # VK_RWIN
    0x5d: 'apps',  # VK_APPS
    0x5f: 'sleep',  # VK_SLEEP
    0x60: 'num0',  # VK_NUMPAD0
    0x61: 'num1',  # VK_NUMPAD1
    0x62: 'num2',  # VK_NUMPAD2
    0x63: 'num3',  # VK_NUMPAD3
    0x64: 'num4',  # VK_NUMPAD4
    0x65: 'num5',  # VK_NUMPAD5
    0x66: 'num6',  # VK_NUMPAD6
    0x67: 'num7',  # VK_NUMPAD7
    0x68: 'num8',  # VK_NUMPAD8
    0x69: 'num9',  # VK_NUMPAD9
    0x6a: 'multiply',  # VK_MULTIPLY  ??? Is this the numpad *?
    0x6b: 'add',  # VK_ADD  ??? Is this the numpad +?
    0x6c: 'separator',  # VK_SEPARATOR  ??? Is this the numpad enter?
    0x6d: 'subtract',  # VK_SUBTRACT  ??? Is this the numpad -?
    0x6e: 'decimal',  # VK_DECIMAL
    0x6f: 'divide',  # VK_DIVIDE
    0x70: 'f1',  # VK_F1
    0x71: 'f2',  # VK_F2
    0x72: 'f3',  # VK_F3
    0x73: 'f4',  # VK_F4
    0x74: 'f5',  # VK_F5
    0x75: 'f6',  # VK_F6
    0x76: 'f7',  # VK_F7
    0x77: 'f8',  # VK_F8
    0x78: 'f9',  # VK_F9
    0x79: 'f10',  # VK_F10
    0x7a: 'f11',  # VK_F11
    0x7b: 'f12',  # VK_F12
    0x7c: 'f13',  # VK_F13
    0x7d: 'f14',  # VK_F14
    0x7e: 'f15',  # VK_F15
    0x7f: 'f16',  # VK_F16
    0x80: 'f17',  # VK_F17
    0x81: 'f18',  # VK_F18
    0x82: 'f19',  # VK_F19
    0x83: 'f20',  # VK_F20
    0x84: 'f21',  # VK_F21
    0x85: 'f22',  # VK_F22
    0x86: 'f23',  # VK_F23
    0x87: 'f24',  # VK_F24
    0x90: 'numlock',  # VK_NUMLOCK
    0x91: 'scrolllock',  # VK_SCROLL
    0xa0: 'shiftleft',  # VK_LSHIFT
    0xa1: 'shiftright',  # VK_RSHIFT
    0xa2: 'ctrlleft',  # VK_LCONTROL
    0xa3: 'ctrlright',  # VK_RCONTROL
    0xa4: 'altleft',  # VK_LMENU
    0xa5: 'altright',  # VK_RMENU
    0xa6: 'browserback',  # VK_BROWSER_BACK
    0xa7: 'browserforward',  # VK_BROWSER_FORWARD
    0xa8: 'browserrefresh',  # VK_BROWSER_REFRESH
    0xa9: 'browserstop',  # VK_BROWSER_STOP
    0xaa: 'browsersearch',  # VK_BROWSER_SEARCH
    0xab: 'browserfavorites',  # VK_BROWSER_FAVORITES
    0xac: 'browserhome',  # VK_BROWSER_HOME
    0xad: 'volumemute',  # VK_VOLUME_MUTE
    0xae: 'volumedown',  # VK_VOLUME_DOWN
    0xaf: 'volumeup',  # VK_VOLUME_UP
    0xb0: 'nexttrack',  # VK_MEDIA_NEXT_TRACK
    0xb1: 'prevtrack',  # VK_MEDIA_PREV_TRACK
    0xb2: 'stop',  # VK_MEDIA_STOP
    0xb3: 'playpause',  # VK_MEDIA_PLAY_PAUSE
    0xb4: 'launchmail',  # VK_LAUNCH_MAIL
    0xb5: 'launchmediaselect',  # VK_LAUNCH_MEDIA_SELECT
    0xb6: 'launchapp1',  # VK_LAUNCH_APP1
    0xb7: 'launchapp2',  # VK_LAUNCH_APP2
}


def ctrl(conn):
    '''
    读取控制命令，并在本机还原操作
    '''
    def Op(key, op, ox, oy):
        # print(key, op, ox, oy)
        if key == 4:
            # 鼠标移动
            ag.moveTo(ox, oy)
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
            k = keyboardMapping.get(key)
            if k is not None:
                if op == 100:
                    ag.keyDown(k)
                elif op == 117:
                    ag.keyUp(k)
    try:
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
