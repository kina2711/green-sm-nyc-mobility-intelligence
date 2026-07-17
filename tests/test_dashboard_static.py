from pathlib import Path

from green_sm_nyc.config import DASHBOARD_DIR


def test_dashboard_entrypoint_references_local_assets() -> None:
    html = (DASHBOARD_DIR / "index.html").read_text(encoding="utf-8")

    assert 'href="styles.css"' in html
    assert 'src="app.js"' in html
    assert "Observed facts" in html
    assert "not a profitability or unmet-demand model" in html


def test_javascript_loads_every_versioned_dataset() -> None:
    javascript = (DASHBOARD_DIR / "app.js").read_text(encoding="utf-8")

    for dataset in ("summary", "market", "zones", "fares", "hourly", "metadata"):
        assert dataset in javascript
    assert "schema_version" in javascript
    assert "fetch(`data/${name}.json`)" in javascript


def test_published_dashboard_contracts_are_available() -> None:
    gitignore = Path(".gitignore").read_text(encoding="utf-8")

    assert "dashboard/data/*.json" not in gitignore
    expected = {
        f"{name}.json" for name in ("summary", "market", "zones", "fares", "hourly", "metadata")
    }
    assert expected <= {path.name for path in (DASHBOARD_DIR / "data").glob("*.json")}
    assert "data/raw/" in gitignore
    assert "data/warehouse/" in gitignore
