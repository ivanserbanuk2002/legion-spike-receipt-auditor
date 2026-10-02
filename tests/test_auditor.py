import json
import unittest

from receipt_auditor import parser


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
