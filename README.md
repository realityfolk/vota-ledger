# Vota ledger

A public copy of Vota's master ledger.

Once a day Vota combines the latest fingerprint of every community into one fingerprint and links it to the day before. A GitHub Action in this repository copies that daily entry here. `ledger.jsonl` has one line per day: the day, the combined fingerprint (`root`), the link to the day before (`prev_hash`) and the entry's own fingerprint (`entry_hash`). Nothing in it names a community, a person, a vote or any text.

**Why a copy outside Vota matters.** This repository's history is kept by GitHub, not by Vota. If Vota ever changed its past, the copy here would no longer match, and the Action stops and says so instead of overwriting anything.

**Check it yourself.** `python3 fetch.py` pulls Vota's ledger, checks every link and fingerprint, and refuses if anything saved here disagrees. Each entry's fingerprint is the SHA-256 of `vota-master-v1|seq|prev_hash|day|root`.

This makes changes to Vota's past easy to detect. It does not make them impossible, and it does not show that entries were honest when they were written.
