import json
from pathlib import Path
from modules.research import sections,rank,cited_lines,analyze
from modules.visuals import render_diagram,render_data
from modules.reports import save_report

def test_sections():
    rows=list(sections([{'text':'2. Methodology\nWe measured samples.\nResults\nValues increased.','page_number':2,'section':None},{'text':'More results','page_number':3,'section':None}]))
    assert [r['section'] for r in rows]==['methodology','results','results']

def test_rank():
    fixture=json.loads((Path(__file__).parents[1]/'evaluation/methodology.json').read_text())
    rows=[{'chunk_id':str(i),'document_id':'a','chunk_text':p['text'],'section':p['section']} for i,p in enumerate(fixture['passages'])]
    assert rank(fixture['question'],rows,[],True)[0]['section']=='methodology'

def test_citations():
    assert cited_lines('Claim [2]\nBad [9]\nUnsupported',[{},{}])=='Claim [2]'

def test_stages():
    calls=[]
    def fake(p): calls.append(p); return 'Measured 30 samples [1]'
    assert analyze('methodology',[{'source_filename':'test','chunk_text':'Measured 30 samples'}],fake)=='Measured 30 samples [1]'
    assert len(calls)==3

def test_exports(tmp_path):
    messages=[{'role':'assistant','content':'Measured samples [1]'}]
    for ext in ['docx','pdf','txt']:
        p=tmp_path/f'report.{ext}';save_report(p,messages);assert p.stat().st_size>0

def test_visuals(tmp_path):
    for kind in ['flow','mind']:
        p=tmp_path/f'{kind}.png';render_diagram('Collect samples [1]\nAnalyze samples [2]',p,kind);assert p.stat().st_size>0
    p=tmp_path/'chart.svg';render_data(['A','B'],[1,2],p);assert p.stat().st_size>0
