from dataclasses import dataclass
from typing import Dict


@dataclass
class ModelOutput:
    text: str
    error_code: int
    model_context: Dict = None
