"""`source_cache.put` refuses to store a bot-block or challenge page.

Why it exists. The cache is the project's answer to "verify this later even if
the live site stops serving it", and a critic is told to check quotes against it
before re-fetching. That only works if what is in the cache is the page.

Found 2026-11-27. A free curl of a La Roche-Posay brand URL returned 5,741 bytes
of Cloudflare interstitial titled "Just a moment..." and `put` stored it without
complaint. The entry then LOOKED like a cached primary source: right url, right
key, plausible size. It contained none of the figures the citing page attributed
to it, and any later check against it would have failed for the wrong reason, or
worse, satisfied a rule that merely asks whether the cache file exists.

Refusing at write time is the only place that helps. Once a challenge page is in
the cache it is indistinguishable, to any later reader, from a real one.
"""
import pathlib
import sys

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import source_cache  # noqa: E402

URL = "https://www.example-brand.com/p/some-product"

CLOUDFLARE = (
    '<!DOCTYPE html><html lang="en-US"><head><title>Just a moment...</title>'
    '<meta http-equiv="X-UA-Compatible" content="IE=Edge">'
    '<meta name="robots" content="noindex,nofollow"></head><body>'
    '<div class="main-wrapper"><h1>Enable JavaScript and cookies to continue</h1>'
    "</div></body></html>"
)


def test_cloudflare_interstitial_is_refused(tmp_path):
    with pytest.raises(ValueError, match="(?i)block|challenge|bot"):
        source_cache.put(URL, CLOUDFLARE, cache_dir=tmp_path)
    assert not list(tmp_path.rglob("*.md")), "nothing may be written"


@pytest.mark.parametrize(
    "body",
    [
        "<html><head><title>Access Denied</title></head><body>Denied</body></html>",
        "<html><head><title>Robot or human?</title></head><body>check</body></html>",
        "<html><head><title>Attention Required! | Cloudflare</title></head>"
        "<body>Sorry, you have been blocked</body></html>",
        "<html><head><title>Pardon Our Interruption</title></head>"
        "<body>you are a bot</body></html>",
    ],
)
def test_other_known_block_pages_are_refused(body, tmp_path):
    with pytest.raises(ValueError):
        source_cache.put(URL, body, cache_dir=tmp_path)


def test_a_real_product_page_still_caches(tmp_path):
    body = (
        "<html><head><title>Toleriane Double Repair UV SPF 30</title></head><body>"
        "<p>$25.99</p><p>3.38 fl oz / 100 mL</p><p>Broad spectrum SPF 30</p>"
        "<p>Avobenzone 3%, Homosalate 5%, Octisalate 5%, Octocrylene 7%</p>"
        "</body></html>"
    )
    out = source_cache.put(URL, body, cache_dir=tmp_path)
    assert out is not None and out.exists()
    assert "25.99" in out.read_text()


def test_the_word_blocked_in_real_prose_does_not_trip_it(tmp_path):
    """A sunscreen page legitimately says UV is 'blocked'."""
    body = (
        "<html><head><title>Mineral Sunscreen SPF 50</title></head><body>"
        "<p>UVA and UVB rays are blocked by zinc oxide. Not a challenge to apply.</p>"
        "</body></html>"
    )
    assert source_cache.put(URL, body, cache_dir=tmp_path) is not None


# --- rate-limit and HTTP-error bodies ---------------------------------------
# The title/marker scan above missed the very next real case, 2026-11-27: a
# retailer answered HTTP 429 with an 18-byte body reading exactly
# "local_rate_limited", and it cached without complaint.
#
# A size floor is NOT the fix. The cache legitimately holds tiny curated
# extracts: 49 bytes of "(c) 2026 Crown Laboratories Inc., a Revance Company"
# is precisely the fact a brand-ownership line is sourced to. The rule has to
# be about a body that IS an error, not a body that is short.

@pytest.mark.parametrize(
    "body",
    [
        "local_rate_limited",
        "Too Many Requests",
        "429 Too Many Requests",
        "error code: 1015",
        "  rate limited \n",
        "Service Unavailable",
        "Bad Gateway",
    ],
)
def test_bare_http_error_body_is_refused(body, tmp_path):
    with pytest.raises(ValueError):
        source_cache.put(URL, body, cache_dir=tmp_path)


@pytest.mark.parametrize(
    "body",
    [
        "© 2026 Crown Laboratories Inc., a Revance Company",
        "Kenvue, maker of Neutrogena®, Aveeno®, OGX®, and Zyrtec®",
        "Round Lab corporate site footer, business registration info.",
    ],
)
def test_small_curated_extracts_still_cache(body, tmp_path):
    """Real entries in the cache today; a size floor would have killed these."""
    assert source_cache.put(URL, body, cache_dir=tmp_path) is not None
