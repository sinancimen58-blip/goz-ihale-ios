"""Tests for safe, idempotent live-source server configuration."""
from app.collector.live_config import configure_env_file, VALUES, TOKEN_KEY

def test_configure_env_file_preserves_existing_token_and_unrelated_settings(tmp_path):
    path=tmp_path/".env"
    path.write_text("GOZ_IHALE_API_WRITE_TOKEN=existing-secret\nCUSTOM_SETTING=keep\nGOZ_IHALE_PORT=8123\n",encoding="utf-8")
    generated=configure_env_file(path)
    assert generated is False
    content=path.read_text(encoding="utf-8")
    assert "GOZ_IHALE_API_WRITE_TOKEN=existing-secret" in content
    assert "CUSTOM_SETTING=keep" in content
    assert "GOZ_IHALE_PORT=8123" in content
    for key,value in VALUES.items():
        assert f"{key}={value}" in content
    assert content.count("GOZ_IHALE_ENABLED_SOURCE_KEYS=")==1
    assert path.stat().st_mode & 0o777 == 0o600

def test_configure_env_file_generates_token_for_missing_or_placeholder(tmp_path):
    path=tmp_path/".env"
    path.write_text(f"{TOKEN_KEY}=replace-with-a-strong-random-secret\n",encoding="utf-8")
    generated=configure_env_file(path)
    assert generated is True
    token=next(line.split("=",1)[1] for line in path.read_text().splitlines() if line.startswith(TOKEN_KEY+"="))
    assert len(token)==64
    assert all(c in "0123456789abcdef" for c in token)
