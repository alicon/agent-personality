"""Validate invented episodes and mask only assistant content in Qwen chat text."""
import hashlib
import json
from pathlib import Path

MINIMAL_SYSTEM = "You are a scientific and computational assistant. Use the supplied task facts."
MARKERS = ("<|im_start|>", "<|im_end|>", "<think>", "</think>")


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=False).encode()).hexdigest()


def load_episodes(path):
    episodes = [json.loads(line) for line in Path(path).read_text().splitlines() if line.strip()]
    ids, families, texts = set(), {}, {}
    for row in episodes:
        if set(row) != {"id", "family", "split", "audience", "traits", "origin", "review", "messages"}:
            raise ValueError("Episode fields must match the closed schema")
        for key in ("id", "family", "audience"):
            if not isinstance(row[key], str) or not row[key].strip():
                raise ValueError(f"Missing {key}")
        if row["id"] in ids:
            raise ValueError("Duplicate episode ID")
        ids.add(row["id"])
        if row["origin"] != "wholly_invented" or row["review"] not in ("agent_authored_unreviewed", "human_reviewed"):
            raise ValueError("Explicit invented provenance and review status required")
        if row["split"] not in ("train", "validation"):
            raise ValueError("Only development train/validation splits are accepted")
        previous = families.setdefault(row["family"], row["split"])
        if previous != row["split"]:
            raise ValueError("Scenario family leaked across splits")
        if not isinstance(row["traits"], list) or not row["traits"] or not all(isinstance(t, str) and t for t in row["traits"]):
            raise ValueError("Trait annotations required")
        messages = row["messages"]
        if not isinstance(messages, list) or len(messages) < 2 or len(messages) % 2:
            raise ValueError("Complete user/assistant exchanges required")
        for i, msg in enumerate(messages):
            expected = "user" if i % 2 == 0 else "assistant"
            if set(msg) != {"role", "content"} or msg["role"] != expected:
                raise ValueError("Roles must alternate user/assistant; system is assembled centrally")
            if not isinstance(msg["content"], str) or not msg["content"].strip():
                raise ValueError("Empty message")
            if any(marker in msg["content"] for marker in MARKERS):
                raise ValueError("Reserved template markers are not allowed in episode text")
            fingerprint = digest(msg["content"].strip())
            if fingerprint in texts and texts[fingerprint] != row["split"]:
                raise ValueError("Exact message duplicate crossed splits")
            texts[fingerprint] = row["split"]
    if not episodes or {r["split"] for r in episodes} != {"train", "validation"}:
        raise ValueError("Nonempty train and validation splits required")
    return episodes


def encode_episode(row, tokenizer, max_length):
    messages = [{"role": "system", "content": MINIMAL_SYSTEM}] + row["messages"]
    rendered = tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=False, enable_thinking=False)
    # Validate against the model's actual template, including its final empty think block.
    spans, cursor = [], 0
    for message in messages:
        header = f'<|im_start|>{message["role"]}\n'
        start = rendered.find(header, cursor)
        end = rendered.find("<|im_end|>", start + len(header))
        if start != cursor or end < 0:
            raise ValueError("Unsupported chat-template layout")
        content = message["content"]
        if rendered[end - len(content):end] != content:
            raise ValueError("Template changed the message content")
        if message["role"] == "assistant":
            spans.append((end - len(content), end + len("<|im_end|>")))
        cursor = end + len("<|im_end|>\n")
    if cursor != len(rendered):
        raise ValueError("Unexpected chat-template tail")
    encoded = tokenizer(rendered, add_special_tokens=False, return_offsets_mapping=True)
    if len(encoded["input_ids"]) > max_length:
        raise ValueError(f'Episode {row["id"]} exceeds sequence limit; never silently truncate')
    labels = [token if any(a < end and b > start for a, b in spans) else -100
              for token, (start, end) in zip(encoded["input_ids"], encoded["offset_mapping"])]
    if not any(label != -100 for label in labels):
        raise ValueError("No assistant loss tokens")
    return {"input_ids": encoded["input_ids"], "attention_mask": encoded["attention_mask"], "labels": labels}


def collate(rows, pad_token_id):
    import torch
    length = max(len(row["input_ids"]) for row in rows)
    return {key: torch.tensor([row[key] + [pad] * (length - len(row[key])) for row in rows])
            for key, pad in (("input_ids", pad_token_id), ("attention_mask", 0), ("labels", -100))}


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", default="data/development.jsonl")
    parser.add_argument("--tokenizer-check", action="store_true")
    args = parser.parse_args()
    rows = load_episodes(args.data)
    result = {"episodes": len(rows), "families": len({r["family"] for r in rows}), "data_sha256": digest(rows),
              "human_reviewed": sum(r["review"] == "human_reviewed" for r in rows),
              "splits": {s: sum(r["split"] == s for r in rows) for s in ("train", "validation")}}
    if args.tokenizer_check:
        from transformers import AutoTokenizer
        tokenizer = AutoTokenizer.from_pretrained("Qwen/Qwen3-14B", revision="40c069824f4251a91eefaf281ebe4c544efd3e18")
        encoded = [encode_episode(r, tokenizer, 4096) for r in rows]
        result.update(total_tokens=sum(len(r["input_ids"]) for r in encoded),
                      max_tokens=max(len(r["input_ids"]) for r in encoded),
                      assistant_loss_tokens=sum(sum(t != -100 for t in r["labels"]) for r in encoded),
                      chat_template_sha256=hashlib.sha256(tokenizer.chat_template.encode()).hexdigest())
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
