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
        return {"correct_tool": None, "note": "manual review"}

    expected = prompt["expected_tool"]
    if expected is None:
        correct_tool = (called_names == [])
    elif isinstance(expected, list):
        correct_tool = (set(called_names) == set(expected))
    else:
        correct_tool = (called_names == [expected])

    if not correct_tool or "expected_args" not in prompt:
        args_valid = None
    else:
        actual_args = tool_calls[0].function.arguments
        args_valid = True
        for key, expected_val in prompt["expected_args"].items():
            actual_val = actual_args.get(key, "")
            if key in ("content", "query", "claim"):
                args_valid &= bool(actual_val.strip())
            else:
                args_valid &= expected_val.lower() in actual_val.lower()

    return {"correct_tool": correct_tool, "args_valid": args_valid}


BENCH_DIR = Path(__file__).parent
prompts = load_json(BENCH_DIR / "prompts.json")
tools = load_json(BENCH_DIR / "tools.json")
multi_tool_prompts = [p for p in prompts if p["category"] == "multi_tool"]

MODELS = ["gemma4:12b", "ornith-1.5:9b", "qwen3.5:9b", "qwen3:14b"]
N = 1  # single try, this is a diagnostic rerun not a full benchmark

results = []
for model in MODELS:
    for each_prompt in multi_tool_prompts:
        for i in range(N):
            start = time.perf_counter()
            try:
                response = ollama.chat(
                    model=model,
                    messages=[{"role": "user", "content": each_prompt["prompt"]}],
                    tools=tools,
                )
                actual_tool_calls = response.message.tool_calls
                response_content = response.message.content
                grading = grade(each_prompt, actual_tool_calls)
            except ollama.ResponseError as e:
                actual_tool_calls = None
                response_content = None
                grading = {"correct_tool": False, "args_valid": None, "note": f"parse_error: {e}"}

            latency = time.perf_counter() - start
            print(f"Model: {model}, Prompt: {each_prompt['id']}, Latency: {latency}")

            tool_calls_serialized = json.dumps([
                {"name": tc.function.name, "arguments": dict(tc.function.arguments)}
                for tc in actual_tool_calls
            ]) if actual_tool_calls else json.dumps([])

            results.append({
                "model": model,
                "prompt_id": each_prompt["id"],
                "category": each_prompt["category"],
                "run_index": i,
                "correct_tool": grading["correct_tool"],
                "args_valid": grading.get("args_valid"),
                "tool_calls": tool_calls_serialized,
                "response_content": response_content,
                "latency": latency,
                "timestamp": time.time(),
            })
            # save each iteration to have results in case of crash
            pd.DataFrame(results).to_csv(BENCH_DIR / "multitool_diagnostic.csv", index=False)
