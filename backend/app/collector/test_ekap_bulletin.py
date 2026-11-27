import unittest
from .ekap_bulletin import extract_bulletin_links

class EKAPBulletinParserTests(unittest.TestCase):
    def test_extracts_official_pdf_and_date(self):
        html='<h4>25.11.2026 Tarihinde yayımlanan</h4><a href="/files/bulten.pdf">PDF</a><a href="https://other.example/file.pdf">foreign</a>'
        result=extract_bulletin_links(html)
        self.assertEqual(result["bulletin_date"],"25.11.2026")
        self.assertEqual(result["pdf_urls"],["https://ekap.kik.gov.tr/files/bulten.pdf"])
    def test_rejects_non_https_and_foreign_links(self):
        html='<a href="http://ekap.kik.gov.tr/a.pdf">x</a><a href="https://evil-ekap.kik.gov.tr/a.pdf">y</a>'
        self.assertEqual(extract_bulletin_links(html)["pdf_urls"],[])
    def test_deduplicates(self):
        html='<a href="/b.pdf">one</a><a href="/b.pdf">two</a>'
        self.assertEqual(len(extract_bulletin_links(html)["pdf_urls"]),1)

if __name__=="__main__":
    unittest.main()
