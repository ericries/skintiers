"""price_view_for formats the structured price for the product template."""
import build


def test_whole_dollar_amount_has_no_cents():
    view = build.price_view_for({"price": [{"amount": 185, "size": "30 ml"}]})
    assert len(view) == 1
    assert view[0]["amount"] == "$185"
    assert view[0]["size"] == "30 ml"
    assert view[0]["currency"] == "USD"


def test_cents_are_kept():
    view = build.price_view_for({"price": [{"amount": 12.89}]})
    assert view[0]["amount"] == "$12.89"


def test_thousands_separator():
    view = build.price_view_for({"price": [{"amount": 1200}]})
    assert view[0]["amount"] == "$1,200"


def test_as_of_passthrough():
    view = build.price_view_for(
        {"price": [{"amount": 18, "as_of": "2026-07-28", "size": "50 ml"}]})
    assert view[0]["as_of"] == "2026-07-28"


def test_no_price_returns_empty():
    assert build.price_view_for({}) == []
    assert build.price_view_for({"price": None}) == []


def test_malformed_entry_skipped():
    view = build.price_view_for({"price": [{"currency": "USD"}, {"amount": 9}]})
    assert len(view) == 1 and view[0]["amount"] == "$9"
