"""TRMNL Weather App server.

Modes:
  python server.py --once   Generate HTML to docs/index.html and exit (used by GitHub Actions)
  python server.py          Run a local HTTP polling server on PORT (for local testing)
"""

import argparse
import logging
import os
import time
from http.server import BaseHTTPRequestHandler, HTTPServer

import requests

import config
from weather import fetch_weather, parse_weather_data
from markup import generate_markup, build_merge_variables

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
log = logging.getLogger(__name__)


def fetch_data():
    """Fetch and parse weather data."""
    log.info("Fetching weather data for (%.4f, %.4f)...", config.LATITUDE, config.LONGITUDE)
    raw = fetch_weather(
        config.LATITUDE, config.LONGITUDE,
        config.TEMPERATURE_UNIT, config.WIND_SPEED_UNIT,
    )
    data = parse_weather_data(raw, config.TEMPERATURE_UNIT, config.WIND_SPEED_UNIT)
    log.info("Current: %s°, %s", data["current"]["temp"], data["current"]["description"])
    return data


def build_markup():
    """Fetch weather data and return generated HTML markup."""
    data = fetch_data()
    return generate_markup(data)


def post_to_trmnl(merge_variables):
    """POST merge_variables to TRMNL webhook API."""
    if not config.TRMNL_PLUGIN_UUID:
        log.warning("TRMNL_PLUGIN_UUID not set, skipping webhook POST")
        return

    url = f"https://usetrmnl.com/api/custom_plugins/{config.TRMNL_PLUGIN_UUID}"
    headers = {"Authorization": f"Bearer {config.TRMNL_API_KEY}"}
    payload = {"merge_variables": merge_variables}

    log.info("Posting merge_variables to TRMNL webhook...")
    resp = requests.post(url, json=payload, headers=headers, timeout=30)
    log.info("TRMNL response: %s %s", resp.status_code, resp.text[:200])
    resp.raise_for_status()


def run_once(output_path="docs/index.html"):
    """Generate HTML, write to output_path, and POST to TRMNL webhook."""
    data = fetch_data()
    markup = generate_markup(data)
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(markup)
    log.info("Wrote %d bytes to %s", len(markup), output_path)

    # Send merge variables to TRMNL webhook
    merge_vars = build_merge_variables(data)
    post_to_trmnl(merge_vars)


# Simple in-memory cache for the polling server
_cached_markup = None
_cache_time = 0
CACHE_TTL = config.UPDATE_INTERVAL_HOURS * 3600


def get_markup_cached():
    global _cached_markup, _cache_time
    now = time.time()
    if _cached_markup is None or (now - _cache_time) > CACHE_TTL:
        try:
            _cached_markup = build_markup()
            _cache_time = now
        except Exception:
            log.exception("Failed to fetch weather data")
            if _cached_markup is None:
                _cached_markup = "<div>Weather data unavailable</div>"
    return _cached_markup


class WeatherHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        markup = get_markup_cached()
        body = markup.encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, fmt, *args):
        log.info("Poll: " + fmt, *args)


def run_server():
    """Run a local HTTP server for testing."""
    get_markup_cached()  # warm up cache
    server = HTTPServer(("0.0.0.0", config.PORT), WeatherHandler)
    log.info("Serving on http://localhost:%d  (cache TTL: %dh)", config.PORT, config.UPDATE_INTERVAL_HOURS)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        log.info("Shutting down.")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--once", action="store_true", help="Generate HTML to docs/index.html and exit")
    args = parser.parse_args()

    if args.once:
        run_once()
    else:
        run_server()


if __name__ == "__main__":
    main()
