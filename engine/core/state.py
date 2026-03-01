from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional

from engine.providers.base import LLMMessage


@dataclass
class AgentState:
    run_id: str

    # Conversation with the model
    messages: List[LLMMessage] = field(default_factory=list)

    # Execution tracking
    step_count: int = 0
    max_steps: int = 40

    # Collected during execution
    issues: List[Dict[str, Any]] = field(default_factory=list)

    # Final state
    finished: bool = False
    final_output: Optional[str] = None

    def add_message(self, message: LLMMessage) -> None:
        self.messages.append(message)

    def next_step(self) -> None:
        self.step_count += 1

    def can_continue(self) -> bool:
        return not self.finished and self.step_count < self.max_steps
