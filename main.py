import uvicorn
from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
import psutil
import socket
import platform
import time
import datetime
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
import subprocess



app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://10.42.0.1:8000",
        "http://localhost:8000",
        "http://127.0.0.1:8000"
    ],
    allow_credentials=True,
    allow_methods=["GET"],
    allow_headers=["*"],
)
# подключаем статические файлы
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/main")
def index():
    return FileResponse("static/index.html")

@app.get("/")
def index():
    return RedirectResponse(url="/main")

@app.get("/reboot")
def reboot():
    subprocess.run(["reboot"])
    return {
        "message": "ok"
    }

@app.get("/suspend")
def suspend():
    subprocess.run(["systemctl", "suspend"])
    return {
        "message": "ok"
    }

@app.get("/poweroff")
def poweroff():
    subprocess.run(["poweroff"])
    return {
        "message": "ok"
    }

@app.get("/api/click")
def click():
    return {"message": "Кнопка нажата с сервера 🚀"}

def get_cpu_temp():
    temps = psutil.sensors_temperatures()

    # 1. пробуем package
    for entries in temps.values():
        for e in entries:
            if "Package" in e.label:
                return e.current

    # 2. fallback: среднее по ядрам
    cores = [
        e.current
        for entries in temps.values()
        for e in entries
        if "Core" in e.label
    ]

    if cores:
        return sum(cores) / len(cores)

    return None

@app.get("/metrics")
def metrics():
    return {
        "cpu": psutil.cpu_percent(interval=0.5),
        "temp": get_cpu_temp(),
        "ram": psutil.virtual_memory().percent,
        "CHARGE": psutil.sensors_battery().percent,
        "disk" : psutil.disk_usage('/').percent
    }

@app.get("/info")
def metrics():
    boot_time = psutil.boot_time()
    uptime_seconds = int(time.time() - boot_time)
    return {
        "hostname": socket.gethostname(),
        "os": platform.system(),
        "kernel": platform.release(),
        "uptime": str(datetime.timedelta(seconds=uptime_seconds))
    }

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="10.42.0.1",
        port=8000,
        reload=False
    )
