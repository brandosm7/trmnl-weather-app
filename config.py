# TRMNL Weather App Configuration
import os

# Location coordinates
LATITUDE = float(os.environ.get("LATITUDE", "42.77275"))
LONGITUDE = float(os.environ.get("LONGITUDE", "-86.211787"))

# TRMNL Private Plugin UUID (from your TRMNL account)
TRMNL_PLUGIN_UUID = os.environ.get("TRMNL_PLUGIN_UUID", "c0d6d16f-2184-4cb1-b66b-c5fcb56783de")

# TRMNL API Key (from your TRMNL account)
TRMNL_API_KEY = os.environ.get("TRMNL_API_KEY", "user_0f33hpqsdxfx0v8akvc7ilrg")

# Units: "fahrenheit" or "celsius" for temperature, "mph" or "kmh" for wind
TEMPERATURE_UNIT = os.environ.get("TEMPERATURE_UNIT", "fahrenheit")
WIND_SPEED_UNIT = os.environ.get("WIND_SPEED_UNIT", "mph")

# Update interval in hours
UPDATE_INTERVAL_HOURS = 3
