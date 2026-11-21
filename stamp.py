#!/usr/bin/env python3
"""Weekly outside timestamp for Vota's ledger copy, made with OpenTimestamps.

Every Sunday it writes a small checkpoint file for the newest day in ledger.jsonl and asks the public
OpenTimestamps calendars to stamp it into the Bitcoin blockchain. Every run it also asks for any waiting
proofs to be completed (this takes a few hours) and writes timestamps.json, the list the Vota page reads.

Needs the `ots` command (pip install opentimestamps-client). Standard library otherwise.
Check a proof yourself:  ots verify checkpoints/<day>.txt.ots
The checkpoint file holds only the day's number, date and fingerprint. Nothing in it names a community, a person or a vote.
"""
import datetime, json, os, re, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
LEDGER = os.path.join(HERE, "ledger.jsonl")
DIR = os.path.join(HERE, "checkpoints")
INDEX = os.path.join(HERE, "timestamps.json")
BLOCK = re.compile(r"BitcoinBlockHeaderAttestation\((\d+)\)")


def read_ledger():
    if not os.path.exists(LEDGER):
        sys.exit("No ledger.jsonl here yet. Nothing stamped.")
    with open(LEDGER) as f:
        rows = [json.loads(line) for line in f if line.strip()]
    if not rows:
        sys.exit("ledger.jsonl is empty. Nothing stamped.")
    return rows


def checkpoint_text(row):
    return f"vota-ledger-checkpoint-v1\nseq: {row['seq']}\nday: {row['day']}\nentry_hash: {row['entry_hash']}\n"


def ots(*args):
    return subprocess.run(["ots", *args], capture_output=True, text=True)


def block_of(proof):
    """The earliest Bitcoin block number in the proof, else None.

    A proof can hold several calendars' answers, some finished and some still waiting, so one
    finished answer is enough, and the earliest block is the one that matters."""
    r = ots("info", proof)
    found = BLOCK.findall((r.stdout or "") + (r.stderr or ""))
    return min(int(b) for b in found) if found else None


def stamp_new(rows, force):
    today = datetime.datetime.now(datetime.timezone.utc)
    if not force and today.weekday() != 6:  # Sunday
        return
    row = rows[-1]
    txt = os.path.join(DIR, f"{row['day']}.txt")
    if os.path.exists(txt + ".ots"):
        return
    os.makedirs(DIR, exist_ok=True)
    with open(txt, "w") as f:
        f.write(checkpoint_text(row))
    r = ots("stamp", txt)
    if not os.path.exists(txt + ".ots"):
        os.remove(txt)
        print("Stamping did not work this time; will try again next run.", (r.stderr or r.stdout).strip())


def main():
    force = "--force" in sys.argv
    rows = read_ledger()
    os.makedirs(DIR, exist_ok=True)
    by_seq = {r["seq"]: r for r in rows}
    stamp_new(rows, force)
    out = []
    if os.path.isdir(DIR):
        for name in sorted(os.listdir(DIR)):
            if not name.endswith(".txt"):
                continue
            txt = os.path.join(DIR, name)
            proof = txt + ".ots"
            if not os.path.exists(proof):
                continue
            with open(txt) as f:
                text = f.read()
            m = re.search(r"seq: (\d+)\nday: (\S+)\nentry_hash: (\w{64})\n", text)
            if not m:
                sys.exit(f"BREAK: {name} is not a checkpoint file.")
            seq, day, h = int(m.group(1)), m.group(2), m.group(3)
            if seq not in by_seq or by_seq[seq]["entry_hash"] != h or by_seq[seq]["day"] != day:
                sys.exit(f"BREAK: checkpoint {name} does not match the ledger.")
            block = block_of(proof)
            if block is None:
                ots("upgrade", proof)
                for leftover in (proof + ".bak",):
                    if os.path.exists(leftover):
                        os.remove(leftover)
                block = block_of(proof)
            out.append({"seq": seq, "day": day, "entry_hash": h, "status": "final" if block else "pending", "block": block})
    with open(INDEX, "w") as f:
        json.dump(out, f, indent=1)
        f.write("\n")
    print(f"{len(out)} timestamps, {sum(1 for o in out if o['status'] == 'final')} final.")


if __name__ == "__main__":
    main()
