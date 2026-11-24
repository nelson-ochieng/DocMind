import json
from modules.structured import answer,parse
from modules.presentation import render

def test_reject_reasoning_and_fake_quote():
    rows={1:{'chunk_text':'The researchers collected samples using a calibrated instrument.'}}
    assert not parse('I need to focus [1]',rows)
    assert not parse(json.dumps({'facts':[{'source':1,'quote':'The researchers collected 500 samples using a calibrated instrument.','category':'Data acquisition'}]}),rows)

def test_verified_and_rendered():
    q='The researchers collected samples using a calibrated instrument.'
    raw=json.dumps({'facts':[{'source':1,'quote':q,'category':'Data acquisition'}]})
    result=answer('methodology',[{'chunk_text':q}],lambda _:raw)
    assert q+' [1]' in result
    assert 'source:0' in render(result,{1:0})
    assert '&lt;script&gt;' in render('<script>',{})

def test_fallback():
    assert 'manual review' in answer('methodology',[{'chunk_text':'A sample.'}],lambda _: 'I need to think [1]')
