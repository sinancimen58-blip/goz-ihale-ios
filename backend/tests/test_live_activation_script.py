from pathlib import Path


def test_live_activation_installs_schedule_before_first_scan():
    script = Path(__file__).resolve().parents[1] / "scripts" / "enable_live_collection.sh"
    text = script.read_text(encoding="utf-8")
    cron_setup = text.index("/etc/cron.d/gozihale-collection")
    initial_scan = text.index("python3 scripts/run_live_scan.py")
    assert cron_setup < initial_scan
