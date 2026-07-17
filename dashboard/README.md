# Dashboard

This is Kien Thai's static HTML/CSS/JavaScript analytical dashboard. It reads versioned JSON files generated from dbt marts; business KPI values are not embedded in the UI code.

Generate data with `uv run mobility-intel export-dashboard`, then serve this directory over HTTP (for example, `python -m http.server 8000 -d dashboard`). Opening the HTML directly with `file://` will block JSON fetches in most browsers.
