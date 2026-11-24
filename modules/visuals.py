import textwrap
from modules.research import diagram_steps

def render_diagram(answer, path, kind='flow'):
    from matplotlib.figure import Figure
    steps=diagram_steps(answer)
    if not steps: raise ValueError('No cited statements to visualize.')
    fig=Figure(figsize=(10,max(5,len(steps)*1.2))); ax=fig.subplots(); ax.axis('off')
    ax.set_title('Evidence outline — relationships and order require review',fontsize=13)
    for i,step in enumerate(steps):
        y=1-(i+.7)/(len(steps)+1); x=.5 if kind=='flow' else (.25 if i%2 else .75)
        ax.text(x,y,'\n'.join(textwrap.wrap(step,85 if kind=='flow' else 42)),ha='center',va='center',fontsize=9,transform=ax.transAxes,bbox=dict(boxstyle='round,pad=.5',fc='#eef2ff',ec='#64748b'))
        if kind=='flow' and i: ax.annotate('',xy=(x,y+.025),xytext=(x,y+.7/(len(steps)+1)),xycoords=ax.transAxes,arrowprops=dict(arrowstyle='->',color='#64748b'))
    fig.savefig(path,bbox_inches='tight',dpi=150)

def render_data(labels, values, path):
    from matplotlib.figure import Figure
    if not labels or len(labels)!=len(values): raise ValueError('Provide matching labels and numeric values.')
    fig=Figure(figsize=(8,5)); ax=fig.subplots(); ax.bar(labels,values); ax.tick_params(axis='x',rotation=30); fig.tight_layout(); fig.savefig(path,dpi=150)
