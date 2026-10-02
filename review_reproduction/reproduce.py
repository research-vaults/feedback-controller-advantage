"""Portable review-check replay: Python3 + NumPy, no network, keys or features."""
from pathlib import Path
import csv,json,itertools
import numpy as np
P=Path(__file__).resolve().parent
rows=list(csv.DictReader((P/'review_records.csv').open()))
for r in rows:
 for k in r:
  if k not in ['model','screen','study']:r[k]=float(r[k])
assert len(rows)==720 and len({(r['model'],r['screen'],r['start']) for r in rows})==720
for r in rows:
 n,h,t,y,b=[r[k] for k in ['pool_size','pool_hits','prefix_tests','prefix_hits','remaining_tests']]
 assert t+b==640
 lo=y+max(0,b-((n-h)-(t-y)))-r['uniform'];hi=y+min(b,h-y)-r['uniform']
 np.testing.assert_allclose([lo,hi],[r['lower_delta'],r['upper_delta']],atol=0,rtol=0)
 assert lo<=r['delta']<=hi
for n in range(1,9):
 for h in range(n+1):
  for k in range(n+1):
   values=[sum(i<h for i in subset) for subset in itertools.combinations(range(n),k)]
   assert min(values)==max(0,k-(n-h)) and max(values)==min(k,h)
def estimate(sub,field='delta'):
 rng=np.random.default_rng(190919);boot=np.zeros(20000);means=[]
 cells=sorted({(r['model'],r['screen']) for r in sub})
 for cell in cells:
  x=np.array([r[field] for r in sub if (r['model'],r['screen'])==cell]);means.append(x.mean());boot+=x[rng.integers(len(x),size=(20000,len(x)))].mean(1)/len(cells)
 return [float(np.mean(means)),*np.quantile(boot,[.025,.975])]
expected=json.loads((P/'expected_review_checks.json').read_text())
car=[r for r in rows if r['study']=='CAR-T released unpublished'];pub=[r for r in rows if r['study']!='CAR-T released unpublished']
for key,sub in [('pooled',rows),('without_phi4',[r for r in rows if not r['model'].startswith('phi')]),('car_t',car),('published_b640',pub)]:
 np.testing.assert_allclose(estimate(sub),[expected[key]['mean'],*expected[key]['interval']],atol=1e-10,rtol=0)
for field,name in [('lower_delta','lower'),('upper_delta','upper')]:np.testing.assert_allclose(estimate(rows,field)[0],expected['recovery'][name],atol=1e-10,rtol=0)
rng=np.random.default_rng(190920);boot=np.zeros(20000)
for sub,sign in [(pub,1),(car,-1)]:
 cells=sorted({(r['model'],r['screen']) for r in sub})
 for cell in cells:
  x=np.array([r['delta'] for r in sub if (r['model'],r['screen'])==cell]);boot+=sign*x[rng.integers(len(x),size=(20000,len(x)))].mean(1)/len(cells)
np.testing.assert_allclose(np.quantile(boot,[.025,.975]),expected['published_minus_car_t']['interval'],rtol=0,atol=1e-10)
print('PASS: per-start bounds, exhaustive finite-pool formula, all review-check means and intervals.')

learned=list(csv.DictReader((P/'learned_outcomes.csv').open()));expected=json.loads((P/'expected_learned.json').read_text());assert len(learned)==120
for rival in ['uniform','llm']:
 rng=np.random.default_rng(190921);boot=np.zeros(20000);means=[]
 for model in sorted({r['initializer'] for r in learned}):
  x=np.array([float(r['assayformer'])-float(r[rival]) for r in learned if r['initializer']==model]);assert len(x)==20;means.append(x.mean());boot+=x[rng.integers(20,size=(20000,20))].mean(1)/6
 e=expected['contrasts']['assayformer_minus_'+rival];np.testing.assert_allclose([np.mean(means),*np.quantile(boot,[.0125,.9875])],[e['mean'],*e['interval']],atol=1e-10,rtol=0)
print('PASS: learned-reference paired means and adjusted intervals.')
