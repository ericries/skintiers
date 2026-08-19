"""`sk add-video` must insert a videos: card via the YAML library (escaping
never hand-built) and enforce the guardrails the video crons apply by hand:
attach-page existence, video-id dedup, dropping unresolvable `related` slugs,
em/en-dash rejection, and re-parsing the frontmatter before write.
"""
import importlib.machinery
import importlib.util
import pathlib
import sys
import types

import frontmatter
import yaml

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import sklib  # noqa: E402


def _load_sk():
    loader = importlib.machinery.SourceFileLoader("sk_cli", str(ROOT / "scripts" / "sk"))
    spec = importlib.util.spec_from_loader("sk_cli", loader)
    mod = importlib.util.module_from_spec(spec)
    loader.exec_module(mod)
    return mod


def _page(data_dir, typ, slug, extra_fm=""):
    (data_dir / typ).mkdir(parents=True, exist_ok=True)
    (data_dir / typ / f"{slug}.md").write_text(
        f"---\nname: {slug}\nslug: {slug}\ntype: {typ[:-1]}\nstatus: published\n"
        f"updated: '2026-08-19'\n{extra_fm}---\n\nBody about {slug}.\n"
    )


def _args(attach, **kw):
    base = dict(attach=attach, id="abc123XYZ00", title="How retinoids work",
                creator="Dr Example", creator_slug="dr-example", credential="dermatologist",
                thesis="A clear thesis.", posted="2026-08-07", platform="YouTube",
                url=None, related="", note=None)
    base.update(kw)
    return types.SimpleNamespace(**base)


def test_add_video_inserts_and_escapes(tmp_path, monkeypatch):
    monkeypatch.setattr(sklib, "DATA_DIR", tmp_path)
    _page(tmp_path, "ingredients", "retinoids")
    sk = _load_sk()
    tricky = "Creator's point: it's a 'quoted' thesis with a colon: yes"
    assert sk.cmd_add_video(_args("retinoids", thesis=tricky)) == 0
    post = frontmatter.load(tmp_path / "ingredients" / "retinoids.md")
    card = post.metadata["videos"][0]
    assert card["thesis"] == tricky  # round-trips exactly through YAML
    assert card["url"] == "https://www.youtube.com/watch?v=abc123XYZ00"  # auto-derived
    assert card["platform"] == "YouTube"


def test_add_video_rejects_missing_page(tmp_path, monkeypatch):
    monkeypatch.setattr(sklib, "DATA_DIR", tmp_path)
    sk = _load_sk()
    assert sk.cmd_add_video(_args("no-such-slug")) == 1  # no page -> error, nothing written


def test_add_video_dedups_by_id(tmp_path, monkeypatch):
    monkeypatch.setattr(sklib, "DATA_DIR", tmp_path)
    _page(tmp_path, "ingredients", "niacinamide")
    sk = _load_sk()
    assert sk.cmd_add_video(_args("niacinamide")) == 0
    # same id again -> treated as dup, returns 0 without adding a second card
    assert sk.cmd_add_video(_args("niacinamide", title="different title")) == 0
    post = frontmatter.load(tmp_path / "ingredients" / "niacinamide.md")
    assert len(post.metadata["videos"]) == 1


def test_add_video_drops_unknown_related(tmp_path, monkeypatch):
    monkeypatch.setattr(sklib, "DATA_DIR", tmp_path)
    _page(tmp_path, "ingredients", "vitamin-c")
    _page(tmp_path, "ingredients", "ferulic-acid")
    sk = _load_sk()
    assert sk.cmd_add_video(_args("vitamin-c", related="ferulic-acid,ghost-slug")) == 0
    post = frontmatter.load(tmp_path / "ingredients" / "vitamin-c.md")
    assert post.metadata["videos"][0]["related"] == ["ferulic-acid"]  # ghost dropped


def test_add_video_rejects_em_dash(tmp_path, monkeypatch):
    monkeypatch.setattr(sklib, "DATA_DIR", tmp_path)
    _page(tmp_path, "ingredients", "azelaic-acid")
    sk = _load_sk()
    assert sk.cmd_add_video(_args("azelaic-acid", thesis="works well — for rosacea")) == 1
    assert "videos" not in frontmatter.load(
        tmp_path / "ingredients" / "azelaic-acid.md").metadata  # nothing written


def test_add_video_appends_to_existing_block(tmp_path, monkeypatch):
    monkeypatch.setattr(sklib, "DATA_DIR", tmp_path)
    _page(tmp_path, "ingredients", "spf",
          extra_fm="videos:\n- title: First\n  creator: X\n  url: u\n")
    sk = _load_sk()
    assert sk.cmd_add_video(_args("spf", id="secondVID99")) == 0
    post = frontmatter.load(tmp_path / "ingredients" / "spf.md")
    assert [v["title"] for v in post.metadata["videos"]] == ["First", "How retinoids work"]


def test_add_video_frontmatter_stays_valid(tmp_path, monkeypatch):
    monkeypatch.setattr(sklib, "DATA_DIR", tmp_path)
    _page(tmp_path, "ingredients", "peptides")
    sk = _load_sk()
    assert sk.cmd_add_video(_args("peptides")) == 0
    text = (tmp_path / "ingredients" / "peptides.md").read_text()
    # the body after the closing --- must be preserved
    assert text.rstrip().endswith("Body about peptides.")
    yaml.safe_load(text[4:text.index("\n---", 3)])  # frontmatter parses
