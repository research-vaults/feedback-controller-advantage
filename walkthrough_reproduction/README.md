# One recorded acquisition

Run `python3 reproduce.py`. No downloads or model calls are made.

This is the first planned native-response confirmation start for the Carnevale adenosine screen, first adaptive round, correct-feedback/NN condition. The example was selected by run order, not yield. The literal prompt and response, source-file checksums, ordered genes and released eligible hit list are in `INSTANCE.json`. The original initial batch contains six hits among 128 genes. Five centres expand into 128 new genes with eight hits:14 hits/256 tests. Gene membership in the released `topmovers` array determines a hit, not an LLM judgment.

The portable check parses the recorded response, assigns 26/26/26/25/25 slots, excludes tested and overlapping genes, compares the ordered batch, and recomputes released-label counts. It uses the first 128 eligible untested neighbours of each centre, already ranked by cosine similarity in the recorded normalized Achilles matrix. Earlier centres can consume at most 103 candidates before the final 25 slots, so these lists suffice for this replay. The full-pool feature calculation was separately rerun locally and exactly reproduced the saved batch. The portable script does not independently establish all-pool ranking, regenerate features, test API access or resample the LLM.

The processed feature-cache checksum is exact; its upstream release date has not been independently verified. File locations in the provenance are project-relative identifiers, not paths needed by this portable check. This one example does not certify all trajectories or demonstrate a typical effect.
