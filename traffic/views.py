from django.shortcuts import render
import requests
from django.utils import timezone
from datetime import datetime

def get_airport_city(icao):
    airport_cities = {
        'LFPG': 'Paris Charles de Gaulle',
        'LHR': 'Londres Heathrow',
        'JFK': 'New York JFK',
        'CDG': 'Paris Charles de Gaulle',
        'ORY': 'Paris Orly',
        'AMS': 'Amsterdam Schiphol',
        'FRA': 'Francfort',
        'MAD': 'Madrid',
        'BCN': 'Barcelone',
        'NCE': 'Nice',
        'LAX': 'Los Angeles',
        'SFO': 'San Francisco',
        'DXB': 'Dubaï',
        'HND': 'Tokyo Haneda',
        'ATL': 'Atlanta',
        'PEK': 'Pékin',
        'SIN': 'Singapour',
        'IST': 'Istanbul',
        'GRU': 'São Paulo',
        'SYD': 'Sydney',
    }
    return airport_cities.get(icao, icao)

def airport_traffic_view(request):
    icao = request.GET.get('icao', 'LFPG').upper()
    airport_city = get_airport_city(icao)
    now = timezone.now()
    begin = int(now.timestamp()) - 3600
    end = int(now.timestamp())
    url_arrivals = f'https://opensky-network.org/api/flights/arrival?airport={icao}&begin={begin}&end={end}'
    url_departures = f'https://opensky-network.org/api/flights/departure?airport={icao}&begin={begin}&end={end}'
    arrivals, departures = [], []
    try:
        resp_arr = requests.get(url_arrivals, timeout=10)
        if resp_arr.status_code == 200:
            arrivals = resp_arr.json()
            for flight in arrivals:
                if 'lastSeen' in flight:
                    flight['lastSeen_fmt'] = datetime.fromtimestamp(flight['lastSeen']).strftime('%d/%m/%Y %H:%M:%S')
                # Ajout de la ville d'arrivée
                city = get_airport_city(flight.get('estArrivalAirport', ''))
                flight['arrival_city'] = city
                # Prévision d'arrivée (si possible, sinon on prend lastSeen)
                if 'lastSeen' in flight:
                    flight['forecast_arrival'] = flight['lastSeen_fmt']
                else:
                    flight['forecast_arrival'] = '-'
    except Exception:
        arrivals = []
    try:
        resp_dep = requests.get(url_departures, timeout=10)
        if resp_dep.status_code == 200:
            departures = resp_dep.json()
            for flight in departures:
                if 'firstSeen' in flight:
                    flight['firstSeen_fmt'] = datetime.fromtimestamp(flight['firstSeen']).strftime('%d/%m/%Y %H:%M:%S')
    except Exception:
        departures = []
    return render(request, 'traffic/airport_traffic.html', {'arrivals': arrivals, 'departures': departures, 'icao': icao, 'airport_city': airport_city})
