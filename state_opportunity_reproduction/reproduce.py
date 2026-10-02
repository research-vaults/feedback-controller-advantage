from pathlib import Path
import json,csv,hashlib
import numpy as np
A=Path(__file__).resolve().parent
rows=list(csv.DictReader((A/'STATE_FEATURES.csv').open()));audit=json.loads((A/'FEATURE_AUDIT.json').read_text());assert hashlib.sha256((A/'STATE_FEATURES.csv').read_bytes()).hexdigest()==audit['features_sha256'];assert len(rows)==720
fields=['log_hits','neighbour_union_fraction','neighbour_overlap','consumed_fraction'];X=np.array([[float(r[k]) for k in fields] for r in rows]);y=np.array([float(r['delta']) for r in rows]);source=np.array([r['source'] for r in rows]);models=np.array([r['model'] for r in rows]);groups=sorted(set(source));identities=sorted(set(models));onehot=np.array([[m==k for k in identities] for m in models],float)
assert all(len({r['source'] for r in rows if r['screen']==s})==1 for s in {r['screen'] for r in rows})
specs={'constant':np.empty((len(rows),0)),'hit_count':X[:,:1],'opportunity':X,'deployment_only':onehot,'hit_deployment':np.c_[X[:,:1],onehot],'opportunity_deployment':np.c_[X,onehot]}
def fit_predict(x,y,tr,te):
 w=np.array([1/np.sum(source[tr]==s) for s in source[tr]]);w*=len(w)/w.sum();ym=np.average(y[tr],weights=w)
 if x.shape[1]==0:return np.full(te.sum(),ym),{'intercept':float(ym),'coefficients':[]}
 mu=np.average(x[tr],axis=0,weights=w);sd=np.sqrt(np.average((x[tr]-mu)**2,axis=0,weights=w));sd[sd<1e-12]=1;z=(x-mu)/sd
 coef=np.linalg.solve((z[tr]*w[:,None]).T@z[tr]+10*np.eye(x.shape[1]),(z[tr]*w[:,None]).T@(y[tr]-ym))
 return z[te]@coef+ym,{'intercept':float(ym),'coefficients':coef.tolist(),'mean':mu.tolist(),'sd':sd.tolist(),'train_sources':sorted(set(source[tr]))}
pred={k:np.zeros(len(rows)) for k in specs};fold={}
for s in groups:
 tr=source!=s;te=~tr;fold[s]={}
 for k,x in specs.items():pred[k][te],fold[s][k]=fit_predict(x,y,tr,te)
 # Labels from the held-out source cannot affect training or predictions.
 mutated=y.copy();mutated[te]+=12345
 for k,x in specs.items():p,_=fit_predict(x,mutated,tr,te);assert np.array_equal(p,pred[k][te]),('heldout_leak',s,k)
metrics={};per={}
for k,v in pred.items():
 per[k]={s:{'n':int(sum(source==s)),'mse':float(np.mean((v[source==s]-y[source==s])**2)),'mae':float(np.mean(abs(v[source==s]-y[source==s]))),'sign_accuracy':float(np.mean((v[source==s]>0)==(y[source==s]>0))),'selected_gain':float(np.mean(y[source==s]*(v[source==s]>0))),'llm_choice_fraction':float(np.mean(v[source==s]>0))} for s in groups}
 metrics[k]={name:float(np.mean([per[k][s][name] for s in groups])) for name in ['mse','mae','sign_accuracy','selected_gain','llm_choice_fraction']}
improve={s:per['hit_count'][s]['mse']-per['opportunity'][s]['mse'] for s in groups};gain=metrics['opportunity']['selected_gain']-metrics['hit_count']['selected_gain'];gate=sum(v>0 for v in improve.values())>=3 and metrics['opportunity']['mse']<metrics['hit_count']['mse'] and gain>=.5
# Conditional paired uncertainty: fixed fitted folds; source/model/run clusters keep correlated readouts together.
contrasts={'mse_improvement_over_hit':(pred['hit_count']-y)**2-(pred['opportunity']-y)**2,'selection_gain_over_hit':y*((pred['opportunity']>0).astype(int)-(pred['hit_count']>0).astype(int)),'mae_improvement_over_hit':abs(pred['hit_count']-y)-abs(pred['opportunity']-y)}
indices_by_group={}
for s in groups:
 for m in identities:
  runs=sorted({int(r['run']) for r in rows if r['source']==s and r['model']==m});indices_by_group[s,m]=[np.array([i for i,r in enumerate(rows) if r['source']==s and r['model']==m and int(r['run'])==run]) for run in runs]
interval={}
for name,values in contrasts.items():
 rng=np.random.default_rng(260927);by_source=[]
 for s in groups:
  by_model=[]
  for m in identities:
   v=np.array([values[ix].mean() for ix in indices_by_group[s,m]]);assert len(v)==20;by_model.append(v[rng.integers(len(v),size=(20000,len(v)))].mean(1))
  by_source.append(np.mean(by_model,axis=0))
 boot=np.mean(by_source,axis=0);interval[name]={'mean':float(np.mean([values[source==s].mean() for s in groups])),'conditional_95_interval':np.quantile(boot,[.025,.975]).tolist(),'scope':'Fitted folds and fixed four sources; does not include training-model or new-source variation'}
out={'status':'EXPLORATORY_DEVELOPMENT_ONLY','states':720,'source_groups':groups,'feature_names':fields,'alpha':10,'primary_models':['constant','hit_count','opportunity'],'deployment_sensitivity_models':['deployment_only','hit_deployment','opportunity_deployment'],'macro_equal_source':metrics,'per_source':per,'conditional_uncertainty':interval,'gate':{'mse_improved_source_count':sum(v>0 for v in improve.values()),'source_count_required':3,'per_source_mse_improvement':improve,'macro_mse_improvement':metrics['hit_count']['mse']-metrics['opportunity']['mse'],'selection_increment_hits128':gain,'required_selection_increment':.5,'passed':bool(gate),'decision':'Proceed to frozen exposed modern-cohort stress test' if gate else 'STOP predictive-rule development before paid campaigns; no modern-cohort scoring or new-source claim'},'absolute_yields':{s:{'llm':float(np.mean([float(r['llm_hits']) for r in rows if r['source']==s])),'uniform':float(np.mean([float(r['uniform_hits']) for r in rows if r['source']==s]))} for s in groups},'coefficients':fold,'checks':{'all_out_of_source':True,'heldout_label_mutation_invariant':True,'all720retained':True},'api_calls':0}
def compare(actual,expected):
 if isinstance(actual,dict):
  assert actual.keys()==expected.keys()
  for k in actual:compare(actual[k],expected[k])
 elif isinstance(actual,list):
  assert len(actual)==len(expected)
  for x,y in zip(actual,expected):compare(x,y)
 elif isinstance(actual,(float,int)) and not isinstance(actual,bool):assert abs(actual-expected)<1e-7,(actual,expected)
 else:assert actual==expected,(actual,expected)
compare(out,json.loads((A/'RESULTS.json').read_text()))
saved=list(csv.DictReader((A/'PREDICTIONS.csv').open()));assert len(saved)==720
for i,row in enumerate(saved):
 for k,v in pred.items():assert abs(float(row[k])-v[i])<1e-7
print('PASS: all720out-of-source predictions, six specifications, source/aggregate metrics, conditional intervals and failed continuation gate reproduced; no file mutation or API calls')
