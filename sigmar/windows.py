import collections
import ctypes
import time

from ctypes import (
    c_ubyte as BYTE,
    c_uint16 as WORD,
    c_uint32 as DWORD,
    c_int32 as LONG,
)

import PIL.Image
import PIL.ImageGrab
import pyautogui


NULL = 0
PW_RENDERFULLCONTENT = 2
DIB_RGB_COLORS = 0
ERROR_INVALID_PARAMETER = 87
HGDI_ERROR = -1


# https://msdn.microsoft.com/en-us/library/windows/desktop/dd162897(v=vs.85).aspx
class RECT(ctypes.Structure):
    _fields_ = [
        ("left", LONG),
        ("top", LONG),
        ("right", LONG),
        ("bottom", LONG),
    ]


# https://msdn.microsoft.com/en-us/library/windows/desktop/dd183376(v=vs.85).aspx
class BITMAPINFOHEADER(ctypes.Structure):
    _fields_ = [
        ('size', DWORD),
        ('width', LONG),
        ('height', LONG),
        ('planes', WORD),
        ('bit_count', WORD),
        ('compression', DWORD),
        ('size_image', DWORD),
        ('x_pels_per_meter', LONG),
        ('y_pels_per_meter', LONG),
        ('clr_used', DWORD),
        ('clr_important', DWORD)
    ]


# https://msdn.microsoft.com/en-us/library/windows/desktop/dd162938(v=vs.85).aspx
class RGBQUAD(ctypes.Structure):
    _fields_ = [
        ("blue", BYTE),
        ("green", BYTE),
        ("red", BYTE),
        ("reserved", BYTE),
    ]


# https://msdn.microsoft.com/en-us/library/windows/desktop/dd183375(v=vs.85).aspx
class BITMAPINFO(ctypes.Structure):
    _fields_ = [
        ('header', BITMAPINFOHEADER),
        ('colors', RGBQUAD * 1)
    ]


class ScreenshotError(Exception):
    pass


class WindowNotFoundError(ScreenshotError):
    def __init__(self):
        super(WindowNotFoundError, self).__init__(
            "Opus Magnum window not found. Is the game running?")


def _raise_error():
    error_code = ctypes.windll.kernel32.GetLastError()
    raise ScreenshotError(f"system call failed with error code {error_code:08x}")


def _get_window_handle():
    window_handle = ctypes.windll.User32.FindWindowA(NULL, ctypes.c_char_p(b"Opus Magnum"))
    if window_handle == NULL:
        raise WindowNotFoundError
    return window_handle


Dimensions = collections.namedtuple("Dimensions", "width height")


def _get_window_dimensions(window_handle):
    client_rect = RECT()
    result = ctypes.windll.user32.GetClientRect(window_handle, ctypes.byref(client_rect))
    if result == 0:
        _raise_error()
    return Dimensions(width=client_rect.right - client_rect.left, height=client_rect.bottom - client_rect.top)


def get_screenshot():
    window_handle = _get_window_handle()
    dimensions = _get_window_dimensions(window_handle)
    window_dc = ctypes.windll.user32.GetWindowDC(window_handle)
    bitmap_dc = ctypes.windll.gdi32.CreateCompatibleDC(window_dc)
    bitmap = ctypes.windll.gdi32.CreateCompatibleBitmap(window_dc, dimensions.width, dimensions.height)
    ctypes.windll.gdi32.SelectObject(bitmap_dc, bitmap)

    try:
        result = ctypes.windll.user32.PrintWindow(window_handle, bitmap_dc, PW_RENDERFULLCONTENT)
        if result == 0:
            raise ScreenshotError("PrintWindow failed")

        bmi = BITMAPINFO()
        ctypes.memset(ctypes.byref(bmi), 0x00, ctypes.sizeof(bmi))
        bmi.header.size = ctypes.sizeof(BITMAPINFOHEADER)
        bmi.header.width = dimensions.width
        bmi.header.height = dimensions.height
        bmi.header.planes = 1
        bmi.header.bit_count = 24

        row_size = ((dimensions.width * bmi.header.bit_count + 31) // 32) * 4
        buffer_size = row_size * dimensions.height
        buffer = ctypes.create_string_buffer(buffer_size)

        ctypes.windll.gdi32.GetDIBits(
            bitmap_dc, bitmap,
            0, dimensions.height,
            ctypes.byref(buffer),
            ctypes.byref(bmi),
            DIB_RGB_COLORS,
        )
        if result == 0 or result == ERROR_INVALID_PARAMETER:
            raise ScreenshotError("GetDIBits failed")

        return PIL.Image.frombuffer("RGB", dimensions, buffer, "raw", "BGR", row_size, -1)
    finally:
        ctypes.windll.gdi32.DeleteDC(bitmap_dc)
        ctypes.windll.gdi32.DeleteObject(bitmap)
        ctypes.windll.user32.ReleaseDC(window_handle, window_dc)


def set_window_foreground(handle=None):
    if handle is None:
        handle = _get_window_handle()
    ctypes.windll.user32.SetForegroundWindow(handle)
    time.sleep(.1)


def get_window_rectangle(handle=None):
    if handle is None:
        handle = _get_window_handle()
    rect = RECT()
    result = ctypes.windll.user32.GetWindowRect(handle, ctypes.byref(rect))
    if result == 0:
        _raise_error()
    return rect


def click_in_window(client_x, client_y):
    handle = _get_window_handle()
    set_window_foreground(handle)
    rect = get_window_rectangle(handle)

    x = client_x + rect.left
    y = client_y + rect.top

    pyautogui.mouseDown(button="left", x=x, y=y)
    time.sleep(0.1)
    pyautogui.mouseUp(button="left", x=x, y=y)


def click_new_game():
    set_window_foreground()

    center = pyautogui.locateCenterOnScreen("new_game_template.png")
    if not center:
        raise Exception("Couldn't find new game button, is Sigmar's Garden open?")

    x, y = center
    pyautogui.mouseDown(button="left", x=x, y=y)
    time.sleep(0.1)
    pyautogui.mouseUp(button="left", x=x, y=y)
    pyautogui.moveTo(x=100, y=100)
    time.sleep(6)
