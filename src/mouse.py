import ctypes
import ctypes.wintypes
user32 = ctypes.windll.user32


class MOUSEINPUT(ctypes.Structure):
    _fields_ = [
        ("dx", ctypes.c_long),
        ("dy", ctypes.c_long),
        ("mouseData", ctypes.c_ulong),
        ("dwFlags", ctypes.c_ulong),
        ("time", ctypes.c_ulong),
        ("dwExtraInfo", ctypes.c_void_p),
    ]


class INPUT(ctypes.Structure):
    _fields_ = [
        ("type", ctypes.c_ulong),
        ("mi", MOUSEINPUT),
    ]


INPUT_MOUSE = 0

MOUSEEVENTF_MOVE = 0x0001
MOUSEEVENTF_LEFTDOWN = 0x0002
MOUSEEVENTF_LEFTUP = 0x0004
MOUSEEVENTF_ABSOLUTE = 0x8000

user32.SendInput.argtypes = [
    ctypes.c_uint,
    ctypes.POINTER(INPUT),
    ctypes.c_int
]

user32.SendInput.restype = ctypes.c_uint

user32 = ctypes.windll.user32

SCREEN_WIDTH = user32.GetSystemMetrics(0)
SCREEN_HEIGHT = user32.GetSystemMetrics(1)

pointer_is_down = False

def move_mouse(x: float, y: float):
    x = max(0.0, min(1.0, x))
    y = max(0.0, min(1.0, y))

    px = int(x * (SCREEN_WIDTH - 1))
    py = int(y * (SCREEN_HEIGHT - 1))

    absolute_x = int(px * 65535 / (SCREEN_WIDTH - 1))
    absolute_y = int(py * 65535 / (SCREEN_HEIGHT - 1))

    inp = INPUT(
        type=INPUT_MOUSE,
        mi=MOUSEINPUT(
            dx=absolute_x,
            dy=absolute_y,
            mouseData=0,
            dwFlags=MOUSEEVENTF_MOVE | MOUSEEVENTF_ABSOLUTE,
            time=0,
            dwExtraInfo=None
        )
    )

    user32.SendInput(
        1,
        ctypes.byref(inp),
        ctypes.sizeof(INPUT)
    )


def mouse_down():
    inp = INPUT(
        type=INPUT_MOUSE,
        mi=MOUSEINPUT(
            dx=0,
            dy=0,
            mouseData=0,
            dwFlags=MOUSEEVENTF_LEFTDOWN,
            time=0,
            dwExtraInfo=None
        )
    )

    user32.SendInput(
        1,
        ctypes.byref(inp),
        ctypes.sizeof(INPUT)
    )


def mouse_up():
    inp = INPUT(
        type=INPUT_MOUSE,
        mi=MOUSEINPUT(
            dx=0,
            dy=0,
            mouseData=0,
            dwFlags=MOUSEEVENTF_LEFTUP,
            time=0,
            dwExtraInfo=None
        )
    )

    user32.SendInput(
        1,
        ctypes.byref(inp),
        ctypes.sizeof(INPUT)
    )

def move_mouse_relative(dx: float, dy: float):
    point = ctypes.wintypes.POINT()

    user32.GetCursorPos(ctypes.byref(point))

    x = point.x + int(dx)
    y = point.y + int(dy)

    x = max(0, min(SCREEN_WIDTH - 1, x))
    y = max(0, min(SCREEN_HEIGHT - 1, y))

    move_mouse(x / SCREEN_WIDTH, y / SCREEN_HEIGHT)