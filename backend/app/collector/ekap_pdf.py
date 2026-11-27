"""Bounded, allowlisted EKAP PDF fetch and text extraction utilities."""
from __future__ import annotations
from urllib.parse import urlparse
from urllib.request import Request, urlopen
import socket, ipaddress

EKAP_HOST = "ekap.kik.gov.tr"
MAX_PDF_BYTES = 8 * 1024 * 1024
TIMEOUT_SECONDS = 12

def validate_pdf_url(url: str) -> str:
    p=urlparse(url)
    host=(p.hostname or "").casefold()
    if p.scheme != "https" or not host or (host != EKAP_HOST and not host.endswith("." + EKAP_HOST)):
        raise ValueError("PDF URL must use HTTPS and an EKAP host")
    if p.username or p.password or p.port not in (None,443):
        raise ValueError("Unsupported URL authority")
    try:
        addresses=socket.getaddrinfo(host,443,type=socket.SOCK_STREAM)
    except OSError as exc:
        raise ValueError("Host resolution failed") from exc
    if not addresses:
        raise ValueError("No address resolved")
    for item in addresses:
        ip=ipaddress.ip_address(item[4][0])
        if not ip.is_global:
            raise ValueError("Non-public address rejected")
    return url

class _NoRedirect:
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None

def download_pdf(url: str) -> bytes:
    validate_pdf_url(url)
    req=Request(url,headers={"User-Agent":"GozIhaleResearch/1.0","Accept":"application/pdf"})
    opener=__import__("urllib.request",fromlist=["build_opener"]).build_opener(_NoRedirect())
    with opener.open(req,timeout=TIMEOUT_SECONDS) as response:
        if response.status != 200:
            raise ValueError("Unexpected HTTP status")
        if response.headers.get_content_type() != "application/pdf":
            raise ValueError("Response is not a PDF")
        length=response.headers.get("Content-Length")
        if length and int(length)>MAX_PDF_BYTES:
            raise ValueError("PDF exceeds size limit")
        data=response.read(MAX_PDF_BYTES+1)
    if len(data)>MAX_PDF_BYTES:
        raise ValueError("PDF exceeds size limit")
    if not data.startswith(b"%PDF-"):
        raise ValueError("Invalid PDF signature")
    return data

def extract_pdf_text(pdf_bytes: bytes) -> str:
    if len(pdf_bytes)>MAX_PDF_BYTES or not pdf_bytes.startswith(b"%PDF-"):
        raise ValueError("Invalid or oversized PDF")
    try:
        from pypdf import PdfReader
        import io
        reader=PdfReader(io.BytesIO(pdf_bytes),strict=False)
        if len(reader.pages)>250:
            raise ValueError("PDF page limit exceeded")
        return "\n".join((page.extract_text() or "") for page in reader.pages)
    except ImportError as exc:
        raise RuntimeError("Install pypdf to enable bulletin extraction") from exc
