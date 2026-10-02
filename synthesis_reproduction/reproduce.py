"""Portable statistics replay from saved outcomes: Python 3 + NumPy, no network.
Not regeneration of LLM proposals or original native-feature acquisition.
"""
from pathlib import Path
from collections import defaultdict
import json
import numpy as np
R=Path(__file__).resolve().parent
read=lambda n:json.loads((R/n).read_text())
checks=0
def equal(a,b):
 global checks
 np.testing.assert_allclose(a,b,rtol=0,atol=1e-10);checks+=1

def stat(rows,key,level=.95):
 groups=defaultdict(list)
 for r in rows:groups[r['model'],r['screen']].append(r[key])
 rng=np.random.default_rng(20260921);draws=[]
 for k in sorted(groups):
  v=np.array(groups[k]);draws.append(v[rng.integers(len(v),size=(20000,len(v)))].mean(1))
 return [np.mean([np.mean(v) for v in groups.values()]),*np.quantile(np.mean(draws,axis=0),[(1-level)/2,1-(1-level)/2])]
def check_stats(rows,expected):
 for k,e in expected.items():equal(stat(rows,k),[e['mean'],*e['interval']])
rows=read('PAIRED_OUTCOMES.json');d=read('DISTRIBUTION.json');assert len(rows)==720
for r in rows:
 assert r['delta']==r['llm']-r['uniform'] and r['oracle_gain']==max(r['delta'],0)
 assert r['llm']==r['initial']+r['llm_adaptive'] and r['uniform']==r['initial']+r['uniform_adaptive']
check_stats(rows,d['pooled'])
for src,e in d['source'].items():check_stats([r for r in rows if r['source']==src],e)
v=np.array([r['delta'] for r in rows]);equal(np.quantile(v,[0,.05,.25,.5,.75,.95,1]),list(d['quantiles'].values()))
assert [sum(v>0),sum(v<0),sum(v==0)]==[223,460,37]
print('PASS original absolute, adaptive, alternative endpoint, distribution and policy oracle statistics')
rows=read('BRANCH_ROWS.json');e=read('BRANCH_SUMMARY.json');assert len(rows)==80
for r in rows:equal(r['downstream'],r['immediate']+r['future_compensation'])
for rnd,by in e['results'].items():
 for src,expect in by.items():check_stats([r for r in rows if r['round']==int(rnd) and (src=='pooled' or r['screen']==src)],expect)
print('PASS saved-state common-continuation estimates, source splits and intervals')
rows=read('CANDIDATE_ROWS.json');e=read('CANDIDATE_SUMMARY.json');assert len(rows)==560
groups=defaultdict(list)
for r in rows:
 assert r['oracle_increment']==max(r['llm'],r['u1'])-max(r['u1'],r['u2'])
 assert r['mixed_regret']>=0 and r['uniform_regret']>=0
 groups[r['model'],r['screen'],r['run']].append(r)
keys=list(e['results']['640']);starts=[]
for (m,s,n),rr in groups.items():
 assert len(rr)==4 and {r['round'] for r in rr}=={1,2,3,4}
 starts.append(dict(model=m,screen=s,run=n,budget=rr[0]['budget'],**{k:float(np.mean([r[k] for r in rr])) for k in keys}))
for scope,expect in e['results'].items():
 subset=[r for r in starts if (str(r['budget'])==scope if scope in ['640','160'] else r['screen']==scope)]
 check_stats(subset,expect)
print('PASS candidate supply, selection, regret, overlap and numerical-tie sensitivity statistics')
x=np.load(R/'modern_arrays.npz')['round_hits'];total=x.sum(-1);e=read('INITIALIZER_RECONSTRUCTION.json')
rng=np.random.default_rng(20260913223125);idx=rng.integers(0,40,size=(2,50000,40))
def modern(v,level):
 draws=np.stack([v[s][idx[s]].mean(1) for s in range(2)])
 return [v.mean(),*np.quantile(draws.mean(0),[(1-level)/2,1-(1-level)/2])]
for mi,m in enumerate(['gemini38','deepseek4']):
 v=total[:,:,mi];rgL=v[:,:,0,0,0];rgU=v[:,:,0,1,0];rcL=v[:,:,1,0,0];rcU=v[:,:,1,1,0];liL=v[:,:,2,0,0];liU=v[:,:,2,1,0];ee=e['models'][m]
 ds=dict(Control_after_LLM_init=liL-liU,LLM_init_minus_random_centre_under_uniform=liU-rcU,Matched_initializer_controller_interaction=liL-liU-rcL+rcU,Availability_LLM=rgL-v[:,:,0,0,2],Assignment_LLM=rgL-v[:,:,0,0,1],Control_after_random_genes=rgL-rgU)
 for k,z in ds.items():q=ee['primary'][k];equal(modern(z,q['level']),[q['mean'],*q['interval']])
 q=ee['random_centre_controller'];equal(modern(rcL-rcU,.95),[q['mean'],*q['interval']])
 for ii,name in enumerate(['random_genes','random_centre_NN','LLM_centre_NN']):
  for pi,pol in enumerate(['LLM','uniform']):q=ee['absolute'][name][pol];equal(modern(v[:,:,ii,pi,0],.95),[q['mean'],*q['interval']])
assert np.array_equal(x[:,:,0,:2,1,0],x[:,:,1,:2,1,0])
print('PASS twelve modern primary intervals, random-centre contrasts, absolute outcomes and shared controls')
print(f'PASS {checks} numerical comparisons; scope: saved-outcome replay, not live model regeneration')
