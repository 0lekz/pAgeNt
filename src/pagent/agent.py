# ReAct loop here

# will call llm.py and tools.py
#

import logging

from pagent import llm, tools

logger = logging.getLogger(__name__)

# arbitrary safeguards for now
MAX_STEPS = 10
MAX_RESULT_CHARS = 4000 

def _truncate(result: str) -> str:
    if len(result) <= MAX_RESULT_CHARS:
        return result
    return result[:MAX_RESULT_CHARS] + "\n[truncated]"

def run(messages: list, model: str) -> str:
    """Run the ReAct loop until the model returns a plain-text answer.

    Mutates 'messages' in place, appending each assistant and tool message.
    """
    for _ in range(MAX_STEPS):
        message = llm.chat(messages, model, tools=tools.schemas())
        messages.append(message)

        if not message.tool_calls:
            return message.content

        for call in message.tool_calls:
            name = call.function.name
            arguments = call.function.arguments
            result = _truncate(tools.execute(name, arguments))
            logger.info(
                "tool_call",
                extra = {
                    "data": {"tool": name, "arguments": arguments, "result": result}
                },
            )

            messages.append(
                {"role": "tool", "content": result, "tool_name": name}
            )

    return "[reached MAX_STEPS without a final answer]"
