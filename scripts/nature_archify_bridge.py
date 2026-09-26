#!/usr/bin/env python
"""
nature-archify Python bridge.

Thin Python wrapper over the nature-archify Node CLI
(nature-archify/bin/archify.mjs).

Used by math-read-do scripts that need to render architecture / workflow /
sequence / dataflow / lifecycle diagrams without writing shell glue.

Typical use:

    from nature_archify_bridge import NatureArchitecture
    cli = NatureArchitecture()             # auto-locate the skill root
    cli.doctor()                           # returns parsed status dict
    cli.validate("architecture", "spec.json", quality="showcase")
    cli.deliver("architecture", "spec.json", "out.html", quality="showcase")
    cli.visual_check("out.html")           # bounded browser evidence

The bridge returns parsed JSON when the upstream command supports --json,
and raises RuntimeError with the CLI's stderr message on non-zero exit.
"""

from __future__ import annotations

import json
import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable, Optional


_SKILL_DIR_CANDIDATES: tuple[Path, ...] = (
    Path(__file__).resolve().parent.parent / "nature-archify",
    Path(__file__).resolve().parent.parent.parent / "archify-main" / "archify",
    Path(__file__).resolve().parent / "_skill_dir",
)


def _locate_skill_root() -> Path:
    for candidate in _SKILL_DIR_CANDIDATES:
        if (candidate / "bin" / "archify.mjs").is_file():
            return candidate
    env = Path(__file__).resolve().parent / "_skill_dir"
    if env.is_dir() and (env / "bin" / "archify.mjs").is_file():
        return env
    raise FileNotFoundError(
        "Cannot locate nature-archify skill root. "
        "Tried: " + ", ".join(str(p) for p in _SKILL_DIR_CANDIDATES)
    )


@dataclass
class CliResult:
    ok: bool
    exit_code: int
    payload: Any
    stdout: str
    stderr: str


class NatureArchitecture:
    DIAGRAM_TYPES: tuple[str, ...] = (
        "architecture", "workflow", "sequence", "dataflow", "lifecycle",
    )
    QUALITY_PROFILES: tuple[str, ...] = ("standard", "showcase")
    ANIMATION_MODES: tuple[str, ...] = ("trace", "none")
    VISUAL_PRESETS: tuple[str, ...] = (
        "classic", "signal-flow", "blueprint", "editorial",
        "paper", "paper-dark", "brutalism", "playful", "neumorphism",
        "memphis", "glass", "bauhaus", "apple",
    )

    def __init__(self, skill_root: Optional[Path] = None, node_bin: Optional[str] = None) -> None:
        self.skill_root = Path(skill_root) if skill_root else _locate_skill_root()
        self.cli = self.skill_root / "bin" / "archify.mjs"
        if not self.cli.is_file():
            raise FileNotFoundError(f"CLI not found: {self.cli}")
        self.node_bin = node_bin or shutil.which("node")
        if not self.node_bin:
            raise FileNotFoundError("node executable not found on PATH. nature-archify requires Node >= 18.")

    @staticmethod
    def _abs(p: str | Path) -> str:
        """Resolve a spec/output path against the caller's working directory.

        The CLI itself runs with cwd set to the skill root, so a relative path
        handed straight to it would be re-anchored there. A caller writing
        ``cli.validate("architecture", "spec.json")`` means its own cwd.
        """
        path = Path(p)
        return str(path if path.is_absolute() else (Path.cwd() / path).resolve())

    def _run(self, args: Iterable[str], json_output: bool = True, timeout: float = 180.0) -> CliResult:
        cmd = [self.node_bin, str(self.cli), *args]
        if json_output and "--json" not in args:
            cmd.append("--json")
        proc = subprocess.run(cmd, cwd=str(self.skill_root), capture_output=True, text=True, timeout=timeout)
        payload: Any = None
        out = proc.stdout.strip()
        if out:
            try:
                payload = json.loads(out)
            except json.JSONDecodeError:
                payload = None
        return CliResult(ok=proc.returncode == 0, exit_code=proc.returncode, payload=payload, stdout=proc.stdout, stderr=proc.stderr)

    def doctor(self) -> CliResult:
        return self._run(["doctor"], json_output=False)

    def guide(self, scenario: str) -> CliResult:
        return self._run(["guide", scenario])

    def validate(self, diagram_type: str, spec_path: str | Path, *, quality: str = "standard") -> CliResult:
        if diagram_type not in self.DIAGRAM_TYPES:
            raise ValueError(f"unsupported diagram_type: {diagram_type}")
        if quality not in self.QUALITY_PROFILES:
            raise ValueError(f"unsupported quality profile: {quality}")
        return self._run(["validate", diagram_type, self._abs(spec_path), "--quality", quality])

    def deliver(self, diagram_type: str, spec_path: str | Path, out_html: str | Path, *, quality: str = "showcase", open_after: bool = False) -> CliResult:
        if diagram_type not in self.DIAGRAM_TYPES:
            raise ValueError(f"unsupported diagram_type: {diagram_type}")
        if quality not in self.QUALITY_PROFILES:
            raise ValueError(f"unsupported quality profile: {quality}")
        args = ["deliver", diagram_type, self._abs(spec_path), self._abs(out_html), "--quality", quality]
        if open_after:
            args.append("--open")
        return self._run(args)

    def visual_check(self, html_path: str | Path) -> CliResult:
        return self._run(["visual-check", self._abs(html_path)])

    def inspect(self, diagram_type: str, spec_path: str | Path) -> CliResult:
        return self._run(["inspect", diagram_type, self._abs(spec_path)])

    def check(self, html_path: str | Path) -> CliResult:
        return self._run(["check", self._abs(html_path)])

    def compare(self, base_path: str | Path, head_path: str | Path, out_html: Optional[str | Path] = None, *, receipt: Optional[str | Path] = None) -> CliResult:
        args = ["compare", "architecture", self._abs(base_path), self._abs(head_path)]
        if out_html is not None:
            args.append(self._abs(out_html))
        if receipt is not None:
            args += ["--receipt", self._abs(receipt)]
        return self._run(args)


__all__ = ["NatureArchitecture", "CliResult"]


if __name__ == "__main__":
    import sys
    cli = NatureArchitecture()
    if len(sys.argv) < 2 or sys.argv[1] == "doctor":
        result = cli.doctor()
        sys.stdout.write(result.stdout)
        sys.exit(0 if result.ok else 1)
    sys.stdout.write("Usage: python nature_archify_bridge.py doctor\n")
    sys.exit(2)
