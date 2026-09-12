#!/usr/bin/env python
"""Rename nature-architecture -> nature-framework in current branch."""
import pathlib

OLD_DIR = pathlib.Path("nature-architecture")
NEW_DIR = pathlib.Path("nature-framework")
OLD_CLI = NEW_DIR / "bin" / "nature-architecture.mjs"
NEW_CLI = NEW_DIR / "bin" / "nature-framework.mjs"
OLD_BRIDGE = pathlib.Path("scripts/nature_architecture_bridge.py")
NEW_BRIDGE = pathlib.Path("scripts/nature_framework_bridge.py")

if OLD_DIR.exists():
    OLD_DIR.rename(NEW_DIR); print("1. Renamed dir")
elif NEW_DIR.exists():
    print("1. Dir already renamed")
else:
    print("1. ERROR"); raise SystemExit(1)

if OLD_CLI.exists():
    OLD_CLI.rename(NEW_CLI); print("2. Renamed CLI")
if OLD_BRIDGE.exists():
    OLD_BRIDGE.rename(NEW_BRIDGE); print("3. Renamed bridge")

exts = {'.mjs', '.md', '.json', '.html', '.py'}
count = 0
for f in NEW_DIR.rglob('*'):
    if f.is_file() and f.suffix in exts:
        text = f.read_text(encoding='utf-8')
        if 'nature-architecture' in text:
            f.write_text(text.replace('nature-architecture', 'nature-framework'), encoding='utf-8')
            count += 1
print(f"4. Replaced in {count} files")

if NEW_BRIDGE.exists():
    text = NEW_BRIDGE.read_text(encoding='utf-8')
    text = text.replace('nature-architecture', 'nature-framework').replace('nature_architecture', 'nature_framework')
    NEW_BRIDGE.write_text(text, encoding='utf-8')
    print("5. Updated bridge.py")

for fpath in ["SKILL.md", "README.md", "skills/registry.yaml", "nature-figure/SKILL.md", "nature-paper2ppt/references/figure-assets.md"]:
    p = pathlib.Path(fpath)
    if not p.exists(): continue
    text = p.read_text(encoding='utf-8')
    if 'nature-architecture' in text:
        p.write_text(text.replace('nature-architecture', 'nature-framework'), encoding='utf-8')
        print(f"6. Updated {fpath}")

print("Done.")