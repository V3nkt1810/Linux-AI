# prep_dataset.py
import csv, json, argparse
from pathlib import Path

parser = argparse.ArgumentParser()
parser.add_argument("--csv", required=True)
parser.add_argument("--out", default="dataset.jsonl")
parser.add_argument("--max_rows", type=int, default=None)
args = parser.parse_args()

in_path = Path(args.csv)
out_path = Path(args.out)
count = 0

with in_path.open() as f_in, out_path.open("w") as f_out:
    reader = csv.DictReader(f_in)
    for row in reader:
        if args.max_rows and count >= args.max_rows:
            break
        instruction = row.get("instruction","").strip()
        commands = row.get("commands","").strip()
        explanation = row.get("explanation","").strip()
        rollback = row.get("rollback","").strip()
        # Build a training target: JSON action object as string (the model will be trained to return just this)
        target = {
            "action": "run_commands",
            "commands": [c.strip() for c in commands.splitlines() if c.strip()],
            "explanation": explanation,
            "rollback": rollback if rollback else None
        }
        sample = {
            "instruction": instruction,
            "response": target
        }
        f_out.write(json.dumps(sample, ensure_ascii=False) + "\n")
        count += 1

print(f"Wrote {count} rows to {out_path}")
