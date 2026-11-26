"""RSS/Atom adapter with conservative URL validation for public feeds."""
from urllib.request import Request, urlopen
from urllib.parse import urlparse
from xml.etree import ElementTree as ET
import socket, ipaddress
from .adapter import SourceAdapter
from .models import NoticeCandidate

def _validate_feed_url(url: str):
    parsed=urlparse(url)
    if parsed.scheme != "https" or not parsed.hostname or parsed.username or parsed.password:
        raise ValueError("Feed URL must be public HTTPS without credentials.")
    host=parsed.hostname.casefold()
    if host=="localhost" or host.endswith(".localhost"):
        raise ValueError("Local feed hosts are not allowed.")
    try:
        addresses=socket.getaddrinfo(host,parsed.port or 443,type=socket.SOCK_STREAM)
    except OSError as exc:
        raise ValueError("Feed host could not be resolved.") from exc
    for item in addresses:
        ip=ipaddress.ip_address(item[4][0])
        if not ip.is_global:
            raise ValueError("Feed host resolves to a non-public address.")
    return url

def parse_feed(xml_bytes: bytes, source_name: str, source_url: str):
    root=ET.fromstring(xml_bytes)
    candidates=[]
    def text_for(node,names):
        for name in names:
            found=node.find(name)
            if found is not None and found.text:
                return found.text.strip()
        return ""
    nodes=root.findall(".//item") or root.findall(".//{*}entry")
    for node in nodes:
        title=text_for(node,["title","{*}title"])
        link=text_for(node,["link","{*}link"])
        if not link:
            link_node=node.find("{*}link")
            if link_node is not None: link=link_node.attrib.get("href","")
        description=text_for(node,["description","summary","content","{*}summary","{*}content"])
        if title:
            candidates.append(NoticeCandidate(title=title,institution=source_name,source_name=source_name,source_url=link or source_url,description=description or None))
    return candidates

class RSSFeedAdapter(SourceAdapter):
    def __init__(self,source_name:str,feed_url:str):
        self.source_name=source_name
        self.feed_url=_validate_feed_url(feed_url)
    def collect(self):
        # Validate again immediately before connecting; redirects are disabled by default urllib behavior only for protocol changes,
        # so the destination is checked before the initial request.
        _validate_feed_url(self.feed_url)
        request=Request(self.feed_url,headers={"User-Agent":"GozIhale/0.1 (public feed reader)"})
        with urlopen(request,timeout=10) as response:
            data=response.read(2_000_000)
        return parse_feed(data,self.source_name,self.feed_url)
