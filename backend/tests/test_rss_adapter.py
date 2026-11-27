from app.collector.rss_adapter import parse_feed, _validate_feed_url

RSS="""<rss version="2.0"><channel><item><title>OCT cihazı</title><link>https://example.org/notice/1</link><description>Hastane alımı</description></item></channel></rss>""".encode("utf-8")
ATOM="""<feed xmlns="http://www.w3.org/2005/Atom"><entry><title>Tonometre alımı</title><link href="https://example.org/notice/2"/><summary>Medikal</summary></entry></feed>""".encode("utf-8")

def test_rss_parse():
    notices=parse_feed(RSS,"Test Feed","https://example.org/rss")
    assert len(notices)==1
    assert notices[0].title=="OCT cihazı"
    assert notices[0].source_url=="https://example.org/notice/1"

def test_atom_parse():
    notices=parse_feed(ATOM,"Atom Feed","https://example.org/atom")
    assert len(notices)==1
    assert notices[0].title=="Tonometre alımı"
    assert notices[0].source_url=="https://example.org/notice/2"

def test_invalid_missing_title_skipped():
    notices=parse_feed(b"<rss><channel><item><link>https://example.org</link></item></channel></rss>","x","https://example.org")
    assert notices==[]

def test_feed_url_requires_https():
    try:
        _validate_feed_url("http://example.org/rss")
    except ValueError:
        pass
    else:
        assert False, "HTTP URL should be rejected"


import pytest
from app.collector.rss_adapter import MAX_FEED_BYTES, MAX_ITEMS


def test_atom_prefers_alternate_link():
    xml = b'<feed xmlns="http://www.w3.org/2005/Atom"><entry><title>Notice</title><link rel="self" href="https://example.org/self"/><link rel="alternate" href="https://example.org/notice"/></entry></feed>'
    notices = parse_feed(xml, "Source", "https://example.org/feed")
    assert notices[0].source_url == "https://example.org/notice"


def test_description_is_bounded():
    xml = ('<rss><channel><item><title>Notice</title><description>' + ('x' * 13000) + '</description></item></channel></rss>').encode()
    notices = parse_feed(xml, "Source", "https://example.org/feed")
    assert len(notices[0].description) == 12000


def test_feed_size_limit_rejected():
    with pytest.raises(ValueError):
        parse_feed(b'x' * (MAX_FEED_BYTES + 1), "Source", "https://example.org/feed")


def test_malformed_xml_rejected():
    with pytest.raises(Exception):
        parse_feed(b'<rss><item>', "Source", "https://example.org/feed")


def test_item_count_is_bounded():
    items = ''.join('<item><title>Notice %s</title></item>' % i for i in range(MAX_ITEMS + 10))
    xml = ('<rss><channel>' + items + '</channel></rss>').encode()
    notices = parse_feed(xml, "Source", "https://example.org/feed")
    assert len(notices) == MAX_ITEMS
