import json
from dataclasses import dataclass, asdict, field
from typing import List, Tuple, Dict, Optional

@dataclass
class WorkflowState:
    image_path: str = ""
    legend_path: str = ""
    legend_box: Optional[Tuple[int, int, int, int]] = None
    detected_symbols: List[Dict] = field(default_factory=list)
    ocr_texts: List[Dict] = field(default_factory=list)
    linked_items: List[Tuple] = field(default_factory=list)
    generated_tasks: List[str] = field(default_factory=list)
    config: Dict = field(default_factory=dict)

    def to_json(self, filepath: str):
        with open(filepath, 'w') as f:
            json.dump(asdict(self), f, indent=2)

    @staticmethod
    def from_json(filepath: str) -> "WorkflowState":
        try:
            with open(filepath, 'r') as f:
                data = json.load(f)
            return WorkflowState(**data)
        except Exception as e:
            print(f"⚠ Failed to load session: {e}")
            return WorkflowState()

    def reset(self):
        self.image_path = ""
        self.legend_path = ""
        self.legend_box = None
        self.detected_symbols.clear()
        self.ocr_texts.clear()
        self.linked_items.clear()
        self.generated_tasks.clear()
        self.config.clear()

    def summary(self) -> Dict[str, str]:
        return {
            "image_path": self.image_path,
            "legend_path": self.legend_path,
            "legend_box": str(self.legend_box),
            "symbols": str(len(self.detected_symbols)),
            "ocr_blocks": str(len(self.ocr_texts)),
            "linked": str(len(self.linked_items)),
            "tasks": str(len(self.generated_tasks))
        }

# Global state instance
state: WorkflowState = WorkflowState()
