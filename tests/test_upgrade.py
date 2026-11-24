from modules.research import analyze, sections

def test_unicode_heading():
    rows=list(sections([{'text':'2  Materials and\u00a0methods\n2.1  Description of\u00a0the method\nCollected data.', 'page_number':4}]))
    assert all('method' in r['section'] for r in rows)

def test_retry_and_fallback():
    calls=[]
    def fake(prompt):
        calls.append(prompt)
        return 'No citations' if len(calls)==1 else 'Collected samples [1]'
    assert 'Collected samples [1]' in analyze('methodology',[{'chunk_text':'Collected samples'}],fake)
    assert 'manual review' in analyze('methodology',[{'chunk_text':'Collected samples'}],lambda p:'No citations')

def test_bad_review_keeps_draft():
    replies=iter(['Collected samples [1]','Collected samples [1]','Bad [99]'])
    assert analyze('methodology',[{'chunk_text':'Collected samples'}],lambda p:next(replies))=='Collected samples [1]'
