from copy import deepcopy

import pytest

from green_sm_nyc.dashboard_export import validate_dashboard_payloads


def test_minimal_dashboard_contract_is_valid() -> None:
    payloads = _minimal_payloads()
    validate_dashboard_payloads(payloads)


def test_dashboard_contract_rejects_out_of_bounds_score() -> None:
    payloads = _minimal_payloads()
    payloads["zones"]["data"][0]["opportunity_score"] = 101

    with pytest.raises(ValueError, match="between 0 and 100"):
        validate_dashboard_payloads(payloads)


def test_dashboard_contract_rejects_missing_dataset() -> None:
    payloads = _minimal_payloads()
    del payloads["hourly"]

    with pytest.raises(ValueError, match="Missing dashboard datasets"):
        validate_dashboard_payloads(payloads)


def _minimal_payloads() -> dict:
    base = {"schema_version": "1.0.0", "row_count": 1, "data": [{"value": 1}]}
    payloads = {
        name: deepcopy(base)
        for name in ("summary", "market", "zones", "fares", "hourly", "metadata")
    }
    payloads["market"]["data"] = [{"completed_trip_share": 0.5}]
    payloads["zones"]["data"] = [{"opportunity_score": 50}]
    return payloads
