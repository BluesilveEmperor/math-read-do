#!/usr/bin/env python
"""
nature-framework Python bridge.

Thin Python wrapper over the nature-framework Node CLI
(nature-framework/bin/nature-framework.mjs).

Used by math-read-do scripts that need to render architecture / framework /
route / system / structure / experiment figures without writing shell glue.

Typical use:

    from nature_framework_bridge import NatureArchitecture
    cli = NatureArchitecture()             # auto-locate the skill root
    cli.doctor()                           # returns parsed status dict
    cli.validate("model", "spec.json", quality="showcase")
    cli.deliver("model", "spec.json", "out.html", quality="showcase", motion="off")

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
    Path(__file__).resolve().parent.parent / "nature-framework",
    Path(__file__).resolve().parent.parent.parent / "paperfig" / "paperfig",
    Path(__file__).resolve().parent / "_skill_dir",
)


def _locate_skill_root() -> Path:
    for candidate in _SKILL_DIR_CANDIDATES:
        if (candidate / "bin" / "nature-framework.mjs").is_file():
            return candidate
    env = Path(__file__).resolve().parent / "_skill_dir"
    if env.is_dir() and (env / "bin" / "nature-framework.mjs").is_file():
        return env
    raise FileNotFoundError(
        "Cannot locate nature-framework skill root. "
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
        "model", "framework", "route", "system", "structure", "experiment",
    )
    QUALITY_PROFILES: tuple[str, ...] = ("standard", "showcase")
    MOTION_MODES: tuple[str, ...] = ("off", "hover", "flow", "tour")

    def __init__(self, skill_root: Optional[Path] = None, node_bin: Optional[str] = None) -> None:
        self.skill_root = Path(skill_root) if skill_root else _locate_skill_root()
        self.cli = self.skill_root / "bin" / "nature-framework.mjs"
        if not self.cli.is_file():
            raise FileNotFoundError(f"CLI not found: {self.cli}")
        self.node_bin = node_bin or shutil.which("node")
        if not self.node_bin:
            raise FileNotFoundError("node executable not found on PATH. nature-framework requires Node >= 18.")

    def _run(self, args: Iterable[str], json_output: bool = True, timeout: float = 120.0) -> CliResult:
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
        return self._run(["validate", diagram_type, str(spec_path), "--quality", quality])

    def deliver(self, diagram_type: str, spec_path: str | Path, out_html: str | Path, *, quality: str = "showcase", motion: Optional[str] = None, pdf: Optional[str | Path] = None, open_after: bool = False) -> CliResult:
        if diagram_type not in self.DIAGRAM_TYPES:
            raise ValueError(f"unsupported diagram_type: {diagram_type}")
        if quality not in self.QUALITY_PROFILES:
            raise ValueError(f"unsupported quality profile: {quality}")
        if motion is not None and motion not in self.MOTION_MODES:
            raise ValueError(f"unsupported motion mode: {motion}")
        args = ["deliver", diagram_type, str(spec_path), str(out_html), "--quality", quality]
        if motion is not None:
            args += ["--motion", motion]
        if pdf is not None:
            args += ["--pdf", str(pdf)]
        if open_after:
            args.append("--open")
        return self._run(args)

    def demo(self, output_dir: str | Path = "./nature-framework-demo", *, motion: Optional[str] = None) -> CliResult:
        args = ["demo", str(output_dir)]
        if motion is not None:
            args += ["--motion", motion]
        return self._run(args, json_output=False)


__all__ = ["NatureArchitecture", "CliResult"]


if __name__ == "__main__":
    import sys
    cli = NatureArchitecture()
    if len(sys.argv) < 2 or sys.argv[1] == "doctor":
        result = cli.doctor()
        sys.stdout.write(result.stdout)
        sys.exit(0 if result.ok else 1)
    sys.stdout.write("Usage: python nature_framework_bridge.py doctor\n")
    sys.exit(2)