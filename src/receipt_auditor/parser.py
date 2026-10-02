import json
import re
from dataclasses import dataclass


@dataclass(frozen=True)
class Receipt:
    chain_id: int
    transaction_hash: str
    status: int
    gas_used: int


def parse_receipts(text: str) -> list[Receipt]:
    receipts = []
    for number, line in enumerate(text.splitlines(), 1):
        if not line.strip():
            continue
        try:
            row = json.loads(line)
            if not isinstance(row, dict):
                raise ValueError("expected an object")
            chain, tx = row["chainId"], row["transactionHash"]
            status, gas = row["status"], row["gasUsed"]
            if type(chain) is not int or chain <= 0:
                raise ValueError("chainId must be a positive integer")
            if not isinstance(tx, str) or not re.fullmatch(r"0x[0-9a-fA-F]{64}", tx):
                raise ValueError("transactionHash must be a 32-byte hex string")
            if status not in ("0x0", "0x1"):
                raise ValueError("status must be 0x0 or 0x1")
            if not isinstance(gas, str) or not re.fullmatch(r"0x[0-9a-fA-F]+", gas):
                raise ValueError("gasUsed must be a nonnegative hex quantity")
            receipts.append(Receipt(chain, tx.lower(), int(status, 16), int(gas, 16)))
        except (ValueError, KeyError, TypeError) as error:
            raise ValueError(f"line {number}: invalid receipt: {error}") from error
    return receipts
