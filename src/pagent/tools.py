
# main tools. read_file, list_directory, etc.
#
#
import inspect
import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Callable

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class Tool:
    name: str
    schema: dict
    fn: Callable[..., str]
    
def read_file(path:str) -> str:
    return Path(path).read_text()

def list_directory(path: str) -> str:
    return "\n".join(sorted(p.name for p in Path(path).iterdir()))

# Tool schemas
# ---
READ_FILE_SCHEMA = {
    "type": "function",
    "function": {
        "name": "read_file",
        "description": "Read and return the contents of a text-based file such as code, markdown, or notes",
        "parameters": {
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "The path to the file"},
            },
            "required": ["path"],
        },
    },
}

LIST_DIRECTORY_SCHEMA = {
    "type": "function",
    "function": {
        "name": "list_directory",
        "description": "List files and subdirectories at a given path",
        "parameters": {
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "The directory path to list"},

            },
            "required": ["path"],
        },
    },
}
# ---schemas


TOOLS = [
    Tool("read_file", READ_FILE_SCHEMA, read_file),
    Tool("list_directory", LIST_DIRECTORY_SCHEMA, list_directory),

]

def _validate(tool: Tool) -> None:
    spec = tool.schema["function"]
    if spec["name"] != tool.name:
        raise ValueError(f"{tool.name}: schema name is {spec['name']!r}")
    
    declared = set(spec["parameters"]["properties"])
    actual = set(inspect.signature(tool.fn).parameters)
    if declared != actual:
        raise ValueError(f"{tool.name}: schema params {declared} != function params {actual}")
    
    assert isinstance(spec["description"], str)
    assert isinstance(spec["parameters"]["required"], dict)
    assert isinstance(spec["parameters"]["properties"], dict)

for _tool in TOOLS:
    _validate(_tool)


REGISTRY = {t.name: t for t in TOOLS}

def schemas() -> list[dict]:
    return [t.schema for t in TOOLS]

def execute(name: str, arguments: dict) -> str:
    tool = REGISTRY.get(name)

    if tool is None:
        return f"Error: no tool named '{name}'. Available: {', '.join(REGISTRY)}"

    try:
        logger.info("Executing tool=%s arguments=%s", name, arguments)
        result = tool.fn(**arguments)
        logger.info("Tool completed: %s", name)
        return result
    except Exception as e:
        # for recovery loop
        logger.exception("Tool failed: %s", name)
        return f"Error: `{type(e).__name__}: {e}`"
