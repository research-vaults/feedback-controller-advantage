"""Replay a saved acquisition from frozen ranks; no network or feature regeneration."""
from pathlib import Path
import json
x=json.loads(Path(__file__).with_name('INSTANCE.json').read_text())
centres=json.loads(x['raw_response'])['centres']
centres=[g.strip().upper() for g in centres]
assert centres==x['normalized_centres'] and len(set(centres))==5
initial=set(x['initial_genes']);hits=set(x['hit_genes'])
assert len(initial)==128 and len(hits)==x['eligible_hits']
assert len(initial&hits)==x['initial_hits']==6
selected=[];used=set(initial)
for i,r in enumerate(x['ranked_neighbours']):
 assert r['centre']==centres[i]
 quota=128//5+(i<128%5)
 assert r['quota']==quota
 assert len(r['ranked_candidates'])==len(set(r['ranked_candidates']))==128
 batch=[]
 for g in r['ranked_candidates']:
  if g in used:continue
  used.add(g);selected.append(g);batch.append(g)
  if len(batch)==quota:break
 assert len(batch)==quota
assert len(selected)==len(set(selected))==128
assert not initial.intersection(selected)
assert selected==x['expected_batch']
new_hits=len(hits.intersection(selected))
assert new_hits==x['expected_new_hits']==8
assert len(hits.intersection(used))==x['expected_cumulative_hits']==14
print('PASS: five parsed centres; ordered128gene batch;8 new hits;14 total/256tests.')
print('Scope: frozen ranked-neighbour replay, not all-pool feature or live model regeneration.')
