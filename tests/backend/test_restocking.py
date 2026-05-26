"""
Tests for restocking API endpoints.
"""
from datetime import date, timedelta

import pytest


TREND_RANK = {"increasing": 0, "stable": 1, "decreasing": 2}


class TestRestockCandidatesEndpoint:
    """Test suite for the restocking candidates endpoint."""

    def test_get_all_candidates(self, client):
        """Test getting restocking candidates."""
        response = client.get("/api/restocking/items")
        assert response.status_code == 200

        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0

        first = data[0]
        assert "item_sku" in first
        assert "item_name" in first
        assert "recommended_qty" in first
        assert "unit_cost" in first
        assert "line_cost" in first
        assert "lead_time_days" in first
        assert "trend" in first

    def test_candidates_only_have_positive_gap(self, client):
        """Candidates must always recommend at least one unit (gap > 0)."""
        response = client.get("/api/restocking/items")
        data = response.json()

        for candidate in data:
            assert candidate["recommended_qty"] > 0
            assert candidate["forecasted_demand"] > candidate["current_demand"]
            assert candidate["recommended_qty"] == (
                candidate["forecasted_demand"] - candidate["current_demand"]
            )

    def test_decreasing_demand_item_excluded(self, client):
        """The decreasing-demand motor (gap <= 0) must not be a candidate."""
        response = client.get("/api/restocking/items")
        data = response.json()

        skus = [c["item_sku"] for c in data]
        assert "MTR-304" not in skus

    def test_line_cost_calculation(self, client):
        """line_cost must equal recommended_qty * unit_cost (to the cent)."""
        response = client.get("/api/restocking/items")
        data = response.json()

        for candidate in data:
            expected = round(candidate["recommended_qty"] * candidate["unit_cost"], 2)
            assert abs(candidate["line_cost"] - expected) < 0.01

    def test_candidates_sorted_by_urgency(self, client):
        """Candidates are pre-sorted: increasing-trend first, then gap descending."""
        response = client.get("/api/restocking/items")
        data = response.json()

        # First item should be the highest-urgency trend present.
        assert data[0]["trend"] == "increasing"

        for prev, curr in zip(data, data[1:]):
            prev_rank = TREND_RANK[prev["trend"]]
            curr_rank = TREND_RANK[curr["trend"]]
            # Trend rank is non-decreasing across the list.
            assert prev_rank <= curr_rank
            # Within the same trend, gap is non-increasing.
            if prev_rank == curr_rank:
                assert prev["recommended_qty"] >= curr["recommended_qty"]


class TestSubmitRestockOrderEndpoint:
    """Test suite for submitting and retrieving restocking orders."""

    def _payload(self):
        return {
            "budget": 5000,
            "items": [
                {
                    "sku": "FLT-405",
                    "name": "Oil Filter Cartridge",
                    "quantity": 150,
                    "unit_cost": 12.0,
                    "lead_time_days": 7,
                },
                {
                    "sku": "GSK-203",
                    "name": "High-Temperature Gasket",
                    "quantity": 100,
                    "unit_cost": 18.75,
                    "lead_time_days": 18,
                },
            ],
        }

    def test_submit_returns_created(self, client):
        """Submitting a restocking order returns 201 with a computed order."""
        response = client.post("/api/restocking/orders", json=self._payload())
        assert response.status_code == 201

        order = response.json()
        assert order["order_number"].startswith("RSO-2025-")
        assert order["status"] == "Submitted"
        assert len(order["items"]) == 2

    def test_submit_computes_totals_and_lead_time(self, client):
        """Server computes total_value, line costs, and max lead time."""
        response = client.post("/api/restocking/orders", json=self._payload())
        order = response.json()

        # 150 * 12.00 + 100 * 18.75 = 3675.00
        assert abs(order["total_value"] - 3675.0) < 0.01
        assert order["max_lead_time_days"] == 18

        for item in order["items"]:
            expected = round(item["quantity"] * item["unit_cost"], 2)
            assert abs(item["line_cost"] - expected) < 0.01

    def test_submit_computes_expected_delivery(self, client):
        """expected_delivery = created_date + max lead time."""
        response = client.post("/api/restocking/orders", json=self._payload())
        order = response.json()

        created = date.fromisoformat(order["created_date"])
        expected = date.fromisoformat(order["expected_delivery"])
        assert expected == created + timedelta(days=order["max_lead_time_days"])

    def test_submit_empty_items_rejected(self, client):
        """An order with no items returns a 400 error."""
        response = client.post(
            "/api/restocking/orders", json={"budget": 1000, "items": []}
        )
        assert response.status_code == 400
        assert "detail" in response.json()

    def test_submit_missing_budget_rejected(self, client):
        """A malformed payload (missing budget) returns a 422 validation error."""
        response = client.post(
            "/api/restocking/orders",
            json={"items": [{"sku": "X", "name": "X", "quantity": 1, "unit_cost": 1.0, "lead_time_days": 1}]},
        )
        assert response.status_code == 422

    def test_submitted_order_appears_in_list(self, client):
        """A submitted order is retrievable via the orders list endpoint."""
        post_response = client.post("/api/restocking/orders", json=self._payload())
        created_number = post_response.json()["order_number"]

        get_response = client.get("/api/restocking/orders")
        assert get_response.status_code == 200

        data = get_response.json()
        assert isinstance(data, list)
        numbers = [o["order_number"] for o in data]
        assert created_number in numbers
