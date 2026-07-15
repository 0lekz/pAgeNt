import logging
import ollama

logger = logging.getLogger(__name__)


def ask(prompt: str, model: str) -> str:
    """Send a single prompt to a local Ollama model and return the reply text."""

    try:
        response = ollama.chat(
            model=model,
            messages=[{"role": "user", "content": prompt}],
        )
        
        logger.info("Ollama call successful", 
                    extra={"data": {"model": model,
                                    "prompt": prompt,
                                    "response": response.message.content}})
    
        return response.message.content

    except Exception as e:
        logger.error("Ollama call failed", extra={"data": {"model": model, "prompt": prompt, "error": str(e)}})
        raise RuntimeError(f"Ollama call failed: {e}") from e
