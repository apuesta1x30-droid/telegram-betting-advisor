import os
import requests
import logging

# Configuración básica
API_KEY = os.getenv("ODDS_API_KEY")
BASE_URL = "https://api.the-odds-api.com/v4"

def get_sports():
    """Obtiene la lista de deportes disponibles."""
    try:
        url = f"{BASE_URL}/sports/?apiKey={API_KEY}"
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        logging.error(f"Error al obtener deportes: {e}")
        return []

def get_odds(sport_key="soccer_spain_la_liga", regions="eu", markets="h2h"):
    """Obtiene las cuotas para un deporte específico."""
    try:
        url = f"{BASE_URL}/sports/{sport_key}/odds/?apiKey={API_KEY}&regions={regions}&markets={markets}"
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        logging.error(f"Error al obtener cuotas: {e}")
        return []
