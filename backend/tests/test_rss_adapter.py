from app.collector.rss_adapter import parse_feed, _validate_feed_url

RSS="""<rss version="2.0"><channel><item><title>OCT cihazı</title><link>https://example.org/notice/1</link><description>Hastane alımı</description></item></channel></rss>""".encode("utf-8")
ATOM=b"""<feed xmlns="http://www.w3.org/2005/Atom"><entry><title>Tonometre alımı</title><link href="https://example.org/notice/2"/><summary>Medikal</summary></entry></feed>"""

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
