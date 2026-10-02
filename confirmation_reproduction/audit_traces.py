"""Offline saved-trace integrity audit; does not regenerate features or model calls."""
from pathlib import Path
import csv,gzip,hashlib,json,collections,math,re
D=Path(__file__).resolve().parent
h=lambda x:hashlib.sha256(x).hexdigest()
def main():
 manifest=json.loads((D/'TRACE_MANIFEST.json').read_text());blob=(D/'campaign_traces.jsonl.gz').read_bytes()
 assert h(blob)==manifest['sha256'];raw=gzip.decompress(blob);assert h(raw)==manifest['uncompressed_sha256']
 blocks=collections.defaultdict(dict);calls=collections.defaultdict(list)
 for line in raw.splitlines():
  z=json.loads(line);key=(z['panel'],z['block'])
  if z['kind']=='decision':
   assert z['file'] not in blocks[key];blocks[key][z['file']]=z['record']
  else:calls[key].append(z['record'])
 summaries={};arm_counts=collections.Counter();recovery=collections.Counter();nsteps=0;nlinked=0
 for panel in ('small','capable'):
  with (D/f'{panel}_outcomes.csv').open() as f:
   summaries[panel]={f"{r['model']}_{r['screen']}_{r['run']}":r for r in csv.DictReader(f)}
 for (panel,block),decisions in blocks.items():
  assert len(decisions)==17,(panel,block)
  init=decisions['INITIAL.json'];initial=init['executed'];assert len(initial)==len(set(initial))==128
  assert [x['gene'] for x in init['truth_batch']]==initial
  assert sum(x['is_hit'] for x in init['truth_batch'])==init['n_hits']
  summary=summaries[panel][block];assert int(summary['initial'])==init['n_hits']
  raw_by_key=collections.defaultdict(list)
  for c in calls[(panel,block)]:
   raw_by_key[c['call_key']].append(c)
   messages=c['payload']['messages'];prompt='\n'.join(m['content'] for m in messages)
   assert h(prompt.encode())==c['prompt_sha256']
   if c['status']=='ok':assert c['response']['choices'][0]['message']['content']==c['content']
  for policy,arm,column in [('LLM','TRUE','TRUE'),('LLM','WITHIN_BATCH_PERMUTED','WITHIN_BATCH_PERMUTED'),('LLM','NO_OUTCOMES','NO_OUTCOMES'),('UNIFORM_HIT','TRUE','UNIFORM')]:
   hist=list(initial);hits=init['n_hits']
   for turn in range(1,5):
    row=decisions[f'{policy}_{arm}_{turn}_NN.json'];assert row['policy']==policy and row['arm']==arm and row['round']==turn
    assert row['tested_before']==hist
    batch=row['executed'];assert len(batch)==len(set(batch))==row['batch_size']==128
    assert not set(batch)&set(hist);assert [x['gene'] for x in row['truth_batch']]==batch
    assert sum(x['is_hit'] for x in row['truth_batch'])==row['n_hits']
    assert [x['gene'] for x in row['slot_provenance']]==batch
    assert len(row['centres'])==len(set(row['centres']))==5
    if policy=='LLM':
     assert row['centres']==row['actor_centres']+row['adapter_centres']
     for attempt in row['attempts']: assert attempt['call_key'] in raw_by_key; nlinked+=1
     successes=[c for attempt in row['attempts'] for c in raw_by_key[attempt['call_key']] if c['status']=='ok']
     assert successes
     text='\n'.join(c['content'] for c in successes).upper()
     assert all(re.search(r'(?<![A-Z0-9_.-])'+re.escape(g.upper())+r'(?![A-Z0-9_.-])',text) for g in row['actor_centres']), (block,turn,'centre absent from saved response')
     arm_counts[panel]+=1;recovery[panel]+=bool(row['adapter_centres'])
    hist.extend(batch);hits+=row['n_hits'];nsteps+=1
   assert len(hist)==len(set(hist))==640
   assert hits==int(summary[column]),(panel,block,column,hits,summary[column])
  for name,a,b in [('assignment','TRUE','WITHIN_BATCH_PERMUTED'),('availability','TRUE','NO_OUTCOMES'),('controller','TRUE','UNIFORM')]:assert int(summary[name])==int(summary[a])-int(summary[b])
 assert len(blocks)==120 and nsteps==1920 and arm_counts=={'small':960,'capable':480}
 assert recovery['capable']==0
 print(json.dumps(dict(status='PASS',blocks=len(blocks),campaigns=len(blocks)*4,adaptive_decisions=nsteps,llm_decisions=dict(arm_counts),decisions_with_recovery=dict(recovery),linked_content_attempts=nlinked,terminal_outcomes_checked=len(blocks)*4,limits='Saved recorded labels/histories only; not independent label verification, feature-neighbour reexecution, proof of prompt nonleakage, or fresh model generation'),indent=2))
if __name__=='__main__':main()
