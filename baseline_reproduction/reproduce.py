from pathlib import Path
import csv,json
import numpy as np

def statistics(rows):
    means={k:float(np.mean([float(r[k]) for r in rows])) for k in ['retuned','original','llm','uniform']}
    contrasts={}
    for left,right in [('retuned','original'),('llm','retuned'),('uniform','retuned')]:
        rng=np.random.default_rng(190923);samples=np.zeros(20000)
        for m in ['qwen25_7b','ministral8b']:
            for s in ['Carnevale22_Adenosine','IL2']:
                diffs=np.array([float(r[left])-float(r[right]) for r in rows if r['model']==m and r['screen']==s])
                assert len(diffs)==20
                samples+=np.mean(diffs[rng.integers(0,len(diffs),(20000,len(diffs)))],axis=1)/4
        contrasts[left+'_minus_'+right]={'mean':means[left]-means[right],'interval':np.quantile(samples,[1/120,119/120]).tolist()}
    return means,contrasts

root=Path(__file__).resolve().parent
with (root/'retuned_outcomes.csv').open() as f: rows=list(csv.DictReader(f))
assert len(rows)==80
expected=json.loads((root/'BASELINE_RESULTS.json').read_text())
means,contrasts=statistics(rows)
assert means==expected['means']
for k,v in contrasts.items():
    np.testing.assert_allclose(v['mean'],expected['contrasts'][k]['mean'],atol=1e-10,rtol=0)
    np.testing.assert_allclose(v['interval'],expected['contrasts'][k]['interval'],atol=1e-10,rtol=0)
dev=json.loads((root/'RETUNED_SETTINGS.json').read_text())
for screen,values in dev['development_means'].items():
    recomputed={k:float(np.mean([r['hits'] for r in dev['development_rows'] if r['screen']==screen and r['setting']==k])) for k in sorted(values)}
    assert recomputed==values
    assert max(recomputed,key=recomputed.get)==dev['selected'][screen]['id']
print('PASS: disjoint-initialization development selection and all three retuning means/adjusted intervals.')
