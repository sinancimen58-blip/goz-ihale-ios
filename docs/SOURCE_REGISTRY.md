# Gözİhale — Source Registry

The monitoring scope is intentionally broader than EKAP. Gözİhale should index ophthalmology-relevant procurement opportunities across official platforms, institutional sources, and commercial aggregators (aggregators are discovery aids; verify each notice at its original publisher).

## Source groups

### National official sources
- EKAP: public tenders, direct procurement notices where published, results, corrections, cancellations and decisions.
- DMO (State Supply Office): catalogue/central purchasing and tender notices.
- ilan.gov.tr / Basın İlan Kurumu: public notices that may contain procurement and institutional announcements.
- Kamu İhale Kurumu (KİK): bulletins, statistics, decisions and complaint/appeal information.
- Resmî Gazete: legal notices, regulations and institution announcements relevant to procurement.

### Institution-specific sources (continuous discovery)
- University hospitals and university procurement / revolving-fund / BAP pages.
- Ministry of Health, provincial health directorates, public hospitals and city hospitals.
- Municipalities and metropolitan municipalities, including municipal companies and health facilities.
- Public agencies, institutes and state-owned enterprises that procure ophthalmic devices.
- Public procurement portals and e-procurement platforms used by individual institutions.

### Other official e-procurement portals (scope review)
- DHMI procurement / e-procurement portal.
- Ministry of Trade GTB e-İhale (monitor only categories relevant to the project).
- MKE e-İhale and other public-company portals (monitor only relevant procurement categories).
- Vakıflar Genel Müdürlüğü and other agency procurement portals.
- International funding/aid procurement portals where Turkey-based medical equipment opportunities are published (EU/TED, UNDP, EBRD, World Bank).

### Discovery aggregators (not authoritative)
- Commercial tender trackers and search services such as İhale365, İhaleTara, İhaleArama and eİhaleBul may help discover notices and mirror records. Never treat these as the authoritative record; open and verify the original notice and document.

## Monitoring logic
1. Search across sources for ophthalmology terms and category aliases.
2. Normalize each candidate to a common record.
3. Store publisher, original URL, source type, publication/update dates, notice ID and retrieval metadata.
4. Deduplicate by normalized notice ID where available; otherwise use a normalized title + institution + date fingerprint.
5. Track changes to deadline, technical specifications, quantity, estimated price (when public), status, correction/cancellation and award information.
6. Classify and score relevance; mark high-priority opportunities.
7. Notify only on new or material changes, while preserving source provenance.

## Ophthalmology keyword scope
OCT/OCT-A, retina imaging, optical biometry, A-scan, topography/tomography, phaco, cataract surgery consumables, IOL, YAG/SLT lasers, fundus camera, ophthalmic microscope, slit lamp, tonometer, visual field/perimeter, refractometer/keratometer, lensmeter, microperimetry, aberrometry, diagnostic ophthalmic devices, probes, accessories, spare parts, maintenance and calibration.

## Access and compliance
Use official APIs, feeds, public pages and permitted access methods. Respect terms, rate limits and robots/access controls. Do not bypass authentication, CAPTCHA, paywalls or access restrictions. Aggregator results must be verified against the publisher.
