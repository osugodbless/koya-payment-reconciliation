#!/usr/bin/env python3
"""Payment reconciliation.

Reads payments.jsonl and works out how much money we actually collected.
Run:  python3 reconcile.py
"""
import json
from decimal import Decimal


def parse_amount(value):
    if isinstance(value, str):
        value = value.replace(",", "").strip()
    return Decimal(str(value))


latest = {}

with open("payments.jsonl") as f:
    for line in f:
        try:
            event = json.loads(line)
        except (json.JSONDecodeError, UnicodeDecodeError):
            continue
        if not isinstance(event, dict):
            continue
        txn_id = event.get("txn_id")
        if txn_id is None or txn_id == "":
            continue
        current = latest.get(txn_id)
        if current is None or event["ts"] > current["ts"]:
            latest[txn_id] = event

total = Decimal("0")
count = 0

for event in latest.values():
    if event["status"] == "success":
        total += parse_amount(event["amount"])
        count += 1

with open("expected.txt") as f:
    expected = int(f.read().strip())

if count != expected:
    print(f"Check failed: counted {count} successful payments, expected {expected}.")
    print("Something in the data isn't being handled the way the README describes.")
else:
    print(f"Check passed: {count} successful payments.")
    print(f"Your code: KOYA-{round(total)}")
