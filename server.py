"""TRMNL Weather App - Fetches weather data and pushes to TRMNL display."""

import argparse
import time
import logging

import requests
import schedule

import config
from weather import fetch_weather, parse_weather_data
from markup import generate_markup

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
log = logging.getLogger(__name__)


def update_trmnl():
    """Fetch weather data, generate markup, and push to TRMNL."""
    try:
        log.info("Fetching weather data for (%.4f, %.4f)...", config.LATITUDE, config.LONGITUDE)
        raw_data = fetch_weather(
            config.LATITUDE,
            config.LONGITUDE,
            config.TEMPERATURE_UNIT,
            config.WIND_SPEED_UNIT,
        )

        weather_data = parse_weather_data(raw_data, config.TEMPERATURE_UNIT, config.WIND_SPEED_UNIT)
        log.info(
            "Current: %s°, %s",
            weather_data["current"]["temp"],
            weather_data["current"]["description"],
        )

        # Build compact merge_variables for TRMNL (2KB limit)
        merge_vars = {
            "ct": weather_data["current"]["temp"],
            "cs": weather_data["current"]["temp_symbol"],
            "cp": weather_data["current"]["precipitation"],
            "ch": weather_data["current"]["humidity"],
            "cw": weather_data["current"]["wind_speed"],
            "cu": weather_data["current"]["wind_unit"],
            "ci": weather_data["current"]["icon"],
        }

        # Hourly data (7 slots)
        for i, h in enumerate(weather_data["hourly"]):
            merge_vars[f"ht{i}"] = h["time"]
            merge_vars[f"hp{i}"] = h["precipitation"]
            merge_vars[f"wa{i}"] = h["wind_arrow"]
            merge_vars[f"ws{i}"] = h["wind_speed"]

        # Daily data (7 days)
        for i, d in enumerate(weather_data["daily"]):
            merge_vars[f"dd{i}"] = d["day"]
            merge_vars[f"dh{i}"] = d["high"]
            merge_vars[f"dl{i}"] = d["low"]
            merge_vars[f"di{i}"] = d["icon"]

        # Push to TRMNL via webhook
        url = f"https://trmnl.com/api/custom_plugins/{config.TRMNL_PLUGIN_UUID}"
        headers = {
            "Content-Type": "application/json",
        }
        payload = {
            "merge_variables": merge_vars,
        }

        response = requests.post(url, json=payload, headers=headers, timeout=30)
        if response.status_code >= 400:
            log.error("TRMNL responded %d: %s", response.status_code, response.text)
        response.raise_for_status()
        log.info("Successfully pushed update to TRMNL (status %d)", response.status_code)

    except requests.RequestException as e:
        log.error("Request failed: %s", e)
    except Exception:
        log.exception("Unexpected error during update")


def main():
    parser = argparse.ArgumentParser(description="TRMNL Weather App")
    parser.add_argument("--once", action="store_true", help="Run once and exit (no scheduling)")
    args = parser.parse_args()

    if args.once:
        log.info("Running single update...")
        update_trmnl()
        return

    log.info("Starting scheduler (every %d hours)...", config.UPDATE_INTERVAL_HOURS)
    update_trmnl()  # Run immediately on start

    schedule.every(config.UPDATE_INTERVAL_HOURS).hours.do(update_trmnl)

    while True:
        schedule.run_pending()
        time.sleep(60)


if __name__ == "__main__":
    main()
