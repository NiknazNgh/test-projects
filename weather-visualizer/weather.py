import requests
import matplotlib.pyplot as plt
from datetime import datetime

# Free API from Open-Meteo
URL = "https://api.open-meteo.com/v1/forecast"

def get_weather(city_lat, city_lon):
    params = {
        "latitude": city_lat,
        "longitude": city_lon,
        "hourly": "temperature_2m",
    }
    res = requests.get(URL, params=params)
    data = res.json()
    times = data["hourly"]["time"]
    temps = data["hourly"]["temperature_2m"]

    # Convert times to datetime
    hours = [datetime.fromisoformat(t) for t in times]

    return hours, temps

def plot_weather(hours, temps, city):
    plt.figure(figsize=(10,5))
    plt.plot(hours[:24], temps[:24], marker="o")  # first 24h
    plt.title(f"24-hour Temperature Forecast for {city}")
    plt.xlabel("Time")
    plt.ylabel("Temperature (°C)")
    plt.xticks(rotation=45)
    plt.grid(True)
    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    # Example: Fort Worth, TX
    lat, lon = 32.7555, -97.3308
    city = "Fort Worth"
    hours, temps = get_weather(lat, lon)
    plot_weather(hours, temps, city)
