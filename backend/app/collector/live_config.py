"""Idempotent server .env setup for three reviewed official HTML sources."""
from pathlib import Path
import secrets

VALUES = {
    "GOZ_IHALE_PORT": "8000",
    "GOZ_IHALE_ENABLED_SOURCE_KEYS": "khgm_central_notices,dmo,pau_hospital_purchase",
    "GOZ_IHALE_HTML_SOURCE_KEYS": "khgm_central_notices,dmo,pau_hospital_purchase",
    "GOZ_IHALE_HTML_PAGE_KHGM_CENTRAL_NOTICES": "https://khgm.saglik.gov.tr/TR-119527/ihale-duyurulari.html",
    "GOZ_IHALE_HTML_PAGE_DMO": "https://www.dmo.gov.tr/Ihale/Liste?type=1",
    "GOZ_IHALE_HTML_PAGE_PAU_HOSPITAL_PURCHASE": "https://www.pau.edu.tr/ihale/tr",
}

TOKEN_KEY = "GOZ_IHALE_API_WRITE_TOKEN"
PLACEHOLDER = "replace-with-a-strong-random-secret"

def configure_env_file(path: str | Path) -> bool:
    """Write reviewed source settings, preserving other entries and any real token.

    Returns True if a new write token was generated.
    """
    path = Path(path)
    lines = path.read_text(encoding="utf-8").splitlines() if path.exists() else []
    existing_token = None
    for line in lines:
        if line.startswith(TOKEN_KEY + "="):
            existing_token = line.split("=", 1)[1].strip()
    generated = not existing_token or existing_token == PLACEHOLDER
    token = secrets.token_hex(32) if generated else existing_token

    values = dict(VALUES)
    for line in lines:
        if line.startswith("GOZ_IHALE_PORT="):
            values["GOZ_IHALE_PORT"] = line.split("=", 1)[1].strip() or VALUES["GOZ_IHALE_PORT"]
            break
    values[TOKEN_KEY] = token
    output = []
    written = set()
    for line in lines:
        key = line.split("=", 1)[0] if "=" in line and not line.lstrip().startswith("#") else None
        if key in values:
            if key not in written:
                output.append(f"{key}={values[key]}")
                written.add(key)
        else:
            output.append(line)
    for key, value in values.items():
        if key not in written:
            output.append(f"{key}={value}")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(output).rstrip() + "\n", encoding="utf-8")
    try:
        path.chmod(0o600)
    except OSError:
        pass
    return generated

def main():
    path = Path(__file__).resolve().parents[2] / ".env"
    generated = configure_env_file(path)
    print(f"Configured {path} for KHGM central notices, DMO and Pamukkale University Hospital.")
    print("Write token generated." if generated else "Existing write token preserved.")

if __name__ == "__main__":
    main()
