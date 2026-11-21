#!/usr/bin/env python3
"""Find and profile the top GitHub open-source repositories matching a project idea.

Part of the github-spec-planner skill. Every emitted fact carries a
source id, source URL and retrieval timestamp, so downstream spec.md / plan.md /
test documents can cite verifiable evidence instead of unverifiable claims.

Ranking rule (documented in the output and reproducible):
  1. Repositories CREATED within the last --months months (default 6).
  2. Merged across one search per keyword, deduplicated by full_name.
  3. Sorted by stargazers_count DESC, then keyword-coverage DESC, then pushed_at DESC.
  4. Top --top repositories are profiled in detail.

Use --window-basis pushed to interpret "within the window" as "actively pushed
within the window" instead of "created within the window".

Authentication:
  export GITHUB_TOKEN=ghp_...   (optional, raises rate limit from 10 to 30/min
                                for search and 60 to 5000/hour for core API)
  Never pass the token with --token on a shared shell; prefer the env var.

Usage:
  python3 github_top5.py --keywords "task,manager,todo" \
      --topics productivity --months 6 --top 5 \
      --output docs/00-research/github_top5.json \
      --report docs/00-research/github_top5.md

Exit codes: 0 success, 1 configuration error, 2 upstream/API failure with no usable data.
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

SCHEMA_VERSION = "1.0"
API_ROOT = "https://api.github.com"
UA = "github-spec-planner/1.0 (reproducible research)"


def utcnow() -> str:
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat()


class FetchError(RuntimeError):
    pass


def http_get(url: str, token: str | None, *, accept: str, timeout: int = 20,
             retries: int = 2) -> tuple[bytes, dict]:
    """GET a URL with rate-limit-aware retries. Returns (body, headers)."""
    headers = {
        "User-Agent": UA,
        "Accept": accept,
        "X-GitHub-Api-Version": "2022-11-28",
    }
    if token and url.startswith(API_ROOT):
        headers["Authorization"] = f"Bearer {token}"

    last_error = None
    for attempt in range(retries + 1):
        req = urllib.request.Request(url, headers=headers)
        try:
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                return resp.read(), dict(resp.headers)
        except urllib.error.HTTPError as exc:
            body = exc.read().decode("utf-8", errors="replace")[:300]
            if exc.code in (403, 429) and attempt < retries:
                reset = exc.headers.get("X-RateLimit-Reset")
                retry_after = exc.headers.get("Retry-After")
                wait = 0
                if retry_after and retry_after.isdigit():
                    wait = int(retry_after)
                elif reset and reset.isdigit():
                    wait = max(0, int(reset) - int(time.time())) + 2
                else:
                    wait = 5
                if wait > 60:
                    raise FetchError(
                        f"Rate limit exhausted for {url}. Reset in {wait}s. "
                        "Set GITHUB_TOKEN or retry later."
                    )
                time.sleep(min(wait, 60))
                last_error = f"HTTP {exc.code}: {body}"
                continue
            raise FetchError(f"HTTP {exc.code} for {url}: {body}")
        except (urllib.error.URLError, TimeoutError) as exc:
            last_error = f"{type(exc).__name__}: {exc}"
            if attempt < retries:
                time.sleep(2 ** attempt)
                continue
    raise FetchError(f"Failed to fetch {url}: {last_error}")


def api_get(path: str, token: str | None) -> tuple[object, dict]:
    url = f"{API_ROOT}{path}"
    body, headers = http_get(url, token, accept="application/vnd.github+json")
    return json.loads(body.decode("utf-8")), headers


def safe_text(value: object, limit: int = 12000) -> str:
    if not isinstance(value, str):
        return ""
    text = re.sub(r"\s+\n", "\n", value).strip()
    return text[:limit]


def compute_since(months: int, basis: str) -> str:
    # Use calendar months approximation: months * 30 days, documented in output.
    days = months * 30
    return (dt.date.today() - dt.timedelta(days=days)).isoformat()


def build_query(keyword: str, since: str, basis: str, topics: list[str],
                min_stars: int) -> str:
    parts = [f'"{keyword}"' if " " in keyword else keyword]
    parts.append(f"{basis}:>={since}")
    parts.append("archived:false")
    parts.append("fork:false")
    if min_stars > 0:
        parts.append(f"stars:>={min_stars}")
    for topic in topics:
        parts.append(f"topic:{topic}")
    return " ".join(parts)


def search_repos(query: str, token: str | None, per_page: int) -> tuple[list[dict], dict]:
    params = urllib.parse.urlencode({
        "q": query,
        "sort": "stars",
        "order": "desc",
        "per_page": per_page,
        "page": 1,
    })
    url = f"{API_ROOT}/search/repositories?{params}"
    data, headers = api_get(f"/search/repositories?{params}", token)
    meta = {
        "query": query,
        "url": url,
        "retrieved_at": utcnow(),
        "total_count": data.get("total_count") if isinstance(data, dict) else None,
        "rate_limit_remaining": headers.get("X-RateLimit-Remaining"),
    }
    items = data.get("items", []) if isinstance(data, dict) else []
    return items if isinstance(items, list) else [], meta


def keyword_coverage(keywords: list[str], texts: list[str]) -> dict:
    blob = " ".join(t for t in texts if t).lower()
    matched = [kw for kw in keywords if kw.lower() in blob]
    score = round(len(matched) / len(keywords), 4) if keywords else 0.0
    return {"score": score, "matched_keywords": matched,
            "total_keywords": len(keywords)}


def fetch_readme(full_name: str, default_branch: str, token: str | None) -> tuple[str, str | None]:
    names = ["README.md", "readme.md", "README.rst", "README.txt", "README"]
    for name in names:
        url = (f"https://raw.githubusercontent.com/{full_name}/"
               f"{urllib.parse.quote(default_branch)}/{name}")
        try:
            body, _ = http_get(url, token, accept="text/plain", timeout=15, retries=1)
            return safe_text(body.decode("utf-8", errors="replace")), url
        except FetchError:
            continue
    return "", None


def profile_repo(item: dict, keywords: list[str], token: str | None,
                 registry: list[dict]) -> dict:
    full_name = item.get("full_name")
    if not full_name:
        return {}
    src_api = f"{API_ROOT}/repos/{full_name}"
    src_html = item.get("html_url") or f"https://github.com/{full_name}"

    def add_source(prefix: str, url: str, tier: str, used_for: str) -> str:
        sid = f"{prefix}-{len(registry) + 1:03d}"
        registry.append({
            "id": sid,
            "tier": tier,
            "url": url,
            "retrieved_at": utcnow(),
            "used_for": used_for,
        })
        return sid

    sid_api = add_source("SRC", src_api, "A-GitHub-API",
                         f"canonical metadata for {full_name}")
    sid_html = add_source("SRC", src_html, "A-GitHub-Web",
                          f"human-verifiable repository page for {full_name}")

    detail = {}
    warnings: list[str] = []
    try:
        detail, _ = api_get(f"/repos/{full_name}", token)
    except FetchError as exc:
        warnings.append(f"detail fetch failed for {full_name}: {exc}")
        detail = dict(item)

    languages: dict = {}
    try:
        languages, _ = api_get(f"/repos/{full_name}/languages", token)
    except FetchError as exc:
        warnings.append(f"languages fetch failed for {full_name}: {exc}")

    contributors = None
    try:
        _, link_headers = api_get(
            f"/repos/{full_name}/contributors?per_page=1&anon=true", token)
        link = link_headers.get("Link", "")
        match = re.search(r'[?&]page=(\d+)>;\s*rel="last"', link)
        if match:
            contributors = int(match.group(1))
    except FetchError as exc:
        warnings.append(f"contributors fetch failed for {full_name}: {exc}")

    default_branch = detail.get("default_branch") or "main"
    readme, readme_url = fetch_readme(full_name, default_branch, token)
    sid_readme = None
    if readme_url:
        sid_readme = add_source("SRC", readme_url, "B-Repository-File",
                                f"README evidence for {full_name}")

    license_info = detail.get("license") or {}
    license_name = license_info.get("spdx_id") if isinstance(license_info, dict) else None

    coverage = keyword_coverage(
        keywords,
        [str(detail.get("name") or ""), str(detail.get("description") or ""),
         " ".join(detail.get("topics") or []), readme[:8000]],
    )

    return {
        "full_name": full_name,
        "html_url": src_html,
        "api_url": src_api,
        "description": safe_text(detail.get("description"), 500),
        "homepage": detail.get("homepage") or None,
        "topics": detail.get("topics") or [],
        "stars": detail.get("stargazers_count"),
        "forks": detail.get("forks_count"),
        "watchers": detail.get("subscribers_count"),
        "open_issues": detail.get("open_issues_count"),
        "contributors": contributors,
        "primary_language": detail.get("language"),
        "languages_bytes": languages if isinstance(languages, dict) else {},
        "license": license_name,
        "created_at": detail.get("created_at"),
        "updated_at": detail.get("updated_at"),
        "pushed_at": detail.get("pushed_at"),
        "default_branch": default_branch,
        "archived": bool(detail.get("archived")),
        "similarity": coverage,
        "readme_excerpt": readme[:2500],
        "source_ids": [sid for sid in (sid_api, sid_html, sid_readme) if sid],
        "evidence_map": {
            "stars": sid_api,
            "forks": sid_api,
            "open_issues": sid_api,
            "topics": sid_api,
            "license": sid_api,
            "created_at": sid_api,
            "pushed_at": sid_api,
            "languages_bytes": sid_api,
            "contributors": sid_api,
            "description": sid_api,
            "readme_excerpt": sid_readme or sid_html,
        },
        "warnings": warnings,
    }


def render_report(payload: dict) -> str:
    p = payload["parameters"]
    m = payload["methodology"]
    lines = [
        "# GitHub 开源项目调研报告（Top 5）",
        "",
        "> 本报告由 `scripts/github_top5.py` 自动生成。所有数据均附来源 ID 与抓取时间，",
        "> 来源台账见同目录 JSON 的 `source_registry` 字段。禁止手工编造未出现在下述来源中的数据。",
        "",
        "## 1. 调研参数",
        "",
        f"- 关键词：{', '.join(p['keywords'])}",
        f"- Topic 过滤：{', '.join(p['topics']) or '（无）'}",
        f"- 时间窗口：{p['months']} 个月（自 {p['since']} 起，按 {p['window_basis']} 判定）",
        f"- 排序与截取：stars 降序 → 关键词覆盖率降序 → 最近 push 降序，取前 {p['top']} 名",
        f"- 生成时间：{payload['generated_at']}",
        f"- 认证状态：{payload['auth_status']}",
        "",
        "## 2. 方法说明",
        "",
        f"- 窗口近似：{m['window_approximation']}",
        f"- 关键词覆盖评分：{m['similarity_formula']}",
        "- 证据分级：A = GitHub API / 官方页面；B = 仓库内原始文件（README 等）；C = 搜索结果片段（仅作线索，不作结论依据）。",
        f"- 局限：{m['limitations']}",
        "",
        "## 3. Top 5 项目",
        "",
        "| 排名 | 项目 | Stars | Forks | 语言 | License | 创建时间 | 最近 push | 关键词覆盖 | 来源 |",
        "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |",
    ]
    for repo in payload["repos"]:
        lines.append(
            f"| {repo['rank']} | [{repo['full_name']}]({repo['html_url']}) | "
            f"{repo.get('stars')} | {repo.get('forks')} | {repo.get('primary_language') or '-'} | "
            f"{repo.get('license') or '-'} | {str(repo.get('created_at'))[:10]} | "
            f"{str(repo.get('pushed_at'))[:10]} | {repo['similarity']['score']} | "
            f"{', '.join(repo['source_ids'])} |"
        )

    lines += ["", "## 4. 逐项目分析素材", ""]
    for repo in payload["repos"]:
        lines += [
            f"### {repo['rank']}. {repo['full_name']}",
            "",
            f"- 描述：{repo.get('description') or '（无描述）'}",
            f"- Topics：{', '.join(repo.get('topics') or []) or '（无）'}",
            f"- 语言构成（字节）：{json.dumps(repo.get('languages_bytes') or {}, ensure_ascii=False)}",
            f"- 贡献者数：{repo.get('contributors') if repo.get('contributors') is not None else '未获取'}",
            f"- Open issues：{repo.get('open_issues')}",
            f"- 命中关键词：{', '.join(repo['similarity']['matched_keywords']) or '（无）'}",
            f"- 来源 ID：{', '.join(repo['source_ids'])}",
            "",
            "README 摘录（用于人工/代理分析，引用时请回溯来源 ID）：",
            "",
            "```text",
            repo.get("readme_excerpt") or "（未获取到 README）",
            "```",
            "",
        ]
        if repo.get("warnings"):
            lines.append("> 抓取告警：" + "；".join(repo["warnings"]))
            lines.append("")

    lines += [
        "## 5. 查询与来源台账",
        "",
        "| 来源 ID | 级别 | URL | 抓取时间 | 用途 |",
        "| --- | --- | --- | --- | --- |",
    ]
    for src in payload["source_registry"]:
        lines.append(
            f"| {src['id']} | {src['tier']} | {src['url']} | {src['retrieved_at']} | {src['used_for']} |"
        )
    lines += ["", "### 检索查询", ""]
    for q in payload["queries"]:
        lines.append(f"- `{q['query']}` — 结果数 {q['total_count']} — 剩余额度 {q['rate_limit_remaining']}")
    if payload.get("warnings"):
        lines += ["", "## 6. 全局告警", ""]
        for w in payload["warnings"]:
            lines.append(f"- {w}")
    lines += [
        "",
        "## 7. 复现命令",
        "",
        "```bash",
        payload["reproduce_command"],
        "```",
        "",
    ]
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--keywords", required=True,
                        help="Comma-separated keywords describing the target project.")
    parser.add_argument("--topics", default="", help="Comma-separated GitHub topics filter.")
    parser.add_argument("--months", type=int, default=6, help="Time window in months (default 6).")
    parser.add_argument("--window-basis", choices=["created", "pushed"], default="created",
                        help="created: built in window; pushed: active in window (default created).")
    parser.add_argument("--top", type=int, default=5, help="How many repos to profile (default 5).")
    parser.add_argument("--per-query", type=int, default=30, help="Search results per query (default 30).")
    parser.add_argument("--min-stars", type=int, default=0, help="Minimum stars filter (default 0).")
    parser.add_argument("--output", required=True, help="Path to write the JSON evidence file.")
    parser.add_argument("--report", default="", help="Optional path to write a Markdown report.")
    parser.add_argument("--token", default=None,
                        help="GitHub token; prefer GITHUB_TOKEN env var instead.")
    args = parser.parse_args()

    token = args.token or os.environ.get("GITHUB_TOKEN")
    keywords = [k.strip() for k in args.keywords.split(",") if k.strip()]
    topics = [t.strip() for t in args.topics.split(",") if t.strip()]
    if not keywords:
        print("ERROR: --keywords must contain at least one keyword.", file=sys.stderr)
        return 1
    if args.top < 1 or args.months < 1:
        print("ERROR: --top and --months must be >= 1.", file=sys.stderr)
        return 1

    since = compute_since(args.months, args.window_basis)
    registry: list[dict] = []
    queries_meta: list[dict] = []
    warnings: list[str] = []
    candidates: dict[str, dict] = {}

    for keyword in keywords:
        query = build_query(keyword, since, args.window_basis, topics, args.min_stars)
        try:
            items, meta = search_repos(query, token, args.per_query)
        except FetchError as exc:
            warnings.append(f"search failed for '{keyword}': {exc}")
            continue
        queries_meta.append(meta)
        for item in items:
            name = item.get("full_name")
            if name and name not in candidates:
                candidates[name] = item
        time.sleep(1)  # be polite with unauthenticated search rate limits

    if not candidates:
        print("ERROR: no search results obtained; refusing to fabricate data. "
              "Check network, keywords, --min-stars/--topics, or set GITHUB_TOKEN.",
              file=sys.stderr)
        for w in warnings:
            print(f"  warning: {w}", file=sys.stderr)
        return 2

    ranked = sorted(
        candidates.values(),
        key=lambda r: (-(r.get("stargazers_count") or 0),
                       -keyword_coverage(keywords, [str(r.get("description") or "")])["score"]),
    )
    selected = ranked[:max(args.top * 3, args.top)]
    repos: list[dict] = []
    for item in selected:
        if len(repos) >= args.top:
            break
        try:
            profiled = profile_repo(item, keywords, token, registry)
        except FetchError as exc:
            warnings.append(f"profiling failed for {item.get('full_name')}: {exc}")
            continue
        if profiled:
            repos.append(profiled)
        time.sleep(0.3)

    # Explicit ranking: stars DESC, coverage DESC, pushed_at DESC.
    repos.sort(key=lambda r: (r.get("stars") or 0,
                              r["similarity"]["score"],
                              str(r.get("pushed_at") or "")), reverse=True)
    repos = repos[:args.top]
    for idx, repo in enumerate(repos, start=1):
        repo["rank"] = idx

    reproduce = (
        f"python3 scripts/github_top5.py --keywords \"{','.join(keywords)}\" "
        + (f"--topics \"{','.join(topics)}\" " if topics else "")
        + f"--months {args.months} --window-basis {args.window_basis} "
        + f"--top {args.top} --min-stars {args.min_stars} "
        + f"--output {args.output}" + (f" --report {args.report}" if args.report else "")
    )

    payload = {
        "schema_version": SCHEMA_VERSION,
        "generated_at": utcnow(),
        "parameters": {
            "keywords": keywords,
            "topics": topics,
            "months": args.months,
            "window_basis": args.window_basis,
            "since": since,
            "top": args.top,
            "min_stars": args.min_stars,
        },
        "auth_status": "authenticated via GITHUB_TOKEN/--token" if token
                       else "unauthenticated (rate limits: search 10/min, core 60/hour)",
        "methodology": {
            "window_approximation": f"months * 30 days -> since={since}; basis={args.window_basis}",
            "ranking": "stars DESC, then keyword coverage DESC, then pushed_at DESC",
            "similarity_formula": "matched_keywords / total_keywords, case-insensitive substring "
                                  "match over name + description + topics + first 8000 chars of README",
            "evidence_tiers": {"A": "GitHub API / official web pages",
                               "B": "raw repository files (README)",
                               "C": "search snippets (leads only, never conclusions)"},
            "limitations": "Star counts are a snapshot, not star growth within the window; "
                           "keyword matching is lexical, not semantic; unauthenticated rate limits apply.",
        },
        "source_registry": registry,
        "queries": queries_meta,
        "repos": repos,
        "warnings": warnings,
        "reproduce_command": reproduce,
    }

    out_path = Path(args.output).expanduser()
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Wrote evidence JSON: {out_path}")

    if args.report:
        report_path = Path(args.report).expanduser()
        report_path.parent.mkdir(parents=True, exist_ok=True)
        report_path.write_text(render_report(payload), encoding="utf-8")
        print(f"Wrote Markdown report: {report_path}")

    if warnings:
        print(f"Completed with {len(warnings)} warning(s); see JSON 'warnings'.", file=sys.stderr)
    print(f"Repos profiled: {len(repos)} / requested {args.top}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
