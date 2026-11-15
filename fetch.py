#!/usr/bin/env python3
"""Pulls Vota's public master ledger and appends new days to ledger.jsonl.

It refuses (exits with an error, writes nothing) if:
  - an entry already saved here no longer matches what Vota now says it was, or
  - any entry's fingerprint does not match its own contents, or
  - an entry does not link to the one before it.
Standard library only, so anyone can read and run it.
"""
import hashlib, json, os, sys, urllib.request

URL = "https://whgpyapexkqlkjixwexx.supabase.co/rest/v1/rpc/master_export"
KEY = "sb_publishable_ziYYKso2SqFzNA67WbgeaA_xHXui8WH"  # public by design: it is in the Vota web app too
FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ledger.jsonl")
FIELDS = ("seq", "day", "root", "prev_hash", "entry_hash")


def entry_hash(seq, prev, day, root):
    return hashlib.sha256(f"vota-master-v1|{seq}|{prev}|{day}|{root}".encode()).hexdigest()


def fetch_all():
    rows, after = [], 0
    while True:
        req = urllib.request.Request(URL, data=json.dumps({"p_after": after}).encode(),
                                     headers={"apikey": KEY, "Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=30) as r:
            page = json.load(r)
        rows += page
        if len(page) < 1000:
            return rows
        after = page[-1]["seq"]


def main():
    remote = [{k: r[k] for k in FIELDS} for r in fetch_all()]
    if not remote:
        sys.exit("Vota returned an empty ledger. Nothing was written.")
    prev = "0" * 64
    for i, r in enumerate(remote, 1):
        if r["seq"] != i:
            sys.exit(f"BREAK: entry {i} is missing from Vota's ledger.")
        if r["prev_hash"] != prev:
            sys.exit(f"BREAK: entry {i} does not link to the entry before it.")
        if r["entry_hash"] != entry_hash(r["seq"], r["prev_hash"], r["day"], r["root"]):
            sys.exit(f"BREAK: entry {i} does not match its own fingerprint.")
        prev = r["entry_hash"]
    local = []
    if os.path.exists(FILE):
        with open(FILE) as f:
            local = [json.loads(line) for line in f if line.strip()]
    for i, l in enumerate(local):
        if i >= len(remote) or l != remote[i]:
            sys.exit(f"BREAK: entry {i + 1} was saved here earlier but Vota now says something different. Nothing was written.")
    new = remote[len(local):]
    if new:
        with open(FILE, "a") as f:
            for r in new:
                f.write(json.dumps(r, separators=(",", ":")) + "\n")
    print(f"{len(remote)} entries checked, {len(new)} new.")


if __name__ == "__main__":
    main()
