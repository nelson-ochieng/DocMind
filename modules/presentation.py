import html,re

def render(text, links):
    """Safe limited Markdown, inline citation links, readable Unicode math."""
    out=[]
    for line in text.splitlines():
        if not line.strip():continue
        s=html.escape(line)
        s=re.sub(r'\[(\d+)\]',lambda m:f'<a href="source:{links[int(m[1])]}">[{m[1]}]</a>' if int(m[1]) in links else m[0],s)
        s=re.sub(r'\*\*(.+?)\*\*',r'<b>\1</b>',s)
        s=s.replace(r'\times','×').replace(r'\leq','≤').replace(r'\geq','≥').replace(r'\alpha','α').replace(r'\beta','β')
        if s.startswith('### '):out.append('<h3>'+s[4:]+'</h3>')
        elif s.startswith('## '):out.append('<h2>'+s[3:]+'</h2>')
        elif s.startswith('- '):out.append('<p style="margin-left:12px">• '+s[2:]+'</p>')
        else:out.append('<p>'+s+'</p>')
    return ''.join(out)
