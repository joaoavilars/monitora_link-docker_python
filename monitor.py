import os
import time
import requests
import subprocess
from datetime import datetime

# Carrega variáveis do ambiente
TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_ID")
TARGET = os.getenv("IP_MONITORADO")
FREQ = int(os.getenv("FREQUENCIA", 60))
MODE = os.getenv("TIPO", "PING").upper()
NOME_HOST = os.getenv("NOME_HOST", TARGET)

def send_telegram(msg):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    try:
        requests.post(url, json={"chat_id": CHAT_ID, "text": msg}, timeout=10)
    except Exception as e:
        print(f"Erro Telegram: {e}")

def format_duration(seconds):
    minutes = int(seconds // 60)
    secs = int(seconds % 60)
    if minutes > 0:
        return f"{minutes}m {secs}s"
    return f"{secs}s"

def check_ping():
    status = os.system(f"ping -c 1 -W 5 {TARGET} > /dev/null 2>&1")
    return status == 0

def check_snmp():
    try:
        result = subprocess.run(
            ["snmpget", "-v2c", "-c", "public", "-t", "5", TARGET, "1.3.6.1.2.1.1.3.0"],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )
        return result.returncode == 0
    except Exception:
        return False

print(f"Monitoramento iniciado para {TARGET} via {MODE}...")
is_up = True
down_time = None

while True:
    current_status = check_ping() if MODE == "PING" else check_snmp()

    if not current_status and is_up:
        down_time = datetime.now()
        msg = (
            f"❌ Novo Incidente: {NOME_HOST} - Link fora do ar\n"
            f"Inicio em {down_time.strftime('%H:%M:%S')} no dia {down_time.strftime('%Y.%m.%d')}\n"
            f"Host: {NOME_HOST}"
        )
        send_telegram(msg)
        print(f"[{down_time.strftime('%Y.%m.%d %H:%M:%S')}] ALERTA: {NOME_HOST} caiu")
        is_up = False

    elif current_status and not is_up:
        up_time = datetime.now()
        duration = (up_time - down_time).total_seconds()
        dur_str = format_duration(duration)
        msg = (
            f"✅ Incidente: {NOME_HOST} - Link fora do ar resolvido em {dur_str}\n"
            f"Incidente resolvido as {up_time.strftime('%H:%M:%S')} no dia {up_time.strftime('%Y.%m.%d')}\n"
            f"Duração: {dur_str}\n"
            f"Host: {NOME_HOST}"
        )
        send_telegram(msg)
        print(f"[{up_time.strftime('%Y.%m.%d %H:%M:%S')}] RESOLVIDO: {NOME_HOST} voltou após {dur_str}")
        is_up = True
        down_time = None

    time.sleep(FREQ)
