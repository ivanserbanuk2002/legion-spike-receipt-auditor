# legion-spike-receipt-auditor

A tiny offline tool for saved EVM-style receipts. Python 3.12; no runtime dependencies.
Input is JSONL: `chainId` (positive integer metadata), `transactionHash`, `status`, `gasUsed`.
Hashes are 32-byte hex strings; status and gas use hexadecimal RPC-style quantities.
The sample is synthetic. Chain identity is supplied by the file, not verified with a node.
MIT licensed; part of the [Legion tool spikes](https://github.com/ivanserbanuk2002).

Audit counts and gas totals use unique `(chainId, transactionHash)` receipts.
Exact duplicates are reported; conflicting duplicates fail. Failed transactions still use gas.
Gas units are not fees, value transfers or profit; extra RPC receipt fields are ignored.
