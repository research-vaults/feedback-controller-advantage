"""Saved-outcome replay. Requires Python 3 and numpy; no network/model calls."""
import csv, json, hashlib
from pathlib import Path
import numpy as np
root=Path(__file__).resolve().parent
rows=list(csv.DictReader((root/'outcomes.csv').open()))
assert len(rows)==720
assert len({(r['model'],r['screen'],r['start']) for r in rows})==720
cells=sorted({(r['model'],r['screen']) for r in rows})
assert len(cells)==36
contrasts={'assignment':('llm_true','llm_permuted'), 'availability':('llm_true','llm_withheld'), 'controller':('llm_true','uniform_true')}
results={}
for name,(a,b) in contrasts.items():
    rng=np.random.default_rng(80908)
    boot=np.zeros(20000);means=[]
    for cell in cells:
        z=np.array([float(r[a])-float(r[b]) for r in rows if (r['model'],r['screen'])==cell])
        assert len(z)==20
        means.append(z.mean())
        boot+=z[rng.integers(0,len(z),(20000,len(z)))].mean(1)/len(cells)
    tail=.05/3/2
    results[name]={'mean':float(np.mean(means)), 'interval':np.quantile(boot,[tail,1-tail]).tolist(), 'level':1-.05/3}
# This is a new retrospective three-contrast reporting family. Original four-contrast
# primary intervals are not replaced or selected according to the results.
out={'n_starts':720,'n_cells':36,'draws':20000,'seed':80908,'results':results,
     'outcomes_sha256':hashlib.sha256((root/'outcomes.csv').read_bytes()).hexdigest()}
expected=root/'EXPECTED_RESULTS.json'
if expected.exists():
    old=json.loads(expected.read_text())
    assert out['outcomes_sha256']==old['outcomes_sha256']
    for key in results:
        np.testing.assert_allclose([results[key]['mean'],*results[key]['interval']], [old['results'][key]['mean'],*old['results'][key]['interval']],rtol=0,atol=1e-10)
    print('PASS: all three means and intervals match the retained result.')
print(json.dumps(out,indent=2))
