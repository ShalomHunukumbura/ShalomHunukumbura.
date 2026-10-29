"""Regenerate the "Developer tools" section of README.md from the tools site's tools.json.

Only the text between the tools:start and tools:end markers changes. Download counts
and stars are left out on purpose, so the README only changes when a tool does.

    python .github/scripts/update_tools.py [path-or-url-to-tools.json]
"""

from __future__ import annotations

import json
import re
import sys
import urllib.request
from pathlib import Path

SOURCE = "https://shalomhunukumbura.github.io/tools/tools.json"
README = Path(__file__).resolve().parents[2] / "README.md"
MARKERS = re.compile(r"(<!-- tools:start -->\n).*?(<!-- tools:end -->)", re.DOTALL)


def load(source: str) -> dict:
    if source.startswith("http"):
        with urllib.request.urlopen(source, timeout=30) as response:
            return json.load(response)
    return json.loads(Path(source).read_text())


def render(data: dict) -> str:
    lines = [
        f"Open-source tools that catch what code review misses. **[All of them, with real output]({data['site']})**",
        "",
        "| Tool | What it does | Install |",
        "| --- | --- | --- |",
    ]
    for tool in data["tools"]:
        name = f"[**{tool['name']}**]({tool['repo']})" if tool.get("repo") else f"**{tool['name']}**"
        lines.append(f"| {name}<br><sub>{tool['kind']}</sub> | {tool['tagline']} | `{tool['install']}` |")
    upcoming = data.get("upcoming") or []
    if upcoming:
        names = [
            f"{t['name']} (built, release pending)" if t["status"] == "building" else t["name"]
            for t in upcoming
        ]
        lines += ["", f"Next up: {', '.join(names)}."]
    return "\n".join(lines) + "\n"


def main() -> None:
    data = load(sys.argv[1] if len(sys.argv) > 1 else SOURCE)
    readme = README.read_text()
    if not MARKERS.search(readme):
        sys.exit("README.md has no <!-- tools:start --> / <!-- tools:end --> markers")
    updated = MARKERS.sub(lambda m: m.group(1) + render(data) + m.group(2), readme)
    if updated != readme:
        README.write_text(updated)
        print("README.md updated")
    else:
        print("README.md already up to date")


if __name__ == "__main__":
    main()
