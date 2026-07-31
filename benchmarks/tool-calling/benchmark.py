# load tools.json, prompts.json

import pandas as pd
import json
import time
from pathlib import Path

import ollama

def load_json(filename):
    with open(filename, "r") as f:
        return json.load(f)


def grade(prompt, tool_calls):
    called_names = [tc.function.name for tc in tool_calls] if tool_calls else []
    if prompt["category"] == "ambiguous":
        return {"correct_tool": None, "note": "manual review"} # don't auto-score

    expected = prompt["expected_tool"]
    if expected is None:
        correct_tool = (called_names == [])
    elif isinstance(expected, list):
        correct_tool = (set(called_names) == set(expected))
    else:
        correct_tool = (called_names == [expected])

    # only meaningful when correct_tool and expected_args exists;
    # for example in multi_tool prompts they currently don't
    # simple field (location) -> equality/substring check
    # free-text field (content) -> just check non-empy, not exact match
    if not correct_tool or "expected_args" not in prompt:
        args_valid = None # not applicable
    else:
        actual_args = tool_calls[0].function.arguments
        args_valid = True
        for key, expected_val in prompt["expected_args"].items():
            actual_val = actual_args.get(key, "")
            if key == "content":
                args_valid &= bool(actual_val.strip())
            else:
                args_valid &= expected_val.lower() in actual_val.lower()

    return {"correct_tool": correct_tool, "args_valid": args_valid}

BENCH_DIR = Path(__file__).parent
prompts = load_json(BENCH_DIR / "prompts.json")
tools = load_json(BENCH_DIR / "tools.json")
model = "gemma4:12b"  # one model per run
N = 5  # number of runs per prompt

results = []
for each_prompt in prompts:
    for i in range(N):
        start = time.perf_counter()
        response = ollama.chat(
            model=model,
            messages=[{"role": "user", "content": each_prompt["prompt"]}],
            tools=tools,
        )
        latency = time.perf_counter() - start
        print(f"Prompt: {each_prompt['id']}, Latency: {latency}")

        actual_tool_calls = response.message.tool_calls  # None or list
        # continue with grading this run against prompt["expected_tool"] / expected_args
        # append results to a list for later analysis

        grading = grade(each_prompt, actual_tool_calls)
        results.append({
            "model": model,
            "prompt_id": each_prompt["id"],
            "category": each_prompt["category"],
            "run_index": i,
            "correct_tool": grading["correct_tool"],
            "args_valid": grading.get("args_valid"), # .get() so missing key doesn't crash 
            "latency": latency,
            "timestamp": time.time(),
        })
      
pd.DataFrame(results).to_csv(BENCH_DIR / "benchmark_results.csv", index=False)
