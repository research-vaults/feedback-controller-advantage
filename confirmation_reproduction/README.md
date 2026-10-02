# Confirmation evidence: statistics and saved-trace audit

From the manuscript source root:

- `python3 confirmation_reproduction/reproduce.py` reproduces the saved paired terminal and clustered-preview statistics using Python 3 and NumPy.
- `python3 confirmation_reproduction/audit_traces.py` uses only the Python standard library and reconstructs the campaign endpoint tables from compressed traces.

Both are offline and make no paid calls. The trace audit covers 80 Qwen2.5/Ministral starts and 40 Gemini starts on Carnevale/IL2: 480 full campaigns, 1,920 adaptive decisions, including 960 small-model and 480 native-interface LLM decisions. All initial batches and four rounds are retained. The small panel has 26 decisions with recovery; the native panel has zero. These are decision counts, not independent starts or new biological sources.

The archive includes all 1,740 saved physical call records for these suffixes (including unsuccessful attempts). It preserves requests, response contents, attempt status, usage, timestamps and charged/conservative costs. Provider request IDs and system fingerprints were omitted. The manifest gives hashes of original source files, the compressed artifact and its uncompressed content. No credentials, personal email addresses, account names or machine-specific home paths were found by the documented pattern checks; this is scoped screening, not a guarantee of all possible privacy properties.

The audit checks SHA-256 identities, request-prompt hashes, response-content consistency, recorded centre occurrence in successful responses, nonoverlapping 128-gene batches, each policy's own growing history, hit sums, 640-gene terminal budgets and exact agreement with every paired-outcome row. It is a saved-record audit, not an independent reimplementation of the original parser. It does not check whether an unknown gene was incorrectly admitted to the eligible pool, recompute neighbour order or distances, independently verify label provenance, or prove prompt nonleakage. Full requests permit further inspection of these questions.

Historical initialization raw calls, the original primary panel, preview raw calls and failed technical pilots are outside this archive. The initial decisions are included as the shared starting point, so the audit can reconstruct complete yield but cannot audit how those initial calls were generated. Preview summaries/protocol remain available for numerical replay. This scope must not be described as all project raw evidence or full acquisition regeneration.

Feature access/redistribution, complete portable acquisition dependencies, public hosting and new-generation replication remain open. API versions can change; fresh sampling is a different replication target from saved-output verification. Report any failure instead of treating a successful summary replay as proof of complete reproducibility.
