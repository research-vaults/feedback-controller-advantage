# Do Repeated LLM Decisions Improve CRISPR Hit Discovery?

Version: **2026-10-02 — saved-evidence reproducibility release**.

This repository contains the current offline analysis code, compact experimental results, protocols, example prompts and available confirmation model outputs/traces supporting the paper. The study distinguishes whether correct experimental feedback improves an LLM-guided policy from whether repeated LLM control outperforms an informed numerical controller. Results concern retrospective recovery of released CRISPR hits, not prospective biological efficacy or a universal model ranking.

This is a deliberately bounded reproducibility package. It includes the nine numerical-replay modules and confirmation trace audit accompanying the 30 September 2026 manuscript. It does not contain a manuscript PDF, private reviews, project planning, earlier drafts, all historical raw campaigns or model weights. No conference submission is changed by this release. A public repository linked to a website is **not a certified anonymous reviewer artifact**; keep any reviewer-facing snapshot separate.

## Quick start

Use Python 3.11 or newer and a CPU. Only NumPy is required. Installation may use the network; the analysis commands make no model/API calls and need no credentials. Allow about 1 GB of available memory for the largest trace audit; the repository contains approximately 32 MB of files and expands the trace stream to about 140 MB during verification.

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python -m pip check
.venv/bin/python verify.py
.venv/bin/python reproduce_all.py
```

The runner executes all ten checks in isolated subprocesses, saves their console output under `outputs/`, and writes `outputs/RESULTS.json` with exit codes and runtimes. A failed assertion or nonzero exit stops the run. It never launches paid generation. Re-running replaces only these disposable replay logs.

## Inputs, commands and outputs

All commands below run from the repository root. Each numerical module checks its result against retained expected values with the original tolerances; its JSON output can be redirected to a file. Numerical inputs and protocols are included beside the corresponding script.

| Command (`python3 …`) | Input and scientific function | Output/check |
|---|---|---|
| `reproduction_core/reproduce.py` | 720 paired terminal records: six models × six readouts × 20 starts | Feedback assignment/availability and informed-controller contrasts; paired uncertainty |
| `review_reproduction/reproduce.py` | Saved robustness and learned-reference records | Missing-output bounds, exclusions and learned-reference comparisons; this directory contains scientific analyses, not peer reviews |
| `baseline_reproduction/reproduce.py` | Numerical-baseline outcomes/settings | Reproduces retuned baseline comparisons |
| `synthesis_reproduction/reproduce.py` | Saved initialization, deployment and candidate arrays; protocols and prompt examples | Checks source/initializer and candidate-level contrasts |
| `confirmation_reproduction/reproduce.py` | Expanded-budget, native-interface and preview outcomes | Recomputes complete-campaign confirmation and preview statistics |
| `selection_reproduction/reproduce.py` | Saved candidate pools and selection records | Equal-proposal comparisons and oracle/selector checks |
| `confirmation_reproduction/audit_traces.py` | Gzipped recorded calls, decisions, histories and released labels | Audits 120 starts, 480 campaigns, 1,920 adaptive decisions, 1,740 recorded calls and terminal totals |
| `executor_check_reproduction/reproduce.py` | Partial executor/instruction outcomes | Reproduces bounds for the unfinished 18/20-start study; does not convert it into confirmation |
| `walkthrough_reproduction/reproduce.py` | Frozen neighbour ranks and one recorded batch | Reconstructs the 128-gene worked example and hit accounting |
| `state_opportunity_reproduction/reproduce.py` | 720 saved states, features and predictions | Reproduces the unsuccessful source-excluded prediction challenge |

The main six readouts cover Carnevale adenosine response, Sanchez tau/tau-down, Schmidt IL2/IFNG and the released CAR-T screen. These are four originating sources, not six independent studies. Scharenberg and BioGRID ORCS confirmation results occur in the extended records where identified. Primary outcomes are cumulative released hits under a specified gene-test budget; intervals condition on the tested screens and computational starts. Read module scope notes before combining populations or interpreting an interval.

## Model outputs, traces and fidelity

`confirmation_reproduction/campaign_traces.jsonl.gz` is a single 28.5 MB compressed file, with SHA-256 and source-record inventory in `TRACE_MANIFEST.json`. It contains model responses and prompts, parsed decisions, history, acquired batches and claim-supporting outcome records for the small-model and native-interface confirmation panels. The audit checks prompt hashes, response/decision linkage, tested-gene uniqueness, per-batch and terminal counts, and recovery bookkeeping. Initial-batch decisions are present; their historical raw initialization calls are not. The original primary panel, technical pilots and all other historical raw campaigns are **not** covered by this trace file. The compressed and uncompressed content hashes are preserved unchanged from the source capsule.

Provider request IDs, timestamps, fingerprints and object envelopes were already omitted in preparation of this capsule. Content and archive metadata were checked again for release. Scientific model identifiers, experimental run IDs, prompts, outcomes, negative results and source attribution remain. These records are experimental observations, not clinical advice or independently verified mechanisms.

## Limits and required external inputs

Replay verifies reported computations from saved observations; it is not independent biological replication, a reconstruction of every original acquisition, or proof that all prompts were free of information leakage. Original hosted responses may not be reproducible bit for bit. Equal gene-test budgets do not imply equal token counts, API expense or runtime.

The full Achilles feature matrix and normalized feature cache are excluded because redistribution authority has not been established. The original public source is https://figshare.com/ndownloader/files/49843176 ; obtain appropriate permission before use. No documented command here needs that download. Frozen ranks/features support the included checks, but do not independently validate feature generation or full-pool nearest-neighbour execution. No raw clinical/participant data or third-party model weights are supplied.

## Attribution and licensing

Released screen-derived observations trace to [BioDiscoveryAgent](https://github.com/snap-stanford/BioDiscoveryAgent); its upstream MIT notice is retained in `licenses/BioDiscoveryAgent-MIT.txt`. Gene-screen publications are identified in the supplied protocols. External confirmation uses BioGRID ORCS screen 1107, curating Shifrut et al., Cell (2018), DOI 10.1016/j.cell.2018.10.024. Cite BioGRID (Stark et al., Nucleic Acids Research, 2006, DOI 10.1093/nar/gkj109) and the original experimental source; the BioGRID notice is retained in `licenses/BIOGRID.txt`. Third-party rights and service conditions remain applicable. This release does not assert a new blanket license for original project code or model-generated content; publication of the files is not a waiver of rights. See upstream notices before reuse.

## Integrity and large files

`SHA256SUMS.json` binds all released payload files except itself. `verify.py` also rejects extra, unmanifested tracked payloads, ignoring only documented development/output paths. Gzip and NumPy archives were inspected internally during release checks. No Git LFS, remote release assets or separately authenticated data are required for the documented commands. Future larger collections should be separately versioned with explicit size, hash, license and retrieval instructions; do not silently replace the frozen inputs or duplicate old manuscript archives.

Known experimental limitations—including failed prediction/selection results, source and initializer dependence, and incomplete trajectories—are retained in the modules. Successful reproduction is not a claim of universal scientific validity or conference readiness.
