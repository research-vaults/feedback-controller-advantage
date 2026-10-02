from pathlib import Path
import json,csv
A=Path(__file__).resolve().parent
b=json.loads((A/'TRAJECTORY_BOUNDS.json').read_text());r=json.loads((A/'PARTIAL_RESULTS.json').read_text())
terms={'instruction_random':{'LLM_RANDOM_TRUTH':1,'LLM_RANDOM_FIXED':-1},'controller_truthful_nn':{'LLM_NN_FREE':1,'UNIFORM_NN_FREE':-1},'opportunity_interaction_nn':{'LLM_NN_OBSERVED':1,'UNIFORM_NN_OBSERVED':-1,'LLM_NN_FREE':-1,'UNIFORM_NN_FREE':1}}
assert len(b)==20
for name,co in terms.items():
 lo=sum(sum(c*x[k]['lo' if c>0 else 'hi'] for k,c in co.items()) for x in b.values())/20
 hi=sum(sum(c*x[k]['hi' if c>0 else 'lo'] for k,c in co.items()) for x in b.values())/20
 expected=r['prespecified_contrast_bounds'][name]['fixed_planned_panel_bound']
 assert max(abs(lo-expected[0]),abs(hi-expected[1]))<1e-9
 print(name,lo,hi)
assert r['status']=='INTERRUPTED_NOT_CONFIRMATORY'
rows=list(csv.DictReader((A/'PAIRED_OUTCOMES_PARTIAL.csv').open()))
assert len(rows)==20
for k,n in r['terminal_campaigns'].items():assert sum(x[k]!='' for x in rows)==n
print('PASS: saved-status and missing-trajectory bound replay; not a completed experiment or raw-feature regeneration')

# Retrospective outer-envelope sensitivity, separate from confirmation.
import numpy as np
z=json.loads((A/'BOUND_SENSITIVITY.json').read_text());keys=sorted(b);sources=np.array([k.split('|')[0] for k in keys]);rng=np.random.default_rng(260926)
idx=np.concatenate([rng.choice(np.flatnonzero(sources==s),(20000,10),replace=True) for s in sorted(set(sources))],axis=1)
for name,co in terms.items():
 lo=np.array([sum(c*b[k][arm]['lo' if c>0 else 'hi'] for arm,c in co.items()) for k in keys],float)
 hi=np.array([sum(c*b[k][arm]['hi' if c>0 else 'lo'] for arm,c in co.items()) for k in keys],float)
 expected=z['contrasts'][name];envelope=[float(np.quantile(lo[idx].mean(1),.05/6)),float(np.quantile(hi[idx].mean(1),1-.05/6))]
 assert np.allclose(envelope,expected['bootstrap_outer_envelope'],rtol=0,atol=1e-9)
 for s in sorted(set(sources)):assert np.allclose([lo[sources==s].mean(),hi[sources==s].mean()],expected['source_point_bounds'][s],rtol=0,atol=1e-9)
 for fraction in [0,.25,.5,.75,1]:
  means=(lo+fraction*(hi-lo))[idx].mean(1)
  assert np.quantile(means,.05/6)>=envelope[0]-1e-9 and np.quantile(means,1-.05/6)<=envelope[1]+1e-9
 print(name,'outer envelope',envelope)
print('PASS: sensitivity-envelope/source replay; no population-coverage or complete-study certification')
