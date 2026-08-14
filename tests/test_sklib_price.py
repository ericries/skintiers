"""The structured `price:` field must only mirror a price the page already states.
check_price_backing is the mechanical enforcement of that accuracy rule."""
import sklib


CONTENT = (
    "The 30 ml bottle is listed at about $185 (accessed 2026-07-28).[^1]\n\n"
    "## Where to Buy\n- [Serum, 30 ml (brand)](https://x.com) (listed at $185.00)\n\n"
    "## Sources\n[^1]: Brand page (listed at $185.00). https://x.com (accessed 2026-07-28)\n"
)


def _meta(price):
    return {"name": "X", "slug": "x", "type": "product", "status": "published",
            "updated": "2026-07-28", "price": price}


def test_no_price_field_is_clean():
    assert sklib.check_price_backing({"type": "product"}, CONTENT) == []


def test_backed_amount_passes_integer_form():
    # $185 appears verbatim; the structured amount 185 is backed.
    errs = sklib.check_price_backing(
        _meta([{"amount": 185, "currency": "USD", "size": "30 ml",
                "as_of": "2026-07-28", "source": "^1"}]), CONTENT)
    assert errs == []


def test_backed_amount_matches_cents_form():
    # $185.00 on the page backs a 185.0 structured amount (equal to cents).
    errs = sklib.check_price_backing(_meta([{"amount": 185.0}]), CONTENT)
    assert errs == []


def test_unbacked_amount_is_error():
    # $99 never appears on the page -> must fail (the anti-invention gate).
    errs = sklib.check_price_backing(_meta([{"amount": 99}]), CONTENT)
    assert len(errs) == 1 and "no verbatim price string" in errs[0]


def test_rounded_invented_amount_is_error():
    # Page says $185; a "rounded" $190 has no verbatim backing -> fail.
    errs = sklib.check_price_backing(_meta([{"amount": 190}]), CONTENT)
    assert errs and "190" in errs[0]


def test_decimal_amount_backed_by_exact_string():
    content = "Target lists the 16 fl oz bottle at $12.89 ([see Where to Buy](#x)).[^6]\n"
    errs = sklib.check_price_backing(_meta([{"amount": 12.89, "size": "16 fl oz"}]), content)
    assert errs == []


def test_price_must_be_a_list():
    errs = sklib.check_price_backing(_meta({"amount": 185}), CONTENT)
    assert errs and "must be a list" in errs[0]


def test_entry_must_have_numeric_amount():
    errs = sklib.check_price_backing(_meta([{"currency": "USD"}]), CONTENT)
    assert errs and "numeric 'amount'" in errs[0]


def test_bad_as_of_format_is_error():
    errs = sklib.check_price_backing(
        _meta([{"amount": 185, "as_of": "July 2026"}]), CONTENT)
    assert any("as_of" in e for e in errs)


def test_multiple_entries_each_checked():
    content = "Sold at $6.00 for 30 ml, and $10.00 for 60 ml.[^1]\n"
    errs = sklib.check_price_backing(
        _meta([{"amount": 6, "size": "30 ml"}, {"amount": 10, "size": "60 ml"}]), content)
    assert errs == []
    errs2 = sklib.check_price_backing(
        _meta([{"amount": 6}, {"amount": 11}]), content)
    assert len(errs2) == 1 and "11" in errs2[0]
