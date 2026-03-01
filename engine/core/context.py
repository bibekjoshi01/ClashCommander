from dataclasses import dataclass, field
from typing import Any, Dict, Optional
import uuid
import time


@dataclass
class ExecutionContext:
    """
    Per-run execution context.

    Shared across:
    - Agent loop
    - Tools
    - Observability layer
    """

    # Unique run identifier
    run_id: str = field(default_factory=lambda: str(uuid.uuid4()))

    # Run metadata
    started_at: float = field(default_factory=time.time)

    # Shared state (mutable memory during run)
    state: Dict[str, Any] = field(default_factory=dict)

    # Optional browser / automation driver
    browser: Optional[Any] = None

    # Optional logger (injectable)
    logger: Optional[Any] = None

    # Arbitrary external dependencies (db clients, storage, etc.)
    resources: Dict[str, Any] = field(default_factory=dict)

    def get(self, key: str, default: Any = None) -> Any:
        return self.state.get(key, default)

    def set(self, key: str, value: Any) -> None:
        self.state[key] = value

    def elapsed(self) -> float:
        return time.time() - self.started_at
