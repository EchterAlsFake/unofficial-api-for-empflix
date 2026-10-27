from pathlib import Path
import pytest
from empflix_api.api import Video
from empflix_api.modules.consts import extractor_video_list

SAMPLE_HTML_PATH = Path(__file__).resolve().parents[2] / "video_sample.html"


def test_video_extract_html():
    assert SAMPLE_HTML_PATH.exists(), f"Sample HTML not found at {SAMPLE_HTML_PATH}"
    html_content = SAMPLE_HTML_PATH.read_text(encoding="utf-8")

    data = Video._extract_html(html_content, url="https://www.empflix.com/amateur-porn/ryan-reid-seduces-hot-couple-kylie-rocket-and-mick-in-bnb-threesome/video3728878")

    assert data["video_id"] == "3728878"
    assert data["title"] == "Ryan Reid seduces hot couple Kylie Rocket and Mick in BnB threesome"
    assert "Ryan hosts Kylie and Mick" in data["description"]
    assert data["duration"] == 480
    assert data["length"] == "08:00"
    assert data["thumbnail_url"].startswith("https://cdnl.empflix.com/thumb/")
    assert data["mosaic_url_template"].startswith("https://cdnl.empflix.com/thumb/")
    assert data["publish_date"] == "2026-01-26T21:09:50+00:00"
    assert data["publish_date_relative"] == "8 months ago"
    assert data["embed_url"] == "https://player.empflix.com/video/3728878"
    assert data["author_name"] == "DoghousePassword"
    assert data["author_link"] == "https://www.empflix.com/profile/DoghousePassword"
    assert data["author_verified"] is False
    assert "Fetish Sex" in data["tags"]
    assert "Hardcore Porn" in data["tags"]
    assert data["likes"] == "168"
    assert data["dislikes"] == "57"
    assert data["rating_percent"] == "75%"
    assert data["rating_votes"] == "225"
    assert data["views"] == "30.5K"

    # Stream sources & qualities
    assert isinstance(data["direct_download_urls"], dict)
    assert 1080 in data["direct_download_urls"]
    assert 720 in data["direct_download_urls"]
    assert 480 in data["direct_download_urls"]
    assert 360 in data["direct_download_urls"]
    assert 240 in data["direct_download_urls"]
    assert 144 in data["direct_download_urls"]
    assert data["video_qualities"] == [144, 240, 360, 480, 720, 1080]


def test_extractor_video_list():
    html_content = SAMPLE_HTML_PATH.read_text(encoding="utf-8")
    videos = extractor_video_list(html_content, base_url="https://www.empflix.com")
    assert len(videos) > 0

    first = videos[0]
    assert first["video_id"] == "2970300"
    assert first["title"] == "Dirty blonde Kylie Rocket"
    assert first["url"] == "https://www.empflix.com/anal-porn/dirty-blonde-kylie-rocket/video2970300"
    assert first["length"] == "06:14"
    assert first["author_name"] == "Hwoarang96"
    assert first["views"] == "3.1K"
    assert first["rating"] == "64%"


@pytest.mark.asyncio
async def test_live_video():
    import os
    import tempfile
    from empflix_api import Client, DownloadConfigRAW

    client = Client()
    video = None
    try:
        async for res in client.search("blonde", pages=1):
            if res.item:
                if not video:
                    video = res.item
                parts = (res.item.length or "").split(":")
                if len(parts) == 2 and int(parts[0]) <= 2:
                    video = res.item
                    break
    except Exception as e:
        pytest.skip(f"Live network unavailable or connection reset by peer: {e}")

    if video is None:
        pytest.skip("No video returned from search (live site may be blocked or unavailable)")
    await video.load_sources("html")
    assert isinstance(video.title, str) and len(video.title) > 0
    assert video.video_qualities is not None and len(video.video_qualities) > 0
    assert video.direct_download_urls is not None and len(video.direct_download_urls) > 0

    with tempfile.TemporaryDirectory() as tmpdir:
        out_path = os.path.join(tmpdir, "test.mp4")
        config = DownloadConfigRAW(quality="worst", path=out_path, no_title=True)
        res = await video.download(config)
        assert res is True
        assert os.path.exists(out_path)
        assert os.path.getsize(out_path) > 1000

