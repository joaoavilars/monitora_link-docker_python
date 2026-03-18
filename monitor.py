import os
import time
import requests
import subprocess
from datetime import datetime

TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_ID")
FREQ = int(os.getenv("FREQUENCIA", 60))

# Suporta múltiplos hosts separados por vírgula
targets = [t.strip() for t in os.getenv("IP_MONITORADO", "").split(",") if t.strip()]
names   = [n.strip() for n in os.getenv("NOME_HOST",    "").split(",") if n.strip()]
modes   = [m.strip().upper() for m in os.getenv("TIPO", "PING").split(",") if m.strip()]

# Monta lista de hosts com fallback para listas menores
hosts = []
for i, ip in enumerate(targets):
    hosts.append({
        "ip":       ip,
        "nome":     names[i] if i < len(names) else ip,
        "modo":     modes[i] if i < len(modes) else "PING",
        "is_up":    True,
        "down_time": None,
    })

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

def check_ping(ip):
    return os.system(f"ping -c 1 -W 5 {ip} > /dev/null 2>&1") == 0

def check_snmp(ip):
    try:
        result = subprocess.run(
            ["snmpget", "-v2c", "-c", "public", "-t", "5", ip, "1.3.6.1.2.1.1.3.0"],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )
        return result.returncode == 0
    except Exception:
        return False

print(f"Monitoramento iniciado para {len(hosts)} host(s):")
for h in hosts:
    print(f"  - {h['nome']} ({h['ip']}) via {h['modo']}")

while True:
    for host in hosts:
        current_status = check_ping(host["ip"]) if host["modo"] == "PING" else check_snmp(host["ip"])

        if not current_status and host["is_up"]:
            host["down_time"] = datetime.now()
            msg = (
                f"❌ Novo Incidente: {host['nome']} - Link fora do ar\n"
                f"Inicio em {host['down_time'].strftime('%H:%M:%S')} no dia {host['down_time'].strftime('%Y.%m.%d')}\n"
                f"Host: {host['nome']}"
            )
            send_telegram(msg)
            print(f"[{host['down_time'].strftime('%Y.%m.%d %H:%M:%S')}] ALERTA: {host['nome']} caiu")
            host["is_up"] = False

        elif current_status and not host["is_up"]:
            up_time = datetime.now()
            dur_str = format_duration((up_time - host["down_time"]).total_seconds())
            msg = (
                f"✅ Incidente: {host['nome']} - Link fora do ar resolvido em {dur_str}\n"
                f"Incidente resolvido as {up_time.strftime('%H:%M:%S')} no dia {up_time.strftime('%Y.%m.%d')}\n"
                f"Duração: {dur_str}\n"
                f"Host: {host['nome']}"
            )
            send_telegram(msg)
            print(f"[{up_time.strftime('%Y.%m.%d %H:%M:%S')}] RESOLVIDO: {host['nome']} voltou após {dur_str}")
            host["is_up"] = True
            host["down_time"] = None

    time.sleep(FREQ)
