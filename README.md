# legion-spike-receipt-auditor

A tiny offline tool for saved EVM-style receipts. Python 3.12; no runtime dependencies.
Input is JSONL: `chainId` (positive integer metadata), `transactionHash`, `status`, `gasUsed`.
Hashes are 32-byte hex strings; status and gas use hexadecimal RPC-style quantities.
The sample is synthetic. Chain identity is supplied by the file, not verified with a node.
MIT licensed; part of the [Legion tool spikes](https://github.com/ivanserbanuk2002).

Audit counts and gas totals use unique `(chainId, transactionHash)` receipts.
Exact duplicates are reported; conflicting duplicates fail. Failed transactions still use gas.
Gas units are not fees, value transfers or profit; extra RPC receipt fields are ignored.

Install with `python -m pip install .`, then run
`receipt-auditor --input data/sample-receipts.jsonl --chain-id 56 --status failed`.
The default output is JSON. Filters apply before duplicate auditing.
Input errors exit 2 without a partial report. No RPC or account credentials are used.

Files ending in `.gz` are read as gzip-compressed UTF-8 JSONL using Python's
standard library, for example `receipt-auditor --input receipts.jsonl.gz`.
Other paths use plain UTF-8 JSONL. Invalid gzip data or UTF-8 exits 2.

`--format csv` prints the same numeric summary as a header and one CSV row.
An empty filtered selection yields zero counts, not a missing report.

`receipt-auditor --input receipts.jsonl.gz --group-by chain` produces one
summary per chain, keyed by chain-ID strings in JSON. Add `--format csv` for
rows with `chain_id` followed by the same summary columns, in ascending chain
order. `--chain-id` and `--status` filters apply before grouping and auditing;
duplicates and conflicts stay scoped to each chain. An empty grouped selection
produces `{}` in JSON or only the CSV header. Omitting `--group-by` keeps the
flat summary.

## Development

`python -m unittest discover -s tests -v` runs offline tests. CI tests Python 3.12
on pushes and pull requests. See [CONTRIBUTING](CONTRIBUTING.md).
Status: working offline spike; no protocol-log decoding or confirmation checks.
