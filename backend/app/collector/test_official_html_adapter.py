"""Unit tests for the official HTML adapter parser and URL guard."""
import unittest
from unittest.mock import patch
from .official_html_adapter import _Links, _validate

class OfficialHTMLParserTests(unittest.TestCase):
    def test_extracts_anchor_text_and_href(self):
        parser=_Links()
        parser.feed('<a href="/notice/1">Optik OCT cihaz alımı</a><a href="/notice/2">YAG lazer</a>')
        self.assertEqual(parser.links,[('/notice/1','Optik OCT cihaz alımı'),('/notice/2','YAG lazer')])

    def test_ignores_empty_href(self):
        parser=_Links()
        parser.feed('<a>no link</a><a href="">empty</a>')
        self.assertEqual(parser.links,[])

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

if __name__=="__main__":
    unittest.main()


    def test_parser_handles_malformed_html_and_nested_text(self):
        parser=_Links()
        parser.feed('<a href="/notice/1"><b>OCT</b> cihaz alımı')
        self.assertEqual(len(parser.links),1)
        self.assertEqual(parser.links[0][0],'/notice/1')
        self.assertIn('OCT',parser.links[0][1])

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
