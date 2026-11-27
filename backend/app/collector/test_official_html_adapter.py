"""Unit tests for the official HTML adapter parser and URL guard."""
import io
import unittest
from unittest.mock import patch
from .official_html_adapter import OfficialHTMLAdapter, _Links, _validate

class _FakeOpener:
    def __init__(self, data):
        self.data=data
    def open(self, request, timeout):
        return io.BytesIO(self.data)

class OfficialHTMLParserTests(unittest.TestCase):
    def test_extracts_anchor_text_and_href(self):
        parser=_Links()
        parser.feed('<a href="/notice/1">Optik OCT cihaz alımı</a><a href="/notice/2">YAG lazer</a>')
        self.assertEqual(parser.links,[('/notice/1','Optik OCT cihaz alımı'),('/notice/2','YAG lazer')])

    def test_ignores_empty_href(self):
        parser=_Links()
        parser.feed('<a>no link</a><a href="">empty</a>')
        self.assertEqual(parser.links,[])

    def test_parser_handles_malformed_html_and_nested_text(self):
        parser=_Links()
        parser.feed('<a href="/notice/1"><b>OCT</b> cihaz alımı')
        parser.close()
        self.assertEqual(len(parser.links),1)
        self.assertEqual(parser.links[0][0],'/notice/1')
        self.assertIn('OCT',parser.links[0][1])

    def test_listing_row_context_is_preserved_for_generic_detail_link(self):
        parser=_Links()
        parser.feed('<table><tr><td>18175</td><td>OCT Retina cihazı satın alımı</td><td>24.11.2026</td><td><a href="/Ihale/Detay/18175">Detay</a></td></tr></table>')
        parser.close()
        self.assertEqual(parser.links[0],('/Ihale/Detay/18175','Detay'))
        self.assertIn('OCT Retina',parser.contexts[0])
        self.assertIn('24.11.2026',parser.contexts[0])

    def test_url_guard_rejects_non_https_and_host_mismatch(self):
        with self.assertRaises(ValueError): _validate("http://example.gov.tr/list","example.gov.tr")
        with self.assertRaises(ValueError): _validate("https://other.gov.tr/list","example.gov.tr")

    def test_url_guard_rejects_credentials_and_fragment(self):
        with self.assertRaises(ValueError): _validate("https://user:pass@example.gov.tr/list","example.gov.tr")
        with self.assertRaises(ValueError): _validate("https://example.gov.tr/list#x","example.gov.tr")

    @patch("socket.getaddrinfo", return_value=[(2,1,6,"",("127.0.0.1",443))])
    def test_url_guard_rejects_non_public_ip(self, mocked_dns):
        with self.assertRaises(ValueError): _validate("https://example.gov.tr/list","example.gov.tr")

    def test_link_limit(self):
        parser=_Links()
        for i in range(350):
            parser.feed(f'<a href="/{i}">link {i}</a>')
        self.assertLessEqual(len(parser.links),300)

    def test_parser_caps_link_count_when_many_links(self):
        parser=_Links()
        for i in range(500):
            parser.feed(f'<a href="/notice/{i}">Notice {i}</a>')
        self.assertEqual(len(parser.links),300)

    def test_relative_and_absolute_link_parsing(self):
        parser=_Links()
        parser.feed('<a href="/relative">Relative</a><a href="https://example.gov.tr/absolute">Absolute</a>')
        self.assertEqual(parser.links[0][0],'/relative')
        self.assertEqual(parser.links[1][0],'https://example.gov.tr/absolute')

    def test_collect_uses_row_context_for_dmo_style_detail_link(self):
        html=('<table><tr><td>18175</td><td>OCT Retina cihazı satın alımı</td>'
              '<td>24.11.2026</td><td><a href="/Ihale/Detay/18175">Detay</a></td></tr></table>').encode()
        with patch("app.collector.official_html_adapter._validate", side_effect=lambda url, host: url), \
             patch("app.collector.official_html_adapter.build_opener", return_value=_FakeOpener(html)):
            adapter=OfficialHTMLAdapter("DMO","https://example.gov.tr/list","example.gov.tr")
            candidates=adapter.collect()
        self.assertEqual(len(candidates),1)
        self.assertIn("OCT Retina",candidates[0].title)
        self.assertIn("24.11.2026",candidates[0].description)
        self.assertEqual(candidates[0].source_url,"https://example.gov.tr/Ihale/Detay/18175")

    def test_collect_deduplicates_repeated_notice_links(self):
        html=(
            '<a href="/notice/1">OCT retina cihazı alımı</a>'
            '<a href="/notice/1">OCT retina cihazı alımı tekrar</a>'
            '<a href="/notice/2">YAG lazer cihazı satın alımı</a>'
        ).encode()
        with patch("app.collector.official_html_adapter._validate", side_effect=lambda url, host: url), \
             patch("app.collector.official_html_adapter.build_opener", return_value=_FakeOpener(html)):
            adapter=OfficialHTMLAdapter("Test Hastanesi","https://example.gov.tr/list","example.gov.tr")
            candidates=adapter.collect()
        self.assertEqual(len(candidates),2)
        self.assertEqual([c.source_url for c in candidates],[
            "https://example.gov.tr/notice/1","https://example.gov.tr/notice/2"
        ])

if __name__=="__main__":
    unittest.main()
