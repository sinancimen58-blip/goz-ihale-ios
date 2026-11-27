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
MAX_CONTEXT_CHARS=2000
GENERIC_LINK_LABELS={"detay","incele","görüntüle","indir","download","click here","devamı"}

class _Links(HTMLParser):
    """Extract links and their enclosing listing-row/card context."""
    def __init__(self):
        super().__init__()
        self.links=[]
        self.contexts=[]
        self._href=None
        self._text=[]
        self._anchor_frame=None
        self._frames=[]

    def _count_links(self):
        return len(self.links)+sum(len(frame["links"]) for frame in self._frames)

    def _add(self,href,title,context=""):
        if href and self._count_links()<MAX_LINKS:
            self.links.append((href,title))
            self.contexts.append(context[:MAX_CONTEXT_CHARS])

    def handle_starttag(self,tag,attrs):
        attrs=dict(attrs)
        classes=set((attrs.get("class") or "").casefold().split())
        if tag.lower() in {"tr","li","article"} or (tag.lower()=="div" and classes.intersection({"notice","announcement","tender","news","item","card"})):
            self._frames.append({"tag":tag.lower(),"text":[],"links":[]})
        if tag.lower()=="a":
            href=attrs.get("href")
            if href and self._count_links()<MAX_LINKS:
                self._href=href
                self._text=[]
                self._anchor_frame=self._frames[-1] if self._frames else None

    def handle_data(self,data):
        if self._href is not None:
            self._text.append(data)
        for frame in self._frames:
            frame["text"].append(data)

    def _finish_anchor(self):
        if self._href is not None:
            href=self._href
            title=" ".join(self._text).strip()
            frame=self._anchor_frame
            if frame is not None:
                frame["links"].append((href,title))
            else:
                self._add(href,title,"")
        self._href=None
        self._text=[]
        self._anchor_frame=None

    def _flush_frame(self,frame):
        context=" ".join(frame["text"]).strip()
        links=frame["links"]
        frame["links"]=[]
        for href,title in links:
            self._add(href,title,context)

    def handle_endtag(self,tag):
        if tag.lower()=="a":
            self._finish_anchor()
        # Close the nearest matching context; also close malformed nested frames.
        for index in range(len(self._frames)-1,-1,-1):
            if self._frames[index]["tag"]==tag.lower():
                for frame in reversed(self._frames[index:]):
                    self._flush_frame(frame)
                del self._frames[index:]
                break

    def close(self):
        super().close()
        self._finish_anchor()
        for frame in reversed(self._frames):
            self._flush_frame(frame)
        self._frames.clear()

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
        parser=_Links(); parser.feed(data.decode("utf-8","replace")); parser.close()
        out=[]
        seen_urls={}
        for index,(href,anchor_title) in enumerate(parser.links):
            context=parser.contexts[index] if index<len(parser.contexts) else ""
            anchor_title=anchor_title.strip()
            generic=anchor_title.casefold() in GENERIC_LINK_LABELS or len(anchor_title)<12
            title=context.strip() if generic and len(context.strip())>=12 else anchor_title
            if len(title)<12: continue
            link=urljoin(self.source_url,href)
            try: _validate(link,self.source_domain)
            except ValueError: continue
            description=context.strip()[:MAX_CONTEXT_CHARS] or None
            # Avoid repeated candidates; prefer the richer listing context on duplicate URLs.
            if link in seen_urls:
                old=out[seen_urls[link]]
                if description and len(description)>len(old.description or ""):
                    old.description=description
                if generic and description and len(description)>len(old.title):
                    old.title=description[:600]
                continue
            seen_urls[link]=len(out)
            out.append(NoticeCandidate(title=title[:600],institution=self.source_name,source_name=self.source_name,source_url=link,description=description))
        return out
