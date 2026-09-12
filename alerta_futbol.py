"""
Alerta de "0-0 al minuto 70" para las 5 grandes ligas europeas.

Revisa los partidos EN VIVO usando la API de API-Football y envia un mensaje
de Telegram la primera vez que un partido llega al minuto objetivo (70 por
defecto) sin goles.

Variables de entorno requeridas:
  API_FOOTBALL_KEY     -> API key de https://www.api-football.com (plan free)
  TELEGRAM_BOT_TOKEN   -> token del bot de Telegram (via @BotFather)
  TELEGRAM_CHAT_ID     -> chat_id al que se envia el aviso

Variables opcionales:
  MINUTO_OBJETIVO   (default 70)
  VENTANA_MINUTOS   (default 15)  -> tolerancia para no perder el aviso
                                     si el chequeo cae unos minutos despues
"""

import os
import sys
import json
import requests

API_KEY = os.environ["API_FOOTBALL_KEY"]
BOT_TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
CHAT_ID = os.environ["TELEGRAM_CHAT_ID"]

MINUTO_OBJETIVO = int(os.environ.get("MINUTO_OBJETIVO", "70"))
VENTANA_MINUTOS = int(os.environ.get("VENTANA_MINUTOS", "15"))

# (nombre de liga, pais) tal como los devuelve API-Football
LIGAS_OBJETIVO = {
    ("Premier League", "England"),
    ("La Liga", "Spain"),
    ("Serie A", "Italy"),
    ("Bundesliga", "Germany"),
    ("Ligue 1", "France"),
}

STATE_FILE = "notified.json"


def cargar_estado():
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE) as f:
            try:
                return set(json.load(f))
            except json.JSONDecodeError:
                return set()
    return set()


def guardar_estado(ids):
    with open(STATE_FILE, "w") as f:
        json.dump(sorted(ids), f)


def obtener_partidos_en_vivo():
    url = "https://v3.football.api-sports.io/fixtures"
    headers = {"x-apisports-key": API_KEY}
    params = {"live": "all"}
    r = requests.get(url, headers=headers, params=params, timeout=20)
    r.raise_for_status()
    return r.json().get("response", [])


def enviar_telegram(mensaje):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    r = requests.post(url, data={"chat_id": CHAT_ID, "text": mensaje}, timeout=20)
    r.raise_for_status()


def main():
    notificados = cargar_estado()
    nuevos_notificados = set(notificados)

    try:
        partidos = obtener_partidos_en_vivo()
    except Exception as e:
        print(f"Error consultando partidos en vivo: {e}", file=sys.stderr)
        return

    for p in partidos:
        liga = p["league"]["name"]
        pais = p["league"]["country"]
        if (liga, pais) not in LIGAS_OBJETIVO:
            continue

        fixture_id = p["fixture"]["id"]
        if fixture_id in notificados:
            continue

        estado = p["fixture"]["status"].get("elapsed") or 0
        goles_local = p["goals"]["home"] or 0
        goles_visita = p["goals"]["away"] or 0

        if (
            goles_local == 0
            and goles_visita == 0
            and MINUTO_OBJETIVO <= estado <= MINUTO_OBJETIVO + VENTANA_MINUTOS
        ):
            local = p["teams"]["home"]["name"]
            visita = p["teams"]["away"]["name"]
            mensaje = f"⚽ 0-0 al minuto {estado}\n{local} vs {visita}\n{liga}"
            try:
                enviar_telegram(mensaje)
                nuevos_notificados.add(fixture_id)
                print(f"Notificado: {local} vs {visita} ({estado}')")
            except Exception as e:
                print(f"Error enviando notificacion para {fixture_id}: {e}", file=sys.stderr)

    # Deja de rastrear partidos que ya no aparecen como "en vivo" (terminaron)
    ids_en_vivo = {p["fixture"]["id"] for p in partidos}
    nuevos_notificados = {fid for fid in nuevos_notificados if fid in ids_en_vivo}

    if nuevos_notificados != notificados:
        guardar_estado(nuevos_notificados)


if __name__ == "__main__":
    main()
