#!/usr/bin/env python3
"""Validate that generated spec/plan/test documents satisfy the traceability contract.

Part of the github-spec-planner skill. The validator enforces the
rules described in references/traceability_spec.md:

  - required deliverables exist
  - every REQ cites at least one SRC/OBS
  - every DEC cites at least one SRC/OBS and lists alternatives
  - every MOD maps to at least one REQ
  - every TASK maps to at least one MOD or REQ
  - every TEST maps to at least one REQ
  - no referenced ID is undefined, no forbidden placeholder remains
  - every SRC in sources.md has a URL and retrieval timestamp

Usage:
  python3 validate_docs.py --docs-dir docs [--report docs/validation_report.md]
                           [--check-links] [--strict]

Exit codes: 0 all checks passed, 1 at least one hard failure, 2 bad arguments.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import urllib.error
import urllib.request
from pathlib import Path

ID_RE = re.compile(r"\b(?:SRC|OBS|REQ|MOD|TASK|DEC|TEST)-[A-Za-z0-9-]+\b")
PLACEHOLDERS = re.compile(
    r"\b(?:TODO|TBD|FIXME|XXX)\b|待补充|待定|占位|\{\{[^}\n]+\}\}", re.IGNORECASE
)

REQUIRED = [
    "00-research/github_top5.json",
    "00-research/github_top5.md",
    "00-research/analysis.md",
    "01-spec/spec.md",
    "01-spec/sources.md",
    "02-plan/plan.md",
    "02-plan/decisions.md",
    "03-tests/test_suite.md",
    "03-tests/test_cases.csv",
]


class Check:
    def __init__(self) -> None:
        self.results: list[tuple[str, bool, str]] = []

    def add(self, name: str, ok: bool, detail: str = "") -> None:
        self.results.append((name, bool(ok), detail))

    @property
    def failed(self) -> int:
        return sum(1 for _, ok, _ in self.results if not ok)

    def report(self) -> str:
        lines = ["# 文档溯源一致性校验报告", "",
                 f"- 检查项总数：{len(self.results)}",
                 f"- 通过：{len(self.results) - self.failed}",
                 f"- 失败：{self.failed}", "",
                 "| 检查项 | 结果 | 说明 |", "| --- | --- | --- |"]
        for name, ok, detail in self.results:
            lines.append(f"| {name} | {'PASS' if ok else 'FAIL'} | {detail} |")
        lines.append("")
        return "\n".join(lines)


def read(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return ""


def definitions_and_blocks(text: str) -> dict[str, str]:
    """Map each defined ID to the text block that follows its definition."""
    lines = text.splitlines()
    found: list[tuple[int, str]] = []
    def_pattern = re.compile(
        r"^\s*(?:\|\s*|[-*]\s*|#{1,6}\s*)?(?:\*\*)?"
        r"((?:SRC|OBS|REQ|MOD|TASK|DEC|TEST)-[A-Za-z0-9-]+)(?:\*\*)?(?:\s*\||\s*[:：]|\s|$)"
    )
    for idx, line in enumerate(lines):
        match = def_pattern.match(line)
        if match:
            found.append((idx, match.group(1)))

    blocks: dict[str, str] = {}
    for pos, (line_idx, ident) in enumerate(found):
        end = found[pos + 1][0] if pos + 1 < len(found) else len(lines)
        # Also stop at the next top-level heading, unless it is the definition itself.
        chunk: list[str] = []
        for line in lines[line_idx:end]:
            if chunk and re.match(r"^#{1,2}\s", line):
                break
            chunk.append(line)
        blocks.setdefault(ident, "")
        blocks[ident] += "\n".join(chunk) + "\n"
    return blocks


def check_link(url: str) -> tuple[bool, str]:
    if not url.startswith(("http://", "https://")):
        return False, "not an http(s) URL"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "evidence-validator/1.0"},
                                     method="HEAD")
        with urllib.request.urlopen(req, timeout=8) as resp:
            return resp.status < 400, f"HTTP {resp.status}"
    except urllib.error.HTTPError as exc:
        # Some hosts reject HEAD; a GET is a reasonable fallback.
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "evidence-validator/1.0"})
            with urllib.request.urlopen(req, timeout=8) as resp:
                return resp.status < 400, f"HTTP {resp.status} (GET fallback)"
        except Exception as exc2:
            return False, f"HTTP {exc.code} / GET {type(exc2).__name__}"
    except Exception as exc:
        return False, f"{type(exc).__name__}: {exc}"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--docs-dir", required=True, help="Directory containing generated docs.")
    parser.add_argument("--report", default="", help="Path to write Markdown report.")
    parser.add_argument("--check-links", action="store_true",
                        help="Liveness-check source URLs (network required).")
    parser.add_argument("--strict", action="store_true",
                        help="Treat link failures and undefined-reference warnings as hard failures.")
    args = parser.parse_args()

    docs = Path(args.docs_dir).expanduser()
    if not docs.is_dir():
        print(f"ERROR: docs directory not found: {docs}", file=sys.stderr)
        return 2

    check = Check()

    texts: dict[str, str] = {}
    for rel in REQUIRED:
        path = docs / rel
        exists = path.is_file() and path.stat().st_size > 0
        check.add(f"文件存在: {rel}", exists,
                  "" if exists else "缺失或为空文件")
        texts[rel] = read(path) if exists else ""

    all_text = "\n".join(texts.values())
    all_ids = set(ID_RE.findall(all_text))

    # Source registry from JSON.
    registry_ids: set[str] = set()
    json_path = docs / "00-research/github_top5.json"
    if json_path.is_file():
        try:
            payload = json.loads(json_path.read_text(encoding="utf-8"))
            registry_ids = {s["id"] for s in payload.get("source_registry", []) if s.get("id")}
            check.add("JSON 证据台账包含来源", bool(registry_ids),
                      f"共 {len(registry_ids)} 个 SRC")
            check.add("JSON schema_version 存在", bool(payload.get("schema_version")),
                      str(payload.get("schema_version")))
            check.add("JSON 含复现命令", bool(payload.get("reproduce_command")), "")
        except (json.JSONDecodeError, OSError) as exc:
            check.add("JSON 可解析", False, str(exc))

    blocks: dict[str, str] = {}
    for rel, text in texts.items():
        for ident, block in definitions_and_blocks(text).items():
            blocks.setdefault(ident, "")
            blocks[ident] += block

    defined = set(blocks)
    # IDs that only appear in the source registry JSON are still defined.
    defined |= registry_ids

    spec_blocks = definitions_and_blocks(texts.get("01-spec/spec.md", ""))
    plan_blocks = definitions_and_blocks(texts.get("02-plan/plan.md", ""))
    dec_blocks = definitions_and_blocks(texts.get("02-plan/decisions.md", ""))
    test_md_blocks = definitions_and_blocks(texts.get("03-tests/test_suite.md", ""))
    test_csv_text = texts.get("03-tests/test_cases.csv", "")
    sources_text = texts.get("01-spec/sources.md", "")

    # CSV TEST IDs: first column, e.g. TEST-FUNC-001.
    csv_test_ids = set()
    for line in test_csv_text.splitlines():
        match = re.match(r'^\s*"?((?:TEST)-[A-Za-z0-9-]+)"?\s*,', line)
        if match:
            csv_test_ids.add(match.group(1))
    test_blocks = dict(test_md_blocks)
    for tid in csv_test_ids:
        test_blocks.setdefault(tid, "")
        # CSV row is the evidence block.
        for line in test_csv_text.splitlines():
            if line.startswith(tid):
                test_blocks[tid] += line + "\n"

    check.add("spec.md 含需求定义", bool(spec_blocks), f"REQ 类 {sum(1 for i in spec_blocks if i.startswith('REQ-'))} 个")
    check.add("plan.md 含任务定义", bool(plan_blocks), f"任务类 {sum(1 for i in plan_blocks if i.startswith('TASK-'))} 个")
    check.add("测试集含用例定义", bool(test_blocks), f"用例 {len(test_blocks)} 个")

    for ident, block in spec_blocks.items():
        if ident.startswith("REQ-"):
            cites = [c for c in ID_RE.findall(block) if c.startswith(("SRC-", "OBS-"))]
            check.add(f"{ident} 有来源引用", bool(cites), ", ".join(sorted(set(cites))))

    for ident, block in dec_blocks.items():
        if not ident.startswith("DEC-"):
            continue
        cites = [c for c in ID_RE.findall(block) if c.startswith(("SRC-", "OBS-"))]
        check.add(f"{ident} 有来源引用", bool(cites), ", ".join(sorted(set(cites))))
        has_alt = bool(re.search(r"备选|替代|alternatives|comparison|对比", block, re.IGNORECASE))
        check.add(f"{ident} 含备选方案", has_alt, "")

    for ident, block in blocks.items():
        if ident.startswith("MOD-"):
            cites = [c for c in ID_RE.findall(block) if c.startswith("REQ-")]
            check.add(f"{ident} 追溯到需求", bool(cites), ", ".join(sorted(set(cites))))

    for ident, block in plan_blocks.items():
        if ident.startswith("TASK-"):
            cites = [c for c in ID_RE.findall(block) if c.startswith(("MOD-", "REQ-"))]
            check.add(f"{ident} 追溯到板块/需求", bool(cites), ", ".join(sorted(set(cites))))

    for ident, block in test_blocks.items():
        if ident.startswith("TEST-"):
            cites = [c for c in ID_RE.findall(block) if c.startswith("REQ-")]
            check.add(f"{ident} 追溯到需求", bool(cites), ", ".join(sorted(set(cites))))

    undefined = sorted(all_ids - defined)
    check.add("无悬空 ID 引用", not undefined,
              "未定义: " + ", ".join(undefined[:12]) if undefined else "")

    # Placeholders.
    offenders = []
    for rel, text in texts.items():
        for match in PLACEHOLDERS.finditer(text):
            line_no = text[:match.start()].count("\n") + 1
            offenders.append(f"{rel}:{line_no}")
    check.add("无 TODO/TBD 等占位符", not offenders,
              ", ".join(offenders[:12]) if offenders else "")

    # Source registry table quality.
    src_rows = [line for line in sources_text.splitlines()
                if re.match(r"^\s*\|\s*SRC-", line)]
    bad_src = []
    for row in src_rows:
        if not re.search(r"https?://", row):
            bad_src.append(row[:60])
        if not re.search(r"20\d{2}-\d{2}-\d{2}", row):
            bad_src.append(row[:60] + " (缺抓取时间)")
    check.add("sources.md 每条来源含 URL 与抓取时间", not bad_src,
              "; ".join(bad_src[:5]) if bad_src else f"{len(src_rows)} 条来源")

    # Optional URL liveness checks, capped for politeness.
    if args.check_links:
        urls = []
        for line in src_rows:
            match = re.search(r"(https?://[^\s|)]+)", line)
            if match and match.group(1) not in urls:
                urls.append(match.group(1))
        for url in urls[:20]:
            ok, detail = check_link(url)
            check.add(f"链接可达: {url[:70]}", ok, detail)
            if not ok and not args.strict:
                # Keep as a reported failure but do not abort more than necessary.
                pass

    report = check.report()
    if args.report:
        report_path = Path(args.report).expanduser()
        report_path.parent.mkdir(parents=True, exist_ok=True)
        report_path.write_text(report, encoding="utf-8")
        print(f"Wrote validation report: {report_path}")
    print(report)
    return 1 if check.failed else 0


if __name__ == "__main__":
    sys.exit(main())
