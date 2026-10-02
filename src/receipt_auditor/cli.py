import argparse
import json
import csv
import sys
import gzip
import zlib
from pathlib import Path

from .audit import summarise, summarise_by_chain
from .parser import parse_receipts


def main() -> int:
    parser = argparse.ArgumentParser(description="Audit saved EVM-style receipt JSONL")
    parser.add_argument("--input", type=Path, default=Path("data/sample-receipts.jsonl"))
    parser.add_argument("--chain-id", type=int)
    parser.add_argument("--status", choices=("succeeded", "failed"))
    parser.add_argument("--format", choices=("json", "csv"), default="json")
    parser.add_argument("--group-by", choices=("chain",))
    args = parser.parse_args()
    if args.chain_id is not None and args.chain_id <= 0:
        parser.error("--chain-id must be positive")
    try:
        opener = gzip.open if args.input.suffix == ".gz" else open
        with opener(args.input, "rt", encoding="utf-8") as source:
            receipts = parse_receipts(source.read())
        if args.chain_id is not None:
            receipts = [item for item in receipts if item.chain_id == args.chain_id]
        if args.status:
            receipts = [item for item in receipts if item.status == int(args.status == "succeeded")]
        result = summarise_by_chain(receipts) if args.group_by else summarise(receipts)
    except (OSError, ValueError, EOFError, zlib.error) as error:
        parser.error(str(error))
    if args.format == "csv":
        fields = ["chain_id", *summarise([])] if args.group_by else list(result)
        writer = csv.DictWriter(sys.stdout, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        if args.group_by:
            writer.writerows({"chain_id": chain, **summary} for chain, summary in result.items())
        else:
            writer.writerow(result)
    else:
        print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
