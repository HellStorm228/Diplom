import os
import psutil
import requests
import subprocess

# Получаем токен и чат ID из переменных окружения
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
    # Формируем URL корректно через переменную
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    response = requests.post(url, data={"chat_id": CHAT_ID, "text": message})
    if response.status_code != 200:
        print(f"Ошибка отправки сообщения: {response.text}")

def check():
    cpu, ram, disk, containers = get_metrics()

    message = f"""
Состояние сервера:

CPU: {cpu}%
RAM: {ram}%
Disk: {disk}%

Контейнеры:
{containers}
"""

    if cpu > 1 or ram > 1 or disk > 1:
        send_alert("⚠ ПРЕВЫШЕНИЕ НАГРУЗКИ!\n" + message)
    else:
        print("OK")

if __name__ == "__main__":
    check()
