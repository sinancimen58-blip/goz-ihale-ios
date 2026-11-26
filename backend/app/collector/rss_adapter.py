"""Simple RSS/Atom feed adapter for explicitly configured public feeds."""
from urllib.request import Request, urlopen
from urllib.parse import urlparse
from xml.etree import ElementTree as ET
from datetime import date
from .adapter import SourceAdapter
from .models import NoticeCandidate

def _validate_feed_url(url: str):
    parsed = urlparse(url)
    if parsed.scheme != "https" or not parsed.hostname or parsed.username or parsed.password:
        raise ValueError("Feed URL must be a public HTTPS URL.")
    host = parsed.hostname.casefold()
    if host in {"localhost"} or host.endswith(".localhost"):
        raise ValueError("Local feed hosts are not allowed.")
    return url

def parse_feed(xml_bytes: bytes, source_name: str, source_url: str):
    root=ET.fromstring(xml_bytes)
    candidates=[]
    def text_for(node, names):
        for name in names:
            found=node.find(name)
            if found is not None and found.text:
                return found.text.strip()
        return ""
    nodes=root.findall(".//item")
    if not nodes:
        nodes=root.findall(".//{*}entry")
    for node in nodes:
        title=text_for(node, ["title","{*}title"])
        link=text_for(node, ["link","{*}link"])
        if not link:
            link_node=node.find("{*}link")
            if link_node is not None:
                link=link_node.attrib.get("href","")
        description=text_for(node, ["description","summary","content","{*}summary","{*}content"])
        if not title:
            continue
        candidates.append(NoticeCandidate(
            title=title,
            institution=source_name,
            source_name=source_name,
            source_url=link or source_url,
            description=description or None
        ))
    return candidates

class RSSFeedAdapter(SourceAdapter):
    def __init__(self, source_name: str, feed_url: str):
        self.source_name=source_name
        self.feed_url=_validate_feed_url(feed_url)
    def collect(self):
        request=Request(self.feed_url,headers={"User-Agent":"GozIhale/0.1 (public feed reader)"})
        with urlopen(request,timeout=10) as response:
            data=response.read(2_000_000)
        return parse_feed(data,self.source_name,self.feed_url)
