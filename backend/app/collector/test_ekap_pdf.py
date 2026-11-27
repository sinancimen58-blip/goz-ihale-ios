import pytest
from app.collector.ekap_pdf import validate_pdf_url, extract_pdf_text, MAX_PDF_BYTES

def test_url_allowlist():
    with pytest.raises(ValueError): validate_pdf_url("http://ekap.kik.gov.tr/a.pdf")
    with pytest.raises(ValueError): validate_pdf_url("https://evil.example/a.pdf")
    with pytest.raises(ValueError): validate_pdf_url("https://ekap.kik.gov.tr:8443/a.pdf")

def test_pdf_signature_and_size():
    with pytest.raises(ValueError): extract_pdf_text(b"not pdf")
    with pytest.raises(ValueError): extract_pdf_text(b"%PDF-"+b"x"*(MAX_PDF_BYTES+1))
