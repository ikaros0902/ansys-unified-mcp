"""Questions the tool cannot decide alone.

Every question has a stable key (for example 'vendor_stackup.thickness_column' or
'copper_fr4.L27').  The answer is looked up in config["answers"] first.  If it is
missing:
  * interactive mode  -> the question is asked in the terminal and the answer is stored
  * non-interactive   -> the question is written to open_questions.md and the run
                         stops (exit code 2); an AI or a colleague fills
                         config["answers"][key] and runs again
Answers are written back into the project JSON so the same question is never asked twice.
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path

from .util import NeedAnswer


@dataclass
class Question:
    key: str
    text: str
    options: list[tuple[str, str]]          # (value, description)
    context: str = ""
    allow_free_text: bool = False


@dataclass
class Asker:
    interactive: bool
    answers: dict
    log: object
    asked: list[Question] = field(default_factory=list)
    pending: list[Question] = field(default_factory=list)

    def choose(self, q: Question) -> str:
        values = [v for v, _ in q.options]
        if q.key in self.answers:
            a = str(self.answers[q.key])
            if a in values or q.allow_free_text:
                self.log(f"  answer from config: {q.key} = {a}")
                return a
            raise NeedAnswer(f"config answer {q.key}={a!r} is not one of {values}")
        if not self.interactive:
            self.pending.append(q)
            raise NeedAnswer(q.key)
        self.log("")
        self.log("=" * 78)
        self.log(f"QUESTION [{q.key}]")
        self.log(q.text)
        if q.context:
            self.log(q.context)
        for i, (v, desc) in enumerate(q.options, 1):
            self.log(f"  {i}) {v}    {desc}")
        while True:
            raw = input("Enter the number of your choice"
                        + (" (or type a value)" if q.allow_free_text else "") + ": ").strip()
            if raw.isdigit() and 1 <= int(raw) <= len(values):
                a = values[int(raw) - 1]
                break
            if q.allow_free_text and raw:
                a = raw
                break
            print("  not a valid choice, try again")
        self.answers[q.key] = a
        self.asked.append(q)
        self.log(f"  -> {q.key} = {a}")
        return a

    def write_pending(self, path: Path) -> None:
        lines = ["# Open questions", "",
                 "The run stopped because these questions have no answer yet. A human decides them;",
                 "the order of the options is not a recommendation. More questions can follow on the next run.",
                 "Put the chosen value into the project JSON under \"answers\":",
                 "", "```json", '"answers": {', f'  "{self.pending[0].key}": "<the chosen option>",' if
                 self.pending else '  "key": "value",',
                 '  "_note": "<who decided, why, date>"', "}", "```", ""]
        for q in self.pending:
            lines += [f"## `{q.key}`", "", q.text, ""]
            if q.context:
                lines += ["```", q.context, "```", ""]
            lines += ["Options:", ""] + [f"- `{v}`" + (f": {d}" if d else "") for v, d in q.options] + [""]
        path.write_text("\n".join(lines), encoding="utf-8")


def save_answers(config_path: Path, answers: dict) -> None:
    """Merge answers into the project JSON (other content is kept)."""
    data = json.loads(config_path.read_text(encoding="utf-8"))
    data.setdefault("answers", {})
    data["answers"].update(answers)
    config_path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
