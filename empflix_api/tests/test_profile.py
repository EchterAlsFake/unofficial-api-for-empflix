from pathlib import Path
import pytest
from empflix_api.api import Profile, Pornstar

ROOT_DIR = Path(__file__).resolve().parents[2]
SAMPLE_PROFILE_PATH = ROOT_DIR / "sample_profile.html"
SAMPLE_PORNSTAR_PATH = ROOT_DIR / "sample_profile_from_pornstar.html"


def test_profile_extract_user():
    assert SAMPLE_PROFILE_PATH.exists()
    html_content = SAMPLE_PROFILE_PATH.read_text(encoding="utf-8")

    data = Profile._extract_html(html_content, url="https://www.empflix.com/profile/DoghousePassword")
    assert data["name"] == "DoghousePassword"
    assert data["total_videos"] == 0
    assert data["total_videos_str"] == "0"
    assert data["subscribers"] == "4"
    assert data["subscribers_count"] == 4
    assert data["entity_id"] == "4288566346"


def test_profile_extract_pornstar():
    assert SAMPLE_PORNSTAR_PATH.exists()
    html_content = SAMPLE_PORNSTAR_PATH.read_text(encoding="utf-8")

    data = Profile._extract_html(html_content, url="https://www.empflix.com/profile/dani-daniels")
    assert data["name"] == "Dani Daniels"
    assert data["thumbnail_url"].startswith("https://img.empflix.com/")
    assert data["total_videos"] == 147
    assert data["total_videos_str"] == "147"
    assert data["subscribers"] == "98"
    assert data["subscribers_count"] == 98
    assert data["entity_id"] == "3236785"

    # Pornstar shares same extraction logic
    p_data = Pornstar._extract_html(html_content, url="https://www.empflix.com/profile/dani-daniels")
    assert p_data == data
