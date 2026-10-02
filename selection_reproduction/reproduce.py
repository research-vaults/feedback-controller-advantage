"""Recompute selection counts and clustered intervals; Python3/NumPy only."""
from pathlib import Path
from collections import defaultdict,Counter
import json
import numpy as np
P=Path(__file__).resolve().parent
rows=json.loads((P/'SELECTION_ROWS.json').read_text());expected=json.loads((P/'SELECTION_AUDIT.json').read_text());checks=0

def eq(x,y):
 global checks
 np.testing.assert_allclose(x,y,rtol=0,atol=1e-12);checks+=1

assert len(rows)==560 and len({(r['model'],r['screen'],r['run'],r['round']) for r in rows})==560
for r in rows:
 selected='LLM' if r['first_geometry_score']<r['second_geometry_score'] else 'U1'
 assert selected==r['chosen_mixed'];assert r['mixed_selected_hits']==r['llm' if selected=='LLM' else 'u1']
 assert r['uniform_selected_hits'] in [r['u1'],r['u2']]
 assert r['mixed_regret']==max(r['llm'],r['u1'])-r['mixed_selected_hits']>=0
 assert r['uniform_regret']==max(r['u1'],r['u2'])-r['uniform_selected_hits']>=0
 assert r['oracle_increment']==max(r['llm'],r['u1'])-max(r['u1'],r['u2'])
 assert r['selected_increment']==r['mixed_selected_hits']-r['uniform_selected_hits']==r['oracle_increment']-r['excess_regret']
 for prefix,a,b,regret in [('mixed','llm','u1','mixed_regret'),('uniform','u1','u2','uniform_regret')]:
  assert r[prefix+'_strict']==int(r[a]!=r[b]);assert r[prefix+'_correct']==int(r[a]!=r[b] and r[regret]==0)
keys=['oracle_increment','selected_increment','mixed_regret','uniform_regret','excess_regret','mixed_strict','mixed_correct','uniform_strict','uniform_correct']
for budget in [640,160]:
 rs=[r for r in rows if r['budget']==budget];e=expected['results'][str(budget)];assert len(rs)==e['states']
 counts=Counter(('LLM_better' if r['llm']>r['u1'] else 'U1_better' if r['u1']>r['llm'] else 'tied',r['chosen_mixed']) for r in rs)
 for truth in ['LLM_better','U1_better','tied']:
  for chosen in ['LLM','U1']:assert counts[truth,chosen]==e['matrix'][truth][chosen]
 parents=defaultdict(list)
 for r in rs:parents[r['model'],r['screen'],r['run']].append(r)
 assert len(parents)==e['starts'] and all({r['round'] for r in rr}=={1,2,3,4} for rr in parents.values())
 cells=defaultdict(list)
 for (m,s,n),rr in sorted(parents.items()):cells[m,s].append(np.mean([[r[k] for k in keys] for r in rr],axis=0))
 rng=np.random.default_rng(20260924);bs=[]
 for cell,v in sorted(cells.items()):
  x=np.array(v);bs.append(x[rng.integers(len(x),size=(20000,len(x)))].mean(1))
 bs=np.mean(bs,axis=0)
 for i,k in enumerate(keys[:5]):eq(np.mean([r[k] for r in rs]),e['means'][k]);eq(np.quantile(bs[:,i],[.025,.975]),e['intervals_95'][k])
 for prefix,i in [('mixed',5),('uniform',7)]:
  den=sum(r[prefix+'_strict'] for r in rs);num=sum(r[prefix+'_correct'] for r in rs);q=e[prefix+'_strict_choice'];assert (num,den)==(q['correct'],q['eligible']);eq(num/den,q['accuracy']);valid=bs[:,i]>0;assert (~valid).sum()==q['zero_denominator_bootstraps'];eq(np.quantile(bs[valid,i+1]/bs[valid,i],[.025,.975]),q['interval95'])
 print(f'PASS B{budget}: {len(rs)} states/{len(parents)} starts, choice matrix and paired uncertainty')
print(f'PASS {checks} numerical comparisons;560 score/outcome identities; saved-state scope only')
