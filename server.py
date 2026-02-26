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

import config
from weather import fetch_weather, parse_weather_data
from markup import generate_markup

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
log = logging.getLogger(__name__)


def build_markup():
    """Fetch weather data and return generated HTML markup."""
    log.info("Fetching weather data for (%.4f, %.4f)...", config.LATITUDE, config.LONGITUDE)
    raw = fetch_weather(
        config.LATITUDE, config.LONGITUDE,
        config.TEMPERATURE_UNIT, config.WIND_SPEED_UNIT,
    )
    data = parse_weather_data(raw, config.TEMPERATURE_UNIT, config.WIND_SPEED_UNIT)
    log.info("Current: %s°, %s", data["current"]["temp"], data["current"]["description"])
    return generate_markup(data)


def run_once(output_path="docs/index.html"):
    """Generate HTML and write to output_path (for GitHub Actions)."""
    markup = build_markup()
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(markup)
    log.info("Wrote %d bytes to %s", len(markup), output_path)


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
