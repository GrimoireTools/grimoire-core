"""
Logging configuration for costilla-bot.

Sets up Loguru with:
- Colored stderr output for local development
- Axiom sink for persistent log storage (requires AXIOM_TOKEN and AXIOM_DATASET env vars)
"""

import sys
from typing import TYPE_CHECKING, Any

from loguru import logger

from grimoire_core.varenv import get_env

if TYPE_CHECKING:
    from collections.abc import Callable


def _build_axiom_sink() -> tuple[Callable[[Any], None] | None, str | None]:
    """Return an Axiom sink function, or None if credentials are not configured."""
    try:
        token = get_env("AXIOM_TOKEN")
        dataset = get_env("AXIOM_DATASET")
    except KeyError, FileNotFoundError:
        return None, None

    if not token or not dataset:
        return None, None

    try:
        import axiom_py

        client = axiom_py.Client(token)
    except ImportError:
        logger.warning("axiom-py not installed. Axiom logging disabled. Run: pip install axiom-py")
        return None, None

    def axiom_sink(message: Any) -> None:
        record = message.record
        event = {
            "message": record["message"],
            "level": record["level"].name.lower(),
            "time": record["time"].isoformat(),
            "module": record["module"],
            "function": record["function"],
            "line": record["line"],
        }
        if record["exception"] is not None:
            event["exception"] = str(record["exception"])
        try:
            client.ingest_events(dataset, [event])
        except Exception as e:
            # Avoid recursive logging errors
            print(f"[Axiom sink error] {e}", file=sys.stderr)

    return axiom_sink, dataset


def setup_logging() -> None:
    """Configure all log sinks. Call once at startup."""
    logger.remove()
    logger.add(sys.stderr, colorize=True)

    axiom_sink, dataset = _build_axiom_sink()
    if axiom_sink:
        logger.add(axiom_sink, level="DEBUG")
        logger.info(f"Axiom logging enabled (dataset: {dataset})")
    else:
        logger.warning("Axiom logging not configured. Set AXIOM_TOKEN and AXIOM_DATASET to enable.")
