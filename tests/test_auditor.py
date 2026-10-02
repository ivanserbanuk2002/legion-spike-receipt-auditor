import json
import unittest
import os
import subprocess
import sys

from receipt_auditor import audit, parser


def record(**changes):
    row = {"chainId": 56, "transactionHash": "0x" + "a" * 64,
           "status": "0x1", "gasUsed": "0x5208"}
    row.update(changes)
    return row


class ParserTests(unittest.TestCase):
    def test_parses_quantities_and_normalises_hash_case(self):
        rows = parser.parse_receipts(json.dumps(record(transactionHash="0x" + "A" * 64)) + "\n\n")
        self.assertEqual((rows[0].chain_id, rows[0].status, rows[0].gas_used), (56, 1, 21000))
        self.assertEqual(rows[0].transaction_hash, "0x" + "a" * 64)

    def test_rejects_invalid_identity_and_quantities(self):
        for change in ({"chainId": True}, {"chainId": 0}, {"transactionHash": "0x12"},
                       {"status": "0x2"}, {"status": 1}, {"gasUsed": "-1"}, {"gasUsed": True}):
            with self.subTest(change=change), self.assertRaises(ValueError):
                parser.parse_receipts(json.dumps(record(**change)))
        for bad in ("[]", "null", "broken"):
            with self.assertRaisesRegex(ValueError, "line 1"):
                parser.parse_receipts(bad)


class AuditTests(unittest.TestCase):
    def test_counts_unique_receipts_with_chain_scoped_duplicates(self):
        text = "\n".join(json.dumps(row) for row in [record(), record(),
               record(chainId=1), record(transactionHash="0x" + "b" * 64, status="0x0")])
        self.assertEqual(audit.summarise(parser.parse_receipts(text)), {
            "records": 4, "unique": 3, "duplicates": 1,
            "succeeded": 2, "failed": 1, "gas_used": 63000,
        })
        self.assertEqual(audit.summarise([])["unique"], 0)

    def test_conflicting_duplicates_are_rejected(self):
        text = json.dumps(record()) + "\n" + json.dumps(record(status="0x0"))
        with self.assertRaisesRegex(ValueError, "conflicting"):
            audit.summarise(parser.parse_receipts(text))


class CliTests(unittest.TestCase):
    def run_cli(self, *args):
        return subprocess.run([sys.executable, "-m", "receipt_auditor.cli", *args],
                              env=os.environ, text=True, capture_output=True)

    def test_filters_saved_sample_and_emits_json(self):
        result = self.run_cli("--input", "data/sample-receipts.jsonl", "--chain-id", "56", "--status", "failed")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout)["failed"], 1)
        self.assertEqual(json.loads(result.stdout)["gas_used"], 42000)

    def test_missing_file_and_bad_chain_fail_without_stdout(self):
        for args in (("--input", "missing.jsonl"), ("--chain-id", "0")):
            result = self.run_cli(*args)
            self.assertEqual(result.returncode, 2)
            self.assertEqual(result.stdout, "")
