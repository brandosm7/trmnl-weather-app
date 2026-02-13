import requests
from datetime import datetime


WEATHER_CODE_MAP = {
    0: ("Clear", "clear"),
    1: ("Mostly Clear", "mostly_clear"),
    2: ("Partly Cloudy", "partly_cloudy"),
    3: ("Overcast", "overcast"),
    45: ("Fog", "fog"),
    48: ("Freezing Fog", "fog"),
    51: ("Light Drizzle", "drizzle"),
    53: ("Drizzle", "drizzle"),
    55: ("Heavy Drizzle", "drizzle"),
    56: ("Freezing Drizzle", "drizzle"),
    57: ("Heavy Freezing Drizzle", "drizzle"),
    61: ("Light Rain", "rain"),
    63: ("Rain", "rain"),
    65: ("Heavy Rain", "rain"),
    66: ("Freezing Rain", "rain"),
    67: ("Heavy Freezing Rain", "rain"),
    71: ("Light Snow", "snow"),
    73: ("Snow", "snow"),
    75: ("Heavy Snow", "snow"),
    77: ("Snow Grains", "snow"),
    80: ("Light Showers", "showers"),
    81: ("Showers", "showers"),
    82: ("Heavy Showers", "showers"),
    85: ("Light Snow Showers", "snow"),
    86: ("Heavy Snow Showers", "snow"),
    95: ("Thunderstorm", "thunderstorm"),
    96: ("Thunderstorm w/ Hail", "thunderstorm"),
    99: ("Thunderstorm w/ Heavy Hail", "thunderstorm"),
}


def fetch_weather(latitude, longitude, temperature_unit="fahrenheit", wind_speed_unit="mph"):
    """Fetch weather data from Open-Meteo API."""
    url = (
        f"https://api.open-meteo.com/v1/forecast"
        f"?latitude={latitude}&longitude={longitude}"
        f"&hourly=temperature_2m,precipitation_probability,relative_humidity_2m,"
        f"wind_speed_10m,wind_direction_10m,weather_code"
        f"&daily=weather_code,temperature_2m_max,temperature_2m_min"
        f"&temperature_unit={temperature_unit}"
        f"&wind_speed_unit={wind_speed_unit}"
        f"&timezone=auto&forecast_days=8"
    )
    response = requests.get(url, timeout=30)
    response.raise_for_status()
    return response.json()


def _find_current_hour_index(times):
    """Find the index of the current hour in the hourly time list."""
    now = datetime.now()
    current_hour_str = now.strftime("%Y-%m-%dT%H:00")
    try:
        return times.index(current_hour_str)
    except ValueError:
        # Fallback: find closest hour
        for i, t in enumerate(times):
            if t >= current_hour_str:
                return max(0, i - 1)
        return 0


def _find_today_index(dates):
    """Find the index of today in the daily date list."""
    today_str = datetime.now().strftime("%Y-%m-%d")
    try:
        return dates.index(today_str)
    except ValueError:
        return 0


def _wind_direction_label(degrees):
    """Convert wind direction degrees to compass arrow character and label."""
    directions = ["N", "NE", "E", "SE", "S", "SW", "W", "NW"]
    # Arrow characters pointing in the direction the wind is blowing FROM
    # (meteorological convention: wind direction = where it comes from)
    arrows = ["↑", "↗", "→", "↘", "↓", "↙", "←", "↖"]
    idx = round(degrees / 45) % 8
    return arrows[idx], directions[idx]


def parse_weather_data(data, temperature_unit="fahrenheit", wind_speed_unit="mph"):
    """Parse Open-Meteo response into structured weather data."""
    hourly = data["hourly"]
    daily = data["daily"]

    temp_symbol = "°F" if temperature_unit == "fahrenheit" else "°C"
    wind_unit = wind_speed_unit

    # Current conditions (nearest hour)
    current_idx = _find_current_hour_index(hourly["time"])

    current = {
        "temp": round(hourly["temperature_2m"][current_idx]),
        "temp_symbol": temp_symbol,
        "precipitation": hourly["precipitation_probability"][current_idx] or 0,
        "humidity": hourly["relative_humidity_2m"][current_idx] or 0,
        "wind_speed": round(hourly["wind_speed_10m"][current_idx] or 0),
        "wind_unit": wind_unit,
        "weather_code": hourly["weather_code"][current_idx] or 0,
    }

    code_info = WEATHER_CODE_MAP.get(current["weather_code"], ("Unknown", "clear"))
    current["description"] = code_info[0]
    current["icon"] = code_info[1]

    # Hourly forecast: next 7 slots at 3-hour intervals (~21 hours)
    hourly_forecast = []
    for i in range(7):
        idx = current_idx + (i * 3)
        if idx >= len(hourly["time"]):
            break
        time_str = hourly["time"][idx]
        dt = datetime.strptime(time_str, "%Y-%m-%dT%H:%M")
        hour_label = dt.strftime("%I %p").lstrip("0")

        wind_deg = hourly["wind_direction_10m"][idx] or 0
        arrow, direction = _wind_direction_label(wind_deg)

        hourly_forecast.append({
            "time": hour_label,
            "precipitation": hourly["precipitation_probability"][idx] or 0,
            "wind_speed": round(hourly["wind_speed_10m"][idx] or 0),
            "wind_direction": direction,
            "wind_arrow": arrow,
        })

    # Daily forecast: 7 days starting from today
    today_idx = _find_today_index(daily["time"])
    daily_forecast = []
    for i in range(7):
        idx = today_idx + i
        if idx >= len(daily["time"]):
            break
        date_str = daily["time"][idx]
        dt = datetime.strptime(date_str, "%Y-%m-%d")
        if i == 0:
            day_label = "Today"
        else:
            day_label = dt.strftime("%a")

        weather_code = daily["weather_code"][idx] or 0
        code_info = WEATHER_CODE_MAP.get(weather_code, ("Unknown", "clear"))

        daily_forecast.append({
            "day": day_label,
            "high": round(daily["temperature_2m_max"][idx]),
            "low": round(daily["temperature_2m_min"][idx]),
            "icon": code_info[1],
            "description": code_info[0],
            "temp_symbol": temp_symbol,
        })

    return {
        "current": current,
        "hourly": hourly_forecast,
        "daily": daily_forecast,
    }
