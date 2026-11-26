from app.collector.registry import SOURCES, list_sources, get_source

def test_registry_has_broad_source_coverage():
    keys = {source.key for source in SOURCES}
    assert {"ekap", "kik", "dmo", "ilan", "resmigazete", "ted", "undp", "worldbank", "ebrd", "ihaletara", "ihale365"} <= keys

def test_sources_are_disabled_by_default():
    assert all(source.enabled is False for source in SOURCES)

def test_aggregators_are_not_official_sources():
    assert get_source("ihaletara").official is False
    assert get_source("ihale365").official is False

def test_group_filter():
    assert all(source.source_group == "international" for source in list_sources("international"))
