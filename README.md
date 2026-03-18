# monitora_link

Monitoramento de IP/host via PING ou SNMP com alertas no Telegram no padrão Zabbix.

## Funcionalidades

- Monitora disponibilidade de um host via **PING** ou **SNMP**
- Envia alerta no Telegram quando o link cai
- Envia notificação de restabelecimento com horário, data e duração do incidente
- Fuso horário configurável (padrão: `America/Sao_Paulo`)

## Exemplo de mensagens

**Incidente:**
```
❌ Novo Incidente: LINK-MATRIZ - Link fora do ar
Inicio em 03:49:09 no dia 2026.03.18
Host: LINK-MATRIZ
```

**Restabelecimento:**
```
✅ Incidente: LINK-MATRIZ - Link fora do ar resolvido em 15m 54s
Incidente resolvido as 04:05:03 no dia 2026.03.18
Duração: 15m 54s
Host: LINK-MATRIZ
```

## Pré-requisitos

- Docker e Docker Compose instalados
- Bot do Telegram criado via [@BotFather](https://t.me/BotFather)
- Chat ID do grupo/canal onde os alertas serão enviados

## Configuração

1. Copie o arquivo de exemplo e preencha com seus dados:

```bash
cp .env.example .env
```

2. Edite o `.env`:

| Variável | Descrição | Exemplo |
|---|---|---|
| `TELEGRAM_TOKEN` | Token do bot gerado pelo BotFather | `123456:ABC-xyz...` |
| `TELEGRAM_ID` | ID do chat/grupo que receberá os alertas | `-100123456789` |
| `IP_MONITORADO` | IP ou hostname do alvo | `200.100.50.1` |
| `NOME_HOST` | Nome amigável exibido nas mensagens | `LINK-FILIAL-01` |
| `FREQUENCIA` | Intervalo entre verificações em segundos | `60` |
| `TIPO` | Método de verificação: `PING` ou `SNMP` | `PING` |

> **Dica:** Para obter o Chat ID, adicione o bot ao grupo e acesse:
> `https://api.telegram.org/bot<SEU_TOKEN>/getUpdates`

## Uso

```bash
# Subir o container
docker compose up --build -d

# Ver logs em tempo real
docker logs -f link-monitor-externo

# Parar
docker compose down
```

## Estrutura

```
monitora_link/
├── monitor.py          # Script principal
├── Dockerfile
├── docker-compose.yml
├── .env                # Suas credenciais (não versionado)
└── .env.example        # Modelo de configuração
```

## SNMP (MikroTik)

Para usar o modo SNMP, habilite no MikroTik:

```
/snmp set enabled=yes community=public
```

E defina `TIPO=SNMP` no `.env`.
