import os
import shutil
import psycopg2
import psutil
import subprocess
import threading
import time
import requests

from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

os.environ['PROC_ROOT'] = '/host/proc'
psutil.PROCFS_PATH = '/host/proc'

TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

DB_HOST = os.getenv("DB_HOST")
DB_NAME = os.getenv("POSTGRES_DB")
DB_USER = os.getenv("POSTGRES_USER")
DB_PASS = os.getenv("POSTGRES_PASSWORD")

if not TOKEN or not CHAT_ID:
    raise ValueError("Нужно задать BOT_TOKEN и CHAT_ID")

# ------------------ DB ------------------

def get_connection():
    return psycopg2.connect(
        host=DB_HOST,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASS
    )

# ------------------ SYSTEM INFO ------------------

def get_metrics():
    cpu = psutil.cpu_percent(interval=1)
    ram = psutil.virtual_memory().percent
    disk = psutil.disk_usage('/host/root').percent

    docker_cmd = shutil.which("docker")
    if not docker_cmd:
        containers = "Docker не найден"
    else:
        try:
            containers = subprocess.getoutput(f"{docker_cmd} ps --format '{{{{.Names}}}}'")
            if not containers:
                containers = "Нет активных контейнеров"
        except Exception as e:
            containers = f"Ошибка Docker: {e}"

    return cpu, ram, disk, containers


def get_top_processes():
    processes = sorted(
        [(p.info['name'], p.info['cpu_percent'])
         for p in psutil.process_iter(['name', 'cpu_percent'])],
        key=lambda x: x[1],
        reverse=True
    )[:5]

    result = ""
    for name, cpu in processes:
        result += f"{name} — {cpu}%\n"

    return result if result else "Нет данных"

# ------------------ TELEGRAM SEND ------------------

def send_telegram_message(text):
    try:
        response = requests.post(
            f"https://api.telegram.org/bot{TOKEN}/sendMessage",
            data={
                "chat_id": CHAT_ID,
                "text": text
            }
        )
        print(f"Telegram response: {response.status_code} {response.text}", flush=True)
    except Exception as e:
        print(f"Ошибка отправки: {e}", flush=True)

# ------------------ MONITORING ------------------

last_alert_time = 0
alert_active = False

def monitor_loop():
    global last_alert_time, alert_active

    print("monitor_loop запущен", flush=True)

    # Прогрев psutil
    psutil.cpu_percent(interval=1)
    time.sleep(5)

    while True:
        try:
            cpu, ram, disk, containers = get_metrics()
            overload = cpu > 40 or ram > 80 or disk > 80
            now = time.time()

            print(f"DEBUG: cpu={cpu} ram={ram} disk={disk} overload={overload} alert_active={alert_active}", flush=True)

            message = (
                f"⚙️ Состояние сервера:\n\n"
                f"CPU: {cpu}%\n"
                f"RAM: {ram}%\n"
                f"Disk: {disk}%"
            )

            if overload:
                if not alert_active or (now - last_alert_time > 300):
                    send_telegram_message("⚠ ПЕРЕГРУЗКА!\n\n" + message)
                    last_alert_time = now
                    alert_active = True
            else:
                if alert_active:
                    send_telegram_message("✅ Восстановлено\n\n" + message)
                    alert_active = False

        except Exception as e:
            print(f"Ошибка в monitor_loop: {e}", flush=True)

        time.sleep(60)

# ------------------ COMMANDS ------------------

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("INSERT INTO test_table(message) VALUES('User started bot')")
    conn.commit()
    cur.close()
    conn.close()

    await update.message.reply_text("Бот работает и подключен к базе данных!")


async def get_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    await update.message.reply_text(f"Ваш chat_id: {chat_id}")


async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    cpu, ram, disk, containers = get_metrics()

    msg = (
        f"⚙️ Состояние сервера:\n\n"
        f"🖥 CPU: {cpu}%\n"
        f"🧠 RAM: {ram}%\n"
        f"💾 Disk: {disk}%\n\n"
        f"🐳 Контейнеры:\n{containers}"
    )
    await update.message.reply_text(msg)


async def containers(update: Update, context: ContextTypes.DEFAULT_TYPE):
    docker_cmd = shutil.which("docker")
    if not docker_cmd:
        await update.message.reply_text("❌ Docker не найден")
        return

    try:
        result = subprocess.getoutput(
            f"{docker_cmd} ps -a --format '{{{{.Names}}}} ({{{{.Status}}}})'"
        )
        msg = result if result else "Нет контейнеров"
    except Exception as e:
        msg = f"Ошибка: {e}"

    await update.message.reply_text(f"🐳 Контейнеры:\n{msg}")


async def top(update: Update, context: ContextTypes.DEFAULT_TYPE):
    processes = get_top_processes()

    msg = f"🔥 Топ процессов по CPU:\n\n{processes}"
    await update.message.reply_text(msg)

# ------------------ APP ------------------

app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("id", get_id))
app.add_handler(CommandHandler("status", status))
app.add_handler(CommandHandler("containers", containers))
app.add_handler(CommandHandler("top", top))

# ------------------ RUN ------------------

if __name__ == "__main__":
    threading.Thread(target=monitor_loop, daemon=True).start()
    app.run_polling()
