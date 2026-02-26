"""Generate HTML markup for TRMNL e-ink display (800x480)."""

# SVG weather icons for e-ink (grayscale-friendly)
WEATHER_ICONS = {
    "clear": """<svg viewBox="0 0 48 48" fill="none" stroke="currentColor" stroke-width="2.5">
        <circle cx="24" cy="24" r="10"/>
        <line x1="24" y1="2" x2="24" y2="8"/><line x1="24" y1="40" x2="24" y2="46"/>
        <line x1="2" y1="24" x2="8" y2="24"/><line x1="40" y1="24" x2="46" y2="24"/>
        <line x1="8.3" y1="8.3" x2="12.5" y2="12.5"/><line x1="35.5" y1="35.5" x2="39.7" y2="39.7"/>
        <line x1="8.3" y1="39.7" x2="12.5" y2="35.5"/><line x1="35.5" y1="12.5" x2="39.7" y2="8.3"/>
    </svg>""",
    "mostly_clear": """<svg viewBox="0 0 48 48" fill="none" stroke="currentColor" stroke-width="2.5">
        <circle cx="20" cy="18" r="8"/>
        <line x1="20" y1="4" x2="20" y2="8"/><line x1="8" y1="18" x2="4" y2="18"/>
        <line x1="10" y1="8" x2="12.5" y2="10.5"/><line x1="30" y1="8" x2="27.5" y2="10.5"/>
        <line x1="32" y1="18" x2="34" y2="18"/>
        <path d="M16 30 Q16 24 22 24 Q22 20 28 20 Q34 20 34 26 Q38 26 38 30 Q38 34 34 34 L18 34 Q14 34 14 30 Z"/>
    </svg>""",
    "partly_cloudy": """<svg viewBox="0 0 48 48" fill="none" stroke="currentColor" stroke-width="2.5">
        <circle cx="20" cy="16" r="8"/>
        <line x1="20" y1="2" x2="20" y2="6"/><line x1="6" y1="16" x2="2" y2="16"/>
        <line x1="9" y1="6" x2="11.5" y2="8.5"/><line x1="31" y1="6" x2="28.5" y2="8.5"/>
        <line x1="34" y1="16" x2="36" y2="16"/>
        <path d="M14 32 Q14 25 21 25 Q22 20 28 20 Q35 20 35 27 Q40 27 40 32 Q40 37 35 37 L18 37 Q14 37 14 32 Z"/>
    </svg>""",
    "overcast": """<svg viewBox="0 0 48 48" fill="none" stroke="currentColor" stroke-width="2.5">
        <path d="M12 34 Q12 27 19 27 Q20 22 26 22 Q33 22 33 29 Q38 29 38 34 Q38 39 33 39 L16 39 Q12 39 12 34 Z"/>
        <path d="M20 27 Q20 21 26 21 Q27 17 32 17 Q38 17 38 23 Q42 23 42 27 Q42 30 39 31" opacity="0.5"/>
    </svg>""",
    "fog": """<svg viewBox="0 0 48 48" fill="none" stroke="currentColor" stroke-width="2.5">
        <line x1="8" y1="18" x2="40" y2="18"/><line x1="6" y1="24" x2="42" y2="24"/>
        <line x1="8" y1="30" x2="40" y2="30"/><line x1="12" y1="36" x2="36" y2="36"/>
    </svg>""",
    "drizzle": """<svg viewBox="0 0 48 48" fill="none" stroke="currentColor" stroke-width="2.5">
        <path d="M12 24 Q12 17 19 17 Q20 12 26 12 Q33 12 33 19 Q38 19 38 24 Q38 29 33 29 L16 29 Q12 29 12 24 Z"/>
        <line x1="16" y1="33" x2="15" y2="37"/><line x1="24" y1="33" x2="23" y2="37"/>
        <line x1="32" y1="33" x2="31" y2="37"/>
    </svg>""",
    "rain": """<svg viewBox="0 0 48 48" fill="none" stroke="currentColor" stroke-width="2.5">
        <path d="M12 22 Q12 15 19 15 Q20 10 26 10 Q33 10 33 17 Q38 17 38 22 Q38 27 33 27 L16 27 Q12 27 12 22 Z"/>
        <line x1="14" y1="31" x2="12" y2="38"/><line x1="21" y1="31" x2="19" y2="38"/>
        <line x1="28" y1="31" x2="26" y2="38"/><line x1="35" y1="31" x2="33" y2="38"/>
    </svg>""",
    "snow": """<svg viewBox="0 0 48 48" fill="none" stroke="currentColor" stroke-width="2.5">
        <path d="M12 22 Q12 15 19 15 Q20 10 26 10 Q33 10 33 17 Q38 17 38 22 Q38 27 33 27 L16 27 Q12 27 12 22 Z"/>
        <line x1="16" y1="32" x2="16" y2="34"/><line x1="14.5" y1="33" x2="17.5" y2="33"/>
        <line x1="24" y1="32" x2="24" y2="34"/><line x1="22.5" y1="33" x2="25.5" y2="33"/>
        <line x1="32" y1="32" x2="32" y2="34"/><line x1="30.5" y1="33" x2="33.5" y2="33"/>
        <line x1="20" y1="36" x2="20" y2="38"/><line x1="18.5" y1="37" x2="21.5" y2="37"/>
        <line x1="28" y1="36" x2="28" y2="38"/><line x1="26.5" y1="37" x2="29.5" y2="37"/>
    </svg>""",
    "showers": """<svg viewBox="0 0 48 48" fill="none" stroke="currentColor" stroke-width="2.5">
        <path d="M12 22 Q12 15 19 15 Q20 10 26 10 Q33 10 33 17 Q38 17 38 22 Q38 27 33 27 L16 27 Q12 27 12 22 Z"/>
        <line x1="15" y1="31" x2="13" y2="36"/><line x1="22" y1="31" x2="20" y2="36"/>
        <line x1="29" y1="31" x2="27" y2="36"/><line x1="36" y1="31" x2="34" y2="36"/>
        <line x1="18" y1="36" x2="16" y2="41"/><line x1="32" y1="36" x2="30" y2="41"/>
    </svg>""",
    "thunderstorm": """<svg viewBox="0 0 48 48" fill="none" stroke="currentColor" stroke-width="2.5">
        <path d="M12 20 Q12 13 19 13 Q20 8 26 8 Q33 8 33 15 Q38 15 38 20 Q38 25 33 25 L16 25 Q12 25 12 20 Z"/>
        <polyline points="22,28 18,35 24,35 20,44" stroke-width="3"/>
    </svg>""",
}


