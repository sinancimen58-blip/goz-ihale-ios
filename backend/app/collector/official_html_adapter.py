"""Conservative adapter for publicly accessible official notice-listing pages.

Only explicit source keys and page URLs configured by the operator are used.
This adapter does not bypass authentication, JavaScript challenges or access controls.
"""
from html.parser import HTMLParser
from urllib.request import Request, build_opener, HTTPRedirectHandler
from urllib.parse import urlparse, urljoin
import socket, ipaddress
from .adapter import SourceAdapter
from .models import NoticeCandidate

MAX_BYTES=2_000_000
MAX_LINKS=300

class _Links(HTMLParser):
    def __init__(self):
        super().__init__(); self.links=[]; self._href=None; self._text=[]
    def handle_starttag(self,tag,attrs):
        if tag.lower()=="a":
            attrs=dict(attrs); href=attrs.get("href")
            if href and len(self.links)<MAX_LINKS:
                self._href=href; self._text=[]
    def handle_data(self,data):
        if self._href is not None: self._text.append(data)
    def handle_endtag(self,tag):
        if tag.lower()=="a" and self._href is not None:
            self.links.append((self._href," ".join(self._text).strip()))
            self._href=None; self._text=[]

class _NoRedirect(HTTPRedirectHandler):
    def redirect_request(self,req,fp,code,msg,headers,newurl):
        raise ValueError("Redirect blocked; configure the official final URL.")

def _validate(url,allowed_host):
    p=urlparse(url)
    if p.scheme!="https" or not p.hostname or p.username or p.password or p.fragment:
        raise ValueError("HTTPS page URL required.")
    host=p.hostname.casefold()
    base=allowed_host.casefold()
    if host!=base and not host.endswith("."+base):
        raise ValueError("Configured page host must match registered source domain.")
    for item in socket.getaddrinfo(host,p.port or 443,type=socket.SOCK_STREAM):
        if not ipaddress.ip_address(item[4][0]).is_global:
            raise ValueError("Non-public host address blocked.")
    return url

class OfficialHTMLAdapter(SourceAdapter):
    def __init__(self,source_name,source_url,source_domain):
        self.source_name=source_name
        self.source_url=_validate(source_url,source_domain)
        self.source_domain=source_domain
    def collect(self):
        _validate(self.source_url,self.source_domain)
        req=Request(self.source_url,headers={"User-Agent":"GozIhale/0.1 (public notice listing reader)"})
        with build_opener(_NoRedirect()).open(req,timeout=15) as response:
            data=response.read(MAX_BYTES+1)
        if len(data)>MAX_BYTES: raise ValueError("Page exceeds size limit.")
        parser=_Links(); parser.feed(data.decode("utf-8","replace"))
        out=[]
        for href,title in parser.links:
            title=title.strip()
            if len(title)<12 or not title: continue
            link=urljoin(self.source_url,href)
            try: _validate(link,self.source_domain)
            except ValueError: continue
            out.append(NoticeCandidate(title=title,institution=self.source_name,source_name=self.source_name,source_url=link,description=None))
        return out
