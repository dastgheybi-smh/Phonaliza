import ctypes
import ctypes.wintypes
user32 = ctypes.windll.user32
import json

from fastapi import FastAPI, WebSocket
from fastapi.responses import FileResponse
import uvicorn
import subprocess

from src.mouse import *


app = FastAPI()

@app.get("/")
async def index():
    return FileResponse("index.html")

@app.get("/screen")
async def screen_info():
    return {
        "width": SCREEN_WIDTH,
        "height": SCREEN_HEIGHT
    }


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()

    print("📱 Device connected")

    try:
        while True:
            message = await websocket.receive_text()
            data = json.loads(message)

            if data["type"] == "move_absolute":
                move_mouse(
                    data["x"],
                    data["y"]
                )

            elif data["type"] == "move_relative":
                move_mouse_relative(
                    data["dx"],
                    data["dy"]
                )

            elif data["type"] == "mouse_down":
                mouse_down()

            elif data["type"] == "mouse_up":
                mouse_up()

    except Exception as e:
        print("📱 Device disconnected")
        print(repr(e))


def setup_firewall():
    rule_name = "Phonaliza"

    check = subprocess.run(
        [
            "netsh",
            "advfirewall",
            "firewall",
            "show",
            "rule",
            f"name={rule_name}"
        ],
        capture_output=True,
        text=True,
        creationflags=subprocess.CREATE_NO_WINDOW
    )

    if "No rules match" not in check.stdout:
        print("🔥 Phonaliza firewall rule already exists")
        return

    print("🛡️ Requesting administrator permission...")

    command = [
        "netsh",
        "advfirewall",
        "firewall",
        "add",
        "rule",
        'name=Phonaliza',
        "dir=in",
        "action=allow",
        "protocol=TCP",
        "localport=8080",
        "profile=Private"
    ]

    import ctypes

    result = ctypes.windll.shell32.ShellExecuteW(
        None,
        "runas",
        "netsh.exe",
        " ".join(f'"{x}"' if " " in x else x for x in command[1:]),
        None,
        0
    )

    if result > 32:
        print("✅ Firewall rule created")
    else:
        print("❌ Firewall permission denied")

if __name__ == "__main__":
    print("Starting Phone Mouse...")
    print(f"Screen: {SCREEN_WIDTH}x{SCREEN_HEIGHT}")
    print("Open http://<PC-IP>:8080 on your phone")

    setup_firewall()

    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8080
    )