from pathlib import Path
from app.collector import live_config

def test_configure_env_file_adds_three_reviewed_sources_and_preserves_token(tmp_path):
    env=tmp_path/".env"
    env.write_text("CUSTOM=value\nGOZ_IHALE_API_WRITE_TOKEN=existing-token\nGOZ_IHALE_PORT=9000\n",encoding="utf-8")
    generated=live_config.configure_env_file(env)
    lines=env.read_text(encoding="utf-8").splitlines()
    values=dict(line.split("=",1) for line in lines if "=" in line and not line.startswith("#"))
    assert generated is False
    assert values["CUSTOM"]=="value"
    assert values["GOZ_IHALE_API_WRITE_TOKEN"]=="existing-token"
    assert values["GOZ_IHALE_PORT"]=="9000"
    assert values["GOZ_IHALE_ENABLED_SOURCE_KEYS"]=="khgm_central_notices,dmo,pau_hospital_purchase"
    assert values["GOZ_IHALE_HTML_SOURCE_KEYS"]==values["GOZ_IHALE_ENABLED_SOURCE_KEYS"]
    assert values["GOZ_IHALE_HTML_PAGE_PAU_HOSPITAL_PURCHASE"]=="https://www.pau.edu.tr/ihale/tr"

def test_configure_env_file_generates_token_when_missing(tmp_path):
    env=tmp_path/".env"
    generated=live_config.configure_env_file(env)
    values=dict(line.split("=",1) for line in env.read_text(encoding="utf-8").splitlines() if "=" in line)
    assert generated is True
    assert len(values["GOZ_IHALE_API_WRITE_TOKEN"])==64
