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

load_dotenv("/home/master/PycharmProject0s/X-API/.env")

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
    ],
    allow_credentials=True,
    allow_methods=["GET"],
    allow_headers=["*"],
)

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
def power_off():
    subprocess.run(["poweroff"])
    return {
        "message": "ok"
    }

def get_cpu_temp():
    temps = psutil.sensors_temperatures()

    for entries in temps.values():
        for e in entries:
            if "Package" in e.label:
                return e.current


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
    
    position_str =  str(query(['playerctl', 'position'])) * 100
    position = ''
    for u in position_str:
        if u == '\n':
            break
        position += u
    position = float(position)
    length_str =  str(query(['playerctl', 'metadata', '--format', '{{ mpris:length / 1000000 }}'])) * 100
    
    length = ''
    for u in length_str:
        if u == '\n':
            break
        length += u
    length = float(length)
    print(position / length * 100)
    voulme = str(query(['wpctl', 'get-volume', '@DEFAULT_AUDIO_SINK@']).split(' ')[1][:-1])
    
    return {
        "hostname": socket.gethostname(),
        "os": platform.system(),
        "kernel": platform.release(),
        "uptime": str(datetime.timedelta(seconds=uptime_seconds)),
        "track" : str(query(['playerctl', 'metadata', '--format', '{{artist}} - {{title}} | {{album}}'])),
        "status" : str(query(['playerctl', 'status'])),
        "progress" : position / length * 100,
        "position" : str(query(['playerctl', 'metadata', '--format', '{{ duration(position) }}'])),
        "length" : str(query([ 'playerctl', 'metadata', '--format', '{{ duration(mpris:length) }}'])),
        "volume" : float(voulme) * 100
    }

@app.get("/playpause")
def play_pause():
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
            print(f"{e}")
            time.sleep(3)
