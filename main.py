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
from fastapi import Request
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
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/main")
def index(auth: bool = Depends(check_auth)):
    return FileResponse("static/index.html")

@app.get("/")
def index():
    return RedirectResponse(url="/main")

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

@app.get("/info")
def info():
    boot_time = psutil.boot_time()
    uptime_seconds = int(time.time() - boot_time)
    
    position_str =  str(subprocess.run(['playerctl', 'position'], capture_output=True, text=True).stdout) * 100    
    position = ''
    try:
        for u in position_str:
            if u == '\n':
                break
            position += u
        position = float(position)
    except: 
        position = 0

    length_str =  str(subprocess.run(['playerctl', 'metadata', '--format', '{{ mpris:length / 1000000 }}'], capture_output=True, text=True).stdout) * 100
    
    length = ''    
    try:
        for u in length_str:
            if u == '\n':
                break
            length += u
        length = float(length)
    except:
        length = 1

    voulme = str(subprocess.run(['wpctl', 'get-volume', '@DEFAULT_AUDIO_SINK@'], capture_output=True, text=True).stdout.split(' ')[1][:-1])
    
    return {
        "cpu": psutil.cpu_percent(interval=0.5),
        "temp": get_cpu_temp(),
        "ram": psutil.virtual_memory().percent,
        "CHARGE": psutil.sensors_battery().percent,
        "disk" : psutil.disk_usage('/').percent,
        "hostname": socket.gethostname(),
        "os": platform.system(),
        "kernel": platform.release(),
        "uptime": str(datetime.timedelta(seconds=uptime_seconds)),
        "track" : str(subprocess.run(['playerctl', 'metadata', '--format', '{{artist}} - {{title}} | {{album}}'], capture_output=True, text=True).stdout),
        "status" : str(subprocess.run(['playerctl', 'status'], capture_output=True, text=True).stdout), 
        "progress" : position / length * 100, 
        "position" : str(subprocess.run(['playerctl', 'metadata', '--format', '{{ duration(position) }}'], capture_output=True, text=True).stdout),
        "length" : str(subprocess.run([ 'playerctl', 'metadata', '--format', '{{ duration(mpris:length) }}'], capture_output=True, text=True).stdout),
        "volume" : float(voulme) * 100
    }

@app.post("/exec")
async def exec(request: Request):
    data = await request.json()
    print(data["command"])
    if data["command"] == "poweroff":
        subprocess.run(["poweroff"])
    elif data["command"] == "reboot":
        subprocess.run(["reboot"])
    elif data["command"] == "suspend":        
        subprocess.run(["systemctl", "suspend"])
    elif data["command"] == "lock":
        subprocess.run(["hyprlock"])
    elif data["command"] == "playpause":
        subprocess.run(['playerctl', 'play-pause'], capture_output=True, text=True)
    elif data["command"] == "next":
        subprocess.run(['playerctl', 'next'], capture_output=True, text=True)
    elif data["command"] == "prev":
        subprocess.run(['playerctl', 'previous'], capture_output=True, text=True)
    return {
        "message" : "ok"
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
