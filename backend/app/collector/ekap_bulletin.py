"""EKAP bulletin archive link discovery; only links from the official EKAP host are accepted."""
from html.parser import HTMLParser
from urllib.parse import urljoin, urlparse
import re

MAX_LINKS = 100

class _ArchiveParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links=[]
        self.text=[]
    def handle_starttag(self,tag,attrs):
        attrs=dict(attrs)
        if tag.lower()=="a":
            href=attrs.get("href","").strip()
            if href and len(self.links)<MAX_LINKS:
                self.links.append(href)
    def handle_data(self,data):
        if data and data.strip():
            self.text.append(data.strip())

def extract_bulletin_links(html: str, base_url: str="https://ekap.kik.gov.tr/ekap/ilan/bultenindirme.aspx"):
    parser=_ArchiveParser()
    parser.feed(html[:2_000_000])
    host=urlparse(base_url).hostname or ""
    out=[]
    for href in parser.links:
        url=urljoin(base_url,href)
        p=urlparse(url)
        if p.scheme!="https" or not p.hostname:
            continue
        if p.hostname.casefold()!=host.casefold() and not p.hostname.casefold().endswith("."+host.casefold()):
            continue
        if p.path.lower().endswith(".pdf") or "pdf" in p.path.lower() or "pdf" in p.query.lower():
            out.append(url)
    date_text=" ".join(parser.text)
    date_match=re.search(r"(\\d{1,2}\\.\\d{1,2}\\.\\d{4})",date_text)
    return {"pdf_urls":list(dict.fromkeys(out)),"bulletin_date":date_match.group(1) if date_match else None,"link_count":len(parser.links)}
