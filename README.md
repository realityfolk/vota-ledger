# Vota ledger

A public copy of Vota's master ledger.

Once a day Vota combines the latest fingerprint of every community into one fingerprint and links it to the day before. A GitHub Action in this repository copies that daily entry here. `ledger.jsonl` has one line per day: the day, the combined fingerprint (`root`), the link to the day before (`prev_hash`) and the entry's own fingerprint (`entry_hash`). Nothing in it names a community, a person, a vote or any text.

**Why a copy outside Vota matters.** This repository's history is kept by GitHub, not by Vota. If Vota ever changed its past, the copy here would no longer match, and the Action stops and says so instead of overwriting anything.

**Check it yourself.** `python3 fetch.py` pulls Vota's ledger, checks every link and fingerprint, and refuses if anything saved here disagrees. Each entry's fingerprint is the SHA-256 of `vota-master-v1|seq|prev_hash|day|root`.

This makes changes to Vota's past easy to detect. It does not make them impossible, and it does not show that entries were honest when they were written.

**A weekly outside timestamp.** Every Sunday the Action also writes a small checkpoint file for the newest day (`checkpoints/<day>.txt`: the day's number, date and fingerprint, nothing else) and asks the public OpenTimestamps calendars to stamp it into the Bitcoin blockchain. The proof sits beside it as `<day>.txt.ots`. A proof is pending for a few hours, then the Action completes it on a later run. `timestamps.json` lists each stamp and whether it is final; the Vota page reads it.

**Check a timestamp yourself.** Install the OpenTimestamps client (`pip install opentimestamps-client`) and run `ots verify checkpoints/<day>.txt.ots`. Or drop both files on opentimestamps.org. A proof shows the checkpoint existed by the date of the Bitcoin block it names. It does not show that the entries were honest when they were written.
