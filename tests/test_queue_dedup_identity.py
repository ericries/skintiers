"""`page_exists_for` is the guard that stops `sk queue-add` re-queuing work the
site has already done. It must resolve a queued NAME to a page by the site's own
identity rules (frontmatter `name:` and `aliases:`), not by guessing a filename.

Why these exist. Five duplicate queue rows reached queue heads in one week, and
one of them produced a duplicate PAGE. The clearest case: a row for
"Dr. Sheila Farhang" sat pending while data/people/sheila-farhang.md had existed
since August carrying exactly that `name:`. The guard slugified the queue name to
"dr-sheila-farhang", found no such file, and waved the row through. Meanwhile
`sklib.find_entities` resolved the very same string to the right page at score 95
(exact name). The identity index existed; the guard just was not using it.

The guard must stay CONSERVATIVE. find_entities also returns weak partial matches
(it scored "Luzu (luliconazole 1% cream)" against an unrelated cream at 69), and
treating those as "already covered" would silently drop real work. Only
exact-grade matches, which its docstring defines as >= 90, may block an add.
"""
import pathlib
import sys

import frontmatter

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import sklib  # noqa: E402


def _page(root, sub, slug, typ, name=None, aliases=None):
    d = pathlib.Path(root) / sub
    d.mkdir(parents=True, exist_ok=True)
    post = frontmatter.Post(
        "body", name=name or slug, slug=slug, type=typ,
        status="published", updated="2026-01-01",
        **({"aliases": aliases} if aliases else {}))
    with open(d / f"{slug}.md", "wb") as f:
        frontmatter.dump(post, f)


def test_exact_frontmatter_name_is_found_even_when_the_slug_differs(tmp_path):
    """The Sheila Farhang case: slug omits the honorific the queue row carries."""
    _page(tmp_path, "people", "sheila-farhang", "person", name="Dr. Sheila Farhang")
    assert sklib.page_exists_for(tmp_path, "Dr. Sheila Farhang", "person") is True


def test_an_alias_is_found(tmp_path):
    """Regional and brand-variant names are exactly what `aliases:` is for."""
    _page(tmp_path, "ingredients", "vitamin-c", "ingredient",
          name="Vitamin C (forms and derivatives)", aliases=["Ascorbic acid"])
    assert sklib.page_exists_for(tmp_path, "Ascorbic acid", "ingredient") is True


def test_a_merely_similar_name_does_not_block_an_add(tmp_path):
    """Must fail safe. A weak partial match is not evidence the work is done;
    treating it as such would silently discard genuine queue items."""
    _page(tmp_path, "products", "vtama-tapinarof-cream", "product",
          name="VTAMA (tapinarof) cream")
    assert sklib.page_exists_for(tmp_path, "Luzu (luliconazole 1% cream)", "product") is False


def test_unrelated_name_is_not_found(tmp_path):
    _page(tmp_path, "ingredients", "retinol", "ingredient", name="Retinol")
    assert sklib.page_exists_for(tmp_path, "Niacinamide", "ingredient") is False


def test_slug_match_still_works(tmp_path):
    """Pre-existing behaviour: the plain slugified name."""
    _page(tmp_path, "ingredients", "squalane", "ingredient", name="Squalane")
    assert sklib.page_exists_for(tmp_path, "Squalane", "ingredient") is True


def test_parenthetical_descriptor_is_still_stripped(tmp_path):
    """Pre-existing behaviour: the '<Existing thing> (descriptor)' harvest shape."""
    _page(tmp_path, "ingredients", "hydroquinone", "ingredient", name="Hydroquinone")
    assert sklib.page_exists_for(
        tmp_path, "Hydroquinone (topical depigmenting agent)", "ingredient") is True


def test_type_is_respected(tmp_path):
    """A person page must not satisfy a product row of the same name."""
    _page(tmp_path, "people", "la-roche-posay", "person", name="La Roche-Posay")
    assert sklib.page_exists_for(tmp_path, "La Roche-Posay", "product") is False


def test_unknown_type_is_false_not_an_error(tmp_path):
    assert sklib.page_exists_for(tmp_path, "Anything", "not-a-type") is False
