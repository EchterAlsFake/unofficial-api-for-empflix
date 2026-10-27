import os
import tempfile
import pytest
from empflix_api import Client, Video, Profile, Pornstar, Channel, Sort, SortDate, DownloadConfigRAW
from base_api.modules.errors import MediaLoadError, NotFound, DownloadFailed


def test_url_normalizations():
    # Video
    assert Client._normalize_video_url("1034648") == "https://www.empflix.com/video/1034648"
    assert Client._normalize_video_url("video1034648") == "https://www.empflix.com/video/1034648"
    assert Client._normalize_video_url("video/1034648") == "https://www.empflix.com/video/1034648"
    assert Client._normalize_video_url("videos/1034648") == "https://www.empflix.com/video/1034648"
    assert Client._normalize_video_url("https://player.empflix.com/video/1034648") == "https://www.empflix.com/video/1034648"
    assert Client._normalize_video_url("https://www.empflix.com/amateur-porn/foo/video1034648") == "https://www.empflix.com/amateur-porn/foo/video1034648"
    assert Client._normalize_video_url("amateur-porn/foo/video1034648") == "https://www.empflix.com/amateur-porn/foo/video1034648"

    # Profile
    assert Client._normalize_profile_url("dani-daniels") == "https://www.empflix.com/profile/dani-daniels"
    assert Client._normalize_profile_url("profile/dani-daniels") == "https://www.empflix.com/profile/dani-daniels"
    assert Client._normalize_profile_url("profiles/dani-daniels") == "https://www.empflix.com/profile/dani-daniels"
    assert Client._normalize_profile_url("pornstar/dani-daniels") == "https://www.empflix.com/profile/dani-daniels"
    assert Client._normalize_profile_url("pornstars/dani-daniels") == "https://www.empflix.com/profile/dani-daniels"
    assert Client._normalize_profile_url("https://www.empflix.com/pornstar/dani-daniels") == "https://www.empflix.com/profile/dani-daniels"
    assert Client._normalize_profile_url("https://www.empflix.com/profiles/dani-daniels") == "https://www.empflix.com/profile/dani-daniels"

    # Channel
    assert Client._normalize_channel_url("team-skeet") == "https://www.empflix.com/channel/team-skeet"
    assert Client._normalize_channel_url("channel/team-skeet") == "https://www.empflix.com/channel/team-skeet"
    assert Client._normalize_channel_url("channels/team-skeet") == "https://www.empflix.com/channel/team-skeet"


@pytest.mark.asyncio
async def test_canonical_resolution_and_metadata():
    client = Client()
    # Loading via bare ID should auto-resolve canonical full URL and populate all metadata
    video = await client.get_video("3728878")
    assert video.title is not None
    assert video.author_name == "DoghousePassword"
    assert video.author_link == "https://www.empflix.com/profile/DoghousePassword"
    assert video.views is not None
    assert video.video_qualities is not None and len(video.video_qualities) > 0

    # Test edge case: video without author badge (anonymous/deleted uploader)
    anon_video = await client.get_video("1034648")
    assert anon_video.title is not None
    assert anon_video.author_name is None
    assert anon_video.author_link is None

    # Related videos should work when loaded via short ID
    related = await video.get_related_videos()
    assert isinstance(related, list)
    assert len(related) > 0
    assert "video_id" in related[0]
    assert "url" in related[0]


@pytest.mark.asyncio
async def test_profile_uploader_and_get_author():
    client = Client()
    video = await client.get_video("https://www.empflix.com/amateur-porn/ryan-reid-seduces-hot-couple-kylie-rocket-and-mick-in-bnb-threesome/video3728878")
    assert video.author_name == "DoghousePassword"
    assert video.author_link == "https://www.empflix.com/profile/DoghousePassword"

    author = await video.get_author(load_html=True)
    assert isinstance(author, Profile)
    assert author.name == "DoghousePassword"
    assert author.entity_id == "4288566346"


@pytest.mark.asyncio
async def test_get_pornstar_client_method():
    client = Client()
    star = await client.get_pornstar("dani-daniels", load_html=True)
    assert isinstance(star, Pornstar)
    assert isinstance(star, Profile)
    assert star.name == "Dani Daniels"
    assert star.entity_id == "3236785"

    star2 = await client.get_pornstar("https://www.empflix.com/pornstar/dani-daniels", load_html=False)
    assert isinstance(star2, Pornstar)
    assert star2.url == "https://www.empflix.com/profile/dani-daniels"


@pytest.mark.asyncio
async def test_search_and_filters():
    client = Client()
    results = []
    async for r in client.search("blonde", sorting_sort=Sort.Sort_most_viewed, sorting_date=SortDate.Sort_all, pages=1):
        if r.item:
            results.append(r.item)
    assert len(results) > 0

    empty_results = []
    async for r in client.search("98765432109876543210zyxwvutsrqponmlkjihgfedcba", pages=1):
        if r.item:
            empty_results.append(r.item)
    assert len(empty_results) == 0


@pytest.mark.asyncio
async def test_404_error_handling():
    client = Client()
    with pytest.raises(MediaLoadError):
        await client.get_video("99999999999999")

    with pytest.raises(MediaLoadError):
        await client.get_profile("non_existent_user_9999999999")


@pytest.mark.asyncio
async def test_download_short_video_and_cli():
    client = Client()
    video = await client.get_video("https://www.empflix.com/amateur-porn/blonde/video1034648")
    with tempfile.TemporaryDirectory() as tmpdir:
        out_path = os.path.join(tmpdir, "edge_test.mp4")
        cfg = DownloadConfigRAW(quality="worst", path=out_path, no_title=True)
        res = await video.download(cfg)
        assert res is True
        assert os.path.exists(out_path)
        assert os.path.getsize(out_path) > 100_000

    from empflix_api.api import run_main
    with tempfile.TemporaryDirectory() as tmpdir:
        out_file = os.path.join(tmpdir, "cli_test.mp4")
        await run_main(["--download", "https://www.empflix.com/amateur-porn/blonde/video1034648", "--quality", "worst", "--output", out_file, "--no-title"])
        assert os.path.exists(out_file)
        assert os.path.getsize(out_file) > 100_000
