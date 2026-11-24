import json
from modules.structured import parse, answer

QUOTE = "The researchers collected samples using a calibrated instrument."

def record(source=1, quote=QUOTE, category="Data acquisition"):
    return json.dumps({"facts": [{"source": source, "quote": quote, "category": category}]})

def test_reject_unknown_and_boolean_source():
    allowed = {1: {"chunk_text": QUOTE}}
    assert not parse(record(source=2), allowed)
    assert not parse(record(source=True), allowed)

def test_reject_invented_category():
    assert not parse(record(category="Invented"), {1: {"chunk_text": QUOTE}})

def test_reject_truncated_json():
    assert not parse(record()[:-1], {1: {"chunk_text": QUOTE}})

def test_retry_and_deduplicate():
    responses = iter(["I need to think", record(), record(source=4)])
    sources = [{"chunk_text": QUOTE}] * 4
    result = answer("methodology", sources, lambda _: next(responses))
    assert result.count(QUOTE) == 1
    assert "I need to think" not in result
