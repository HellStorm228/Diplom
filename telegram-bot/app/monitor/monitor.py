import os
import time
import psutil
import requests
import subprocess

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

if not BOT_TOKEN or not CHAT_ID:
    raise ValueError("Необходимо установить переменные окружения BOT_TOKEN и CHAT_ID")

def get_metrics():
    cpu = psutil.cpu_percent()
    ram = psutil.virtual_memory().percent
    disk = psutil.disk_usage('/').percent
    containers = subprocess.getoutput("docker ps --format '{{.Names}}'")
    return cpu, ram, disk, containers

def send_alert(message):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    requests.post(url, data={"chat_id": CHAT_ID, "text": message})

def check():
    cpu, ram, disk, containers = get_metrics()

    message = f"""
⚙️ Состояние сервера:

CPU: {cpu}%
RAM: {ram}%
Disk: {disk}%


"""

    if cpu > 1 or ram > 1 or disk > 1:
        send_alert("⚠ ПРЕВЫШЕНИЕ НАГРУЗКИ!\n" + message)
    else:
        print("OK")

if __name__ == "__main__":
    while True:
        check()
        time.sleep(1800)

