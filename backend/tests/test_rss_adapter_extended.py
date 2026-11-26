from app.collector.rss_adapter import parse_feed

ATOM_LINKS = b"""<feed xmlns="http://www.w3.org/2005/Atom"><entry><title>Optik biyometri alımı</title><link rel="alternate" href="https://example.org/item/3"/><summary>İhale</summary></entry></feed>"""

def test_atom_alternate_link():
    items = parse_feed(ATOM_LINKS, "Feed", "https://example.org/feed")
    assert len(items) == 1
    assert items[0].source_url == "https://example.org/item/3"

def test_description_is_bounded():
    payload = ("<rss><channel><item><title>Test</title><description>" + ("x" * 15000) + "</description></item></channel></rss>").encode()
    items = parse_feed(payload, "Feed", "https://example.org/feed")
    assert len(items) == 1
    assert len(items[0].description) <= 12000
