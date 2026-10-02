from .parser import Receipt


def summarise(receipts: list[Receipt]) -> dict[str, int]:
    seen: dict[tuple[int, str], Receipt] = {}
    result = dict(records=len(receipts), unique=0, duplicates=0,
                  succeeded=0, failed=0, gas_used=0)
    for receipt in receipts:
        key = (receipt.chain_id, receipt.transaction_hash)
        if key in seen:
            if receipt != seen[key]:
                raise ValueError(f"conflicting duplicate receipt: {key}")
            result["duplicates"] += 1
            continue
        seen[key] = receipt
        result["unique"] += 1
        result["succeeded" if receipt.status else "failed"] += 1
        result["gas_used"] += receipt.gas_used
    return result


def summarise_by_chain(receipts: list[Receipt]) -> dict[str, dict[str, int]]:
    groups: dict[int, list[Receipt]] = {}
    for receipt in receipts:
        groups.setdefault(receipt.chain_id, []).append(receipt)
    return {str(chain): summarise(groups[chain]) for chain in sorted(groups)}