def _icon_svg(icon_name, size=48):
    """Return an SVG icon wrapped in a sized container."""
    svg = WEATHER_ICONS.get(icon_name, WEATHER_ICONS["clear"])
    return f'<div style="width:{size}px;height:{size}px;display:inline-block;vertical-align:middle">{svg}</div>'


def _icon_svg_small(icon_name):
    """Return a small icon for daily forecast."""
    return _icon_svg(icon_name, size=32)


def generate_markup(weather_data):
    """Generate full HTML markup for TRMNL display."""
    current = weather_data["current"]
    hourly = weather_data["hourly"]
    daily = weather_data["daily"]

    # Build hourly header labels (7 fixed-time labels on a 19-column grid)
    chart_hours = weather_data["chart_hours"]
    LABEL_COLS = [1, 4, 7, 10, 13, 16, 19]  # 1-indexed CSS grid-column positions
    hourly_slots_html = ""
    for i, h in enumerate(hourly):
        col = LABEL_COLS[i]
        hourly_slots_html += f"""
            <div class="hourly-slot" style="grid-column:{col}">
                <div class="hourly-time">{h["time"]}</div>
                <div class="hourly-precip">{h["precipitation"]}%</div>
            </div>"""

    # Build precipitation bar chart (19 bars from chart_hours)
    precip_bars_html = ""
    for h in chart_hours:
        bar_height = max(2, int((h["precipitation"] / 100) * 60))
        precip_bars_html += f'<div class="bar-slot"><div class="bar" style="height:{bar_height}px"></div></div>'

    # Build wind speed line graph SVG (19 data points from chart_hours)
    wind_speeds = [h["wind_speed"] for h in chart_hours]
    n = len(wind_speeds)
    min_ws = min(wind_speeds) if wind_speeds else 0
    max_ws = max(wind_speeds) if wind_speeds else 1
    ws_range = max_ws - min_ws if max_ws != min_ws else 1
    GRAPH_TOP, GRAPH_BOTTOM, SVG_H = 5, 38, 56
    x_pos = [round((i + 0.5) / n * 700) for i in range(n)]
    y_pos = [GRAPH_BOTTOM - round((ws - min_ws) / ws_range * (GRAPH_BOTTOM - GRAPH_TOP)) for ws in wind_speeds]
    points_str = " ".join(f"{x_pos[i]},{y_pos[i]}" for i in range(n))
    dots_svg = "".join(f'<circle cx="{x_pos[i]}" cy="{y_pos[i]}" r="3" fill="currentColor"/>' for i in range(n))
    LABEL_INDICES = [0, 3, 6, 9, 12, 15, 18]
    labels_svg = "".join(
        f'<text x="{x_pos[i]}" y="{SVG_H - 2}" text-anchor="middle" font-size="11">{wind_speeds[i]}</text>'
        for i in LABEL_INDICES if i < n
    )
    wind_graph_svg = (
        f'<svg viewBox="0 0 700 {SVG_H}" width="100%" height="{SVG_H}" preserveAspectRatio="none" style="display:block">'
        f'<polyline points="{points_str}" fill="none" stroke="currentColor" stroke-width="2"/>'
        f'{dots_svg}{labels_svg}</svg>'
    )

    # Build daily forecast
    daily_html = ""
    for d in daily:
        daily_html += f"""
            <div class="daily-slot">
                <div class="daily-day">{d["day"]}</div>
                <div class="daily-icon">{_icon_svg_small(d["icon"])}</div>
                <div class="daily-temps">
                    <span class="daily-high">{d["high"]}°</span>
                    <span class="daily-low">{d["low"]}°</span>
                </div>
            </div>"""

    markup = f"""<div class="weather-container">
    <style>
        .weather-container {{
            width: 800px;
            height: 480px;
            font-family: sans-serif;
            padding: 16px 20px;
            box-sizing: border-box;
            display: flex;
            flex-direction: column;
        }}

        /* Current conditions */
        .current-row {{
            display: flex;
            align-items: center;
            justify-content: space-between;
            margin-bottom: 10px;
        }}
        .current-left {{
            display: flex;
            align-items: center;
            gap: 10px;
        }}
        .current-temp {{
            font-size: 72px;
            font-weight: 700;
            line-height: 1;
        }}
        .current-temp-symbol {{
            font-size: 28px;
            font-weight: 400;
            vertical-align: super;
        }}
        .current-stats {{
            text-align: right;
            font-size: 18px;
            line-height: 1.6;
        }}

        /* Hourly section */
        .hourly-header {{
            display: grid;
            grid-template-columns: repeat(19, 1fr);
            border-top: 1px solid #888;
            padding-top: 8px;
        }}
        .hourly-slot {{
            text-align: center;
        }}
        .hourly-time {{
            font-size: 14px;
            margin-bottom: 2px;
        }}
        .hourly-precip {{
            font-size: 14px;
            font-weight: 600;
        }}

        /* Precipitation bar chart */
        .bar-chart {{
            display: grid;
            grid-template-columns: repeat(19, 1fr);
            align-items: flex-end;
            height: 62px;
            margin: 2px 0;
        }}
        .bar-slot {{
            display: flex;
            justify-content: center;
            align-items: flex-end;
            height: 100%;
        }}
        .bar {{
            width: 70%;
            background: #000;
            min-height: 2px;
        }}

        /* Wind row */
        .wind-row {{
            display: flex;
            justify-content: space-between;
            padding: 6px 0;
            border-top: 1px solid #888;
        }}
        .wind-slot {{
            flex: 1;
            text-align: center;
        }}
        .wind-arrow {{
            font-size: 22px;
            line-height: 1.2;
        }}
        .wind-speed {{
            font-size: 12px;
        }}

        /* Daily forecast */
        .daily-row {{
            display: flex;
            justify-content: space-between;
            border-top: 1px solid #888;
            padding-top: 8px;
            margin-top: auto;
        }}
        .daily-slot {{
            flex: 1;
            text-align: center;
        }}
        .daily-day {{
            font-size: 14px;
            font-weight: 600;
            margin-bottom: 4px;
        }}
        .daily-icon {{
            margin: 2px 0;
            display: flex;
            justify-content: center;
        }}
        .daily-temps {{
            font-size: 14px;
        }}
        .daily-high {{
            font-weight: 700;
        }}
        .daily-low {{
            margin-left: 4px;
            opacity: 0.6;
        }}
    </style>

    <div class="current-row">
        <div class="current-left">
            {_icon_svg(current["icon"], size=80)}
            <div class="current-temp">
                {current["temp"]}<span class="current-temp-symbol">{current["temp_symbol"]}</span>
            </div>
        </div>
        <div class="current-stats">
            Feels Like: {current["feels_like"]}{current["temp_symbol"]}<br>
            Precipitation: {current["precipitation"]}%<br>
            Humidity: {current["humidity"]}%<br>
            Wind: {current["wind_speed"]} {current["wind_unit"]}
        </div>
    </div>

    <div class="hourly-header">{hourly_slots_html}
    </div>

    <div class="bar-chart">{precip_bars_html}
    </div>

    <div class="wind-row">{wind_graph_svg}
    </div>

    <div class="daily-row">{daily_html}
    </div>
</div>"""

    return markup
