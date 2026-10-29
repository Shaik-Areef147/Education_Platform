"""Smoke tests: run every page headlessly and assert no exceptions. Run: python -m pytest -q"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import pytest
from streamlit.testing.v1 import AppTest

PAGES = ["Overview", "Learner Demographics", "Enrollment Distribution", "Demographics x Preference",
         "Behavioral Insights", "Insights & Recommendations", "Data Explorer"]

ROOT = Path(__file__).resolve().parent.parent


@pytest.mark.parametrize("page", PAGES)
def test_page_renders(page):
    at = AppTest.from_file(str(ROOT / "app.py"), default_timeout=90).run()
    at.sidebar.radio[0].set_value(page).run()
    assert not at.exception, [e.value for e in at.exception]
    assert not at.error


def test_empty_filter_is_handled():
    at = AppTest.from_file(str(ROOT / "app.py"), default_timeout=90).run()
    at.sidebar.multiselect[0].set_value([]).run()
    assert not at.exception
    assert len(at.warning) >= 1
