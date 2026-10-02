"""Offline replay of prespecified bridge and exploratory preview summaries. NumPy only."""
import csv,json,hashlib
from pathlib import Path
import numpy as np
A=Path(__file__).resolve().parent
checks=0
for name in ['small','capable']:
 p=A/(name+'_outcomes.csv');expected=json.loads((A/(name+'_results.json')).read_text());assert hashlib.sha256(p.read_bytes()).hexdigest()==expected['csv_sha256']
 rows=list(csv.DictReader(p.open()))
 for key in ['assignment','availability','controller']:
  rng=np.random.default_rng(202609232345);rep=[];means=[]
  for m,s in sorted({(r['model'],r['screen']) for r in rows}):
   x=np.array([float(r[key]) for r in rows if (r['model'],r['screen'])==(m,s)])
   assert len(x)==20;rep.append(x[rng.integers(20,size=(20000,20))].mean(axis=1));means.append(x.mean())
  lo,hi=np.quantile(np.mean(rep,axis=0),[.05/6,1-.05/6]);actual=[np.mean(means),lo,hi];want=[expected['primary'][key][v] for v in ['mean','low','high']]
  assert np.allclose(actual,want,rtol=0,atol=1e-10),(name,key,actual,want);checks+=3
 print('PASS',name,'three primary means and adjusted intervals')
p=A/'preview_outcomes.csv';expected=json.loads((A/'preview_results.json').read_text());assert hashlib.sha256(p.read_bytes()).hexdigest()==expected['csv_sha256'];rows=list(csv.DictReader(p.open()))
for m in ['qwen25_7b','gemini38']:
 for key,w in expected['results'][m]['pooled'].items():
  starts={}
  for r in rows:
   if r['selector']==m:starts.setdefault((r['generator'],r['screen'],r['start']),[]).append(float(r[key]))
  rng=np.random.default_rng(202609240001);rep=[];means=[]
  for g,s in sorted({(g,s) for g,s,n in starts}):
   x=np.array([np.mean(v) for (gg,ss,n),v in starts.items() if (gg,ss)==(g,s)]);assert len(x)==5
   rep.append(x[rng.integers(5,size=(20000,5))].mean(1));means.append(x.mean())
  lo,hi=np.quantile(np.mean(rep,axis=0),[.025,.975]);assert np.allclose([np.mean(means),lo,hi],[w['mean'],w['low'],w['high']],rtol=0,atol=1e-10),(m,key);checks+=3
print('PASS',checks,'numerical comparisons. Saved-outcome replay, not live API regeneration.')
