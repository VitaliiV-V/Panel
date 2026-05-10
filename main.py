import uvicorn
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
import psutil
import socket
import platform
import time
import datetime
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials
import subprocess
import secrets
from dotenv import load_dotenv
import os


load_dotenv()

security = HTTPBasic()

USERNAME = os.getenv("USERNAME")
PASSWORD = os.getenv("PASSWORD")

def check_auth(credentials: HTTPBasicCredentials = Depends(security)):
    correct_user = secrets.compare_digest(credentials.username, USERNAME)
    correct_pass = secrets.compare_digest(credentials.password, PASSWORD)

    if not (correct_user and correct_pass):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unauthorized",
            headers={"WWW-Authenticate": "Basic"},
        )
    return True


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
def index(auth: bool = Depends(check_auth)):
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

def query(s):
    penis = subprocess.run(
        s,
        capture_output=True,
        text=True
    )
    return penis.stdout

@app.get("/info")
def metrics():
    boot_time = psutil.boot_time()
    uptime_seconds = int(time.time() - boot_time)
    x1 =  str(query(['playerctl', 'position'])) * 100
    x2 = ''
    for u in x1:
        if u == '\n':
            break
        x2 += u
    x2 = float(x2)
    x3 =  str(query(['playerctl', 'metadata', '--format', '{{ mpris:length / 1000000 }}'])) * 100
    x4 = ''
    for u in x3:
        if u == '\n':
            break
        x4 += u
    x4 = float(x4)
    print(x2 / x4 * 100)
    x5 = str(query(['wpctl', 'get-volume', '@DEFAULT_AUDIO_SINK@']).split(' ')[1][:-1])
    print(x5)
    return {
        "hostname": socket.gethostname(),
        "os": platform.system(),
        "kernel": platform.release(),
        "uptime": str(datetime.timedelta(seconds=uptime_seconds)),
        "track" : str(query(['playerctl', 'metadata', '--format', '{{artist}} - {{title}} | {{album}}'])),
        "status" : str(query(['playerctl', 'status'])),
        "progress" : x2 / x4 * 100,
        "position" : str(query(['playerctl', 'metadata', '--format', '{{ duration(position) }}'])),
        "length" : str(query([ 'playerctl', 'metadata', '--format', '{{ duration(mpris:length) }}'])),
        "volume" : float(x5) * 100
    }

@app.get("/playpause")
def play_pause():
    status = subprocess.run(
        ['playerctl', 'status'],
        capture_output=True,
        text=True
    )
    if status.stdout == "Playing\n":
        status = subprocess.run(
            ['playerctl', 'pause'],
            capture_output=True,
            text=True
        )
        return {
            "status": "Paused"
        }
    else:
        status = subprocess.run(
            ['playerctl', 'play'],
            capture_output=True,
            text=True
        )
        return {
            "status": "Playing\n"
        }

@app.get("/playpause")
def play_pause():
    status = subprocess.run(
        ['playerctl', 'status'],
        capture_output=True,
        text=True
    )
    status = subprocess.run(
        ['playerctl', 'play-pause'],
        capture_output=True,
        text=True
    )
    if status.stdout == "Playing\n":
        return {
            "status": "Paused"
        }
    else:
        return {
            "status": "Playing\n"
        }


@app.get("/next")
def next():
    status = subprocess.run(
        ['playerctl', 'next'],
        capture_output=True,
        text=True
    )
    return {
        "message": "ok"
    }

@app.get("/previous")
def previous():
    status = subprocess.run(
        ['playerctl', 'previous'],
        capture_output=True,
        text=True
    )
    return {
        "message": "ok"
    }


if __name__ == "__main__":
    while True:
        try:
            uvicorn.run(
                "main:app",
                host="10.42.0.1",
                port=8000,
                reload=False
            )
            break
        except Exception as e:
            print(f"Ошибка запуска: {e}")
            print("Повтор через 3 секунды...")
            time.sleep(3)
