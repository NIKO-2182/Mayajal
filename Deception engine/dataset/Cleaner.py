import re
import json

INPUT = "Jsonl path to be cleaned"
OUTPUT = "Jsonl path to save cleaned data"

PROMPT = "user@ubuntu:~$ "

def clean_text(text: str) -> str:
    # Remove noisy success phrase
    text = re.sub(r"\n*Command completed successfully\.?\n*", "\n", text)

    # Collapse 3+ newlines → 2 newlines
    text = re.sub(r"\n{3,}", "\n\n", text)

    # Ensure it ends with a prompt
    if not text.rstrip().endswith(PROMPT.strip()):
        text = text.rstrip() + "\n\n" + PROMPT

    return text

with open(INPUT, "r") as fin, open(OUTPUT, "w") as fout:
    for line in fin:
        obj = json.loads(line)
        obj["text"] = clean_text(obj["text"])
        fout.write(json.dumps(obj) + "\n")
