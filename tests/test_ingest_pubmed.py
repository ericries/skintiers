import sys, pathlib
ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import ingest_pubmed as ing


def test_build_term_has_quality_filter():
    term = ing.build_term()
    # journal allowlist + rigorous study types are ANDed in
    assert '"J Am Acad Dermatol"[Journal]' in term
    assert '"Randomized Controlled Trial"[Publication Type]' in term
    # must be about skin, and procedures are excluded
    assert "skin[Title/Abstract]" in term
    assert 'NOT (' in term and '"laser"[Title]' in term
    # recency + human + English gates present
    assert '[dp]) AND English[lang] AND humans[mh]' in term


def test_pmid_extraction_from_source_urls():
    text = ("see https://pubmed.ncbi.nlm.nih.gov/42235049/ and "
            "https://pubmed.ncbi.nlm.nih.gov/42163060/")
    assert set(ing._PMID_RE.findall(text)) == {"42235049", "42163060"}


def test_candidate_name_is_stable_and_traceable():
    s = {"first_author": "Draelos", "year": "2026",
         "title": "A Botanical Anti-Inflammatory Moisturizer in Rosacea", "pmid": "42163060"}
    name = ing.candidate_name(s)
    assert name.startswith("Draelos 2026 ")
    assert "(PMID 42163060)" in name        # PMID embedded -> stable dedupe key
