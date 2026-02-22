#!/usr/bin/env python3
"""Authenticated resource enrichment for transcript session folders.

This script enriches session resources listed in:
  <session>/.pipeline/resource_manifest.json

Supported providers:
  - Notion: authenticated block extraction via unofficial API v3
  - Canva: authenticated browser capture via Playwright storage state
  - Generic HTTP fallback for any URL (HTML title/content snapshot)

It writes:
  - <session>/.resources/resource_enrichment_report.json
  - provider-specific extracted artifacts under <session>/.resources/
"""

from __future__ import annotations

import argparse
import json
import os
import re
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

import requests


DEFAULT_ROOT = Path("/Users/praxlannister/Documents/Zoom")


@dataclass
class ResourceItem:
    name: str
    url: str


@dataclass
class EnrichmentResult:
    name: str
    url: str
    provider: str
    method: str
    authenticated: bool
    status: str
    http_status: int | None
    final_url: str | None
    title: str | None
    output_files: list[str]
    notes: list[str]
    error: str | None


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def slug(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-") or "resource"


def detect_provider(url: str) -> str:
    host = urlparse(url).netloc.lower()
    if "notion.so" in host:
        return "notion"
    if "canva.com" in host:
        return "canva"
    if "drive.google.com" in host or "docs.google.com" in host:
        return "google-drive"
    return "generic"


def parse_manifest(session_dir: Path) -> list[ResourceItem]:
    manifest_path = session_dir / ".pipeline" / "resource_manifest.json"
    if not manifest_path.exists():
        return []
    data = json.loads(manifest_path.read_text(encoding="utf-8"))
    resources_raw = data.get("resources", [])
    items: list[ResourceItem] = []
    for row in resources_raw:
        if not isinstance(row, dict):
            continue
        name = str(row.get("name", "")).strip()
        url = str(row.get("url", "")).strip()
        if not name or not url:
            continue
        items.append(ResourceItem(name=name, url=url))
    return items


def load_cookies_into_session(session: requests.Session, cookies_json: Path) -> None:
    payload = json.loads(cookies_json.read_text(encoding="utf-8"))
    if isinstance(payload, dict):
        for k, v in payload.items():
            session.cookies.set(k, str(v))
        return
    if isinstance(payload, list):
        for row in payload:
            if not isinstance(row, dict):
                continue
            name = row.get("name")
            value = row.get("value")
            domain = row.get("domain")
            path = row.get("path", "/")
            if name and value:
                session.cookies.set(str(name), str(value), domain=domain, path=path)


def extract_html_title(text: str) -> str | None:
    m = re.search(r"<title[^>]*>(.*?)</title>", text, re.IGNORECASE | re.DOTALL)
    if not m:
        return None
    return " ".join(m.group(1).split())


def save_text(path: Path, text: str, dry_run: bool) -> None:
    if dry_run:
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", errors="ignore")


def save_bytes(path: Path, blob: bytes, dry_run: bool) -> None:
    if dry_run:
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(blob)


def to_rel(path: Path, session_dir: Path) -> str:
    return str(path.relative_to(session_dir))


def extract_drive_file_id(url: str) -> str | None:
    m = re.search(r"/d/([A-Za-z0-9_-]+)", url)
    if m:
        return m.group(1)
    m = re.search(r"[?&]id=([A-Za-z0-9_-]+)", url)
    if m:
        return m.group(1)
    return None


def parse_notion_page_id(url: str) -> str | None:
    parsed = urlparse(url)
    candidate = parsed.path.strip("/").split("/")[-1]
    candidate = candidate.split("?")[0]
    candidate = candidate.split("#")[0]

    m_hyphen = re.search(r"([0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12})", candidate)
    if m_hyphen:
        return m_hyphen.group(1).lower()
    m_flat = re.search(r"([0-9a-fA-F]{32})", candidate)
    if not m_flat:
        m_flat = re.search(r"([0-9a-fA-F]{32})", parsed.path)
    if m_flat:
        raw = m_flat.group(1).lower()
        return f"{raw[0:8]}-{raw[8:12]}-{raw[12:16]}-{raw[16:20]}-{raw[20:32]}"
    return None


def notion_load_page_chunks(
    page_id: str,
    token_v2: str,
    active_user: str,
    timeout: int = 45,
    max_calls: int = 30,
) -> tuple[list[dict[str, Any]], list[str]]:
    endpoint = "https://www.notion.so/api/v3/loadCachedPageChunk"
    headers = {
        "content-type": "application/json",
        "x-notion-active-user-header": active_user,
        "user-agent": "Mozilla/5.0",
    }
    cookies = {"token_v2": token_v2}
    cursor: dict[str, Any] = {"stack": []}
    chunks: list[dict[str, Any]] = []
    notes: list[str] = []

    for idx in range(max_calls):
        payload = {
            "page": {"id": page_id},
            "limit": 100,
            "cursor": cursor,
            "chunkNumber": idx,
            "verticalColumns": False,
        }
        resp = requests.post(endpoint, headers=headers, cookies=cookies, json=payload, timeout=timeout)
        resp.raise_for_status()
        data = resp.json()
        chunks.append(data)

        nxt = data.get("cursor")
        if not nxt or nxt == cursor:
            break
        cursor = nxt
    else:
        notes.append("Reached max_calls while paginating Notion chunks; output may be partial.")

    return chunks, notes


def notion_extract_markdown(chunks: list[dict[str, Any]], page_id: str) -> str:
    blocks: dict[str, dict[str, Any]] = {}
    for c in chunks:
        record_map = c.get("recordMap", {})
        bmap = record_map.get("block", {})
        for bid, payload in bmap.items():
            value = payload.get("value")
            if isinstance(value, dict):
                blocks[bid] = value

    def get_text(block: dict[str, Any]) -> str:
        props = block.get("properties", {})
        title = props.get("title")
        if not isinstance(title, list):
            return ""
        fragments: list[str] = []
        for seg in title:
            if isinstance(seg, list) and seg:
                fragments.append(str(seg[0]))
        return "".join(fragments).strip()

    lines: list[str] = []
    visited: set[str] = set()

    def visit(block_id: str, depth: int) -> None:
        if block_id in visited:
            return
        visited.add(block_id)
        block = blocks.get(block_id)
        if not block:
            return
        txt = get_text(block)
        btype = block.get("type", "text")

        if txt:
            if btype in {"header", "sub_header", "sub_sub_header"}:
                level = {"header": 1, "sub_header": 2, "sub_sub_header": 3}.get(btype, 2)
                lines.append(f"{'#' * level} {txt}")
            elif btype == "numbered_list":
                lines.append(("  " * max(depth - 1, 0)) + f"1. {txt}")
            elif btype == "bulleted_list":
                lines.append(("  " * max(depth - 1, 0)) + f"- {txt}")
            else:
                lines.append(("  " * max(depth - 1, 0)) + txt)

        for child in block.get("content", []) or []:
            visit(str(child), depth + 1)

    root_variants = [page_id, page_id.replace("-", "")]
    root = None
    for rid in root_variants:
        if rid in blocks:
            root = rid
            break

    if root is None and blocks:
        # Fallback: best-effort traversal from first known block.
        root = next(iter(blocks.keys()))

    if root is not None:
        visit(root, 0)

    out = "\n\n".join([ln for ln in lines if ln.strip()])
    return out.strip() + ("\n" if out else "")


def enrich_generic_http(
    session: requests.Session,
    item: ResourceItem,
    session_dir: Path,
    resources_dir: Path,
    dry_run: bool,
) -> EnrichmentResult:
    filename = f"{slug(item.name)}.html"
    out_path = resources_dir / filename
    try:
        resp = session.get(item.url, timeout=40, allow_redirects=True)
        title = extract_html_title(resp.text)
        save_text(out_path, resp.text, dry_run=dry_run)
        return EnrichmentResult(
            name=item.name,
            url=item.url,
            provider=detect_provider(item.url),
            method="generic-http-fetch",
            authenticated=False,
            status="ok",
            http_status=resp.status_code,
            final_url=str(resp.url),
            title=title,
            output_files=[to_rel(out_path, session_dir)],
            notes=[],
            error=None,
        )
    except Exception as exc:  # pragma: no cover - runtime/network dependent
        return EnrichmentResult(
            name=item.name,
            url=item.url,
            provider=detect_provider(item.url),
            method="generic-http-fetch",
            authenticated=False,
            status="error",
            http_status=None,
            final_url=None,
            title=None,
            output_files=[],
            notes=[],
            error=str(exc),
        )


def enrich_google_drive(
    session: requests.Session,
    item: ResourceItem,
    session_dir: Path,
    resources_dir: Path,
    dry_run: bool,
) -> EnrichmentResult:
    base = enrich_generic_http(session, item, session_dir, resources_dir, dry_run)
    file_id = extract_drive_file_id(item.url)
    if not file_id:
        return base

    try:
        dl_url = f"https://drive.google.com/uc?export=download&id={file_id}"
        resp = session.get(dl_url, timeout=60, allow_redirects=True)
        ctype = resp.headers.get("content-type", "").lower()
        if resp.status_code == 200 and ("pdf" in ctype or resp.content.startswith(b"%PDF")):
            pdf_path = resources_dir / f"{slug(item.name)}.pdf"
            save_bytes(pdf_path, resp.content, dry_run=dry_run)
            base.output_files.append(to_rel(pdf_path, session_dir))
            base.notes.append("Google Drive direct PDF export captured.")
        return base
    except Exception as exc:  # pragma: no cover - runtime/network dependent
        base.notes.append(f"Google Drive PDF export attempt failed: {exc}")
        return base


def enrich_notion(
    session: requests.Session,
    item: ResourceItem,
    session_dir: Path,
    resources_dir: Path,
    token_v2: str | None,
    active_user: str | None,
    dry_run: bool,
) -> EnrichmentResult:
    fallback = enrich_generic_http(session, item, session_dir, resources_dir, dry_run)
    fallback.provider = "notion"

    if not token_v2 or not active_user:
        fallback.notes.append("No NOTION_TOKEN_V2 / NOTION_ACTIVE_USER provided; using public HTML snapshot only.")
        return fallback

    page_id = parse_notion_page_id(item.url)
    if not page_id:
        fallback.notes.append("Could not parse Notion page ID from URL; using public HTML snapshot only.")
        return fallback

    try:
        chunks, notes = notion_load_page_chunks(page_id=page_id, token_v2=token_v2, active_user=active_user)
        md = notion_extract_markdown(chunks, page_id=page_id)
        md_path = resources_dir / f"{slug(item.name)}.notion.md"
        raw_path = resources_dir / f"{slug(item.name)}.notion.raw.json"

        save_text(md_path, md, dry_run=dry_run)
        save_text(raw_path, json.dumps(chunks, ensure_ascii=False, indent=2), dry_run=dry_run)

        fallback.method = "notion-api-v3-loadCachedPageChunk"
        fallback.authenticated = True
        fallback.output_files.extend([to_rel(md_path, session_dir), to_rel(raw_path, session_dir)])
        fallback.notes.extend(notes)
        return fallback
    except Exception as exc:  # pragma: no cover - runtime/network dependent
        fallback.notes.append(f"Authenticated Notion extraction failed: {exc}")
        return fallback


def enrich_canva(
    session: requests.Session,
    item: ResourceItem,
    session_dir: Path,
    resources_dir: Path,
    playwright_storage_state: Path | None,
    dry_run: bool,
) -> EnrichmentResult:
    fallback = enrich_generic_http(session, item, session_dir, resources_dir, dry_run)
    fallback.provider = "canva"

    if playwright_storage_state is None:
        fallback.notes.append("No Playwright storage-state provided; Canva authenticated capture skipped.")
        return fallback
    if not playwright_storage_state.exists():
        fallback.notes.append(f"Playwright storage-state not found: {playwright_storage_state}")
        return fallback

    try:
        from playwright.sync_api import sync_playwright  # type: ignore
    except Exception as exc:  # pragma: no cover - optional dependency
        fallback.notes.append(f"Playwright unavailable: {exc}")
        return fallback

    html_path = resources_dir / f"{slug(item.name)}.canva-auth.html"
    png_path = resources_dir / f"{slug(item.name)}.canva-auth.png"
    pdf_path = resources_dir / f"{slug(item.name)}.canva-auth.pdf"

    try:
        if dry_run:
            fallback.method = "playwright-auth-capture"
            fallback.authenticated = True
            fallback.notes.append("Dry-run: skipped browser launch.")
            return fallback

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context(storage_state=str(playwright_storage_state))
            page = context.new_page()
            page.goto(item.url, wait_until="networkidle", timeout=90000)
            page.wait_for_timeout(2000)

            html = page.content()
            save_text(html_path, html, dry_run=False)
            page.screenshot(path=str(png_path), full_page=True)
            fallback.output_files.extend([to_rel(html_path, session_dir), to_rel(png_path, session_dir)])
            fallback.method = "playwright-auth-capture"
            fallback.authenticated = True
            fallback.final_url = page.url
            fallback.title = page.title()

            try:
                page.pdf(path=str(pdf_path), print_background=True)
                fallback.output_files.append(to_rel(pdf_path, session_dir))
            except Exception as pdf_exc:
                fallback.notes.append(f"Page PDF generation unavailable: {pdf_exc}")

            context.close()
            browser.close()
        return fallback
    except Exception as exc:  # pragma: no cover - runtime/browser dependent
        fallback.notes.append(f"Authenticated Canva capture failed: {exc}")
        return fallback


def enrich_session(
    session_dir: Path,
    notion_token_v2: str | None,
    notion_active_user: str | None,
    playwright_storage_state: Path | None,
    cookies_json: Path | None,
    dry_run: bool,
) -> dict[str, Any]:
    resources = parse_manifest(session_dir)
    resources_dir = session_dir / ".resources"
    report_path = resources_dir / "resource_enrichment_report.json"

    if not dry_run:
        resources_dir.mkdir(parents=True, exist_ok=True)

    session = requests.Session()
    session.headers.update({"User-Agent": "Mozilla/5.0"})
    if cookies_json:
        load_cookies_into_session(session, cookies_json)

    results: list[EnrichmentResult] = []
    for item in resources:
        provider = detect_provider(item.url)
        if provider == "notion":
            res = enrich_notion(
                session=session,
                item=item,
                session_dir=session_dir,
                resources_dir=resources_dir,
                token_v2=notion_token_v2,
                active_user=notion_active_user,
                dry_run=dry_run,
            )
        elif provider == "canva":
            res = enrich_canva(
                session=session,
                item=item,
                session_dir=session_dir,
                resources_dir=resources_dir,
                playwright_storage_state=playwright_storage_state,
                dry_run=dry_run,
            )
        elif provider == "google-drive":
            res = enrich_google_drive(
                session=session,
                item=item,
                session_dir=session_dir,
                resources_dir=resources_dir,
                dry_run=dry_run,
            )
        else:
            res = enrich_generic_http(
                session=session,
                item=item,
                session_dir=session_dir,
                resources_dir=resources_dir,
                dry_run=dry_run,
            )
        results.append(res)

    report = {
        "ts": now_iso(),
        "session_dir": str(session_dir),
        "dry_run": dry_run,
        "resource_count": len(resources),
        "auth": {
            "notion_token_v2": bool(notion_token_v2),
            "notion_active_user": bool(notion_active_user),
            "playwright_storage_state": str(playwright_storage_state) if playwright_storage_state else None,
            "cookies_json": str(cookies_json) if cookies_json else None,
        },
        "results": [asdict(r) for r in results],
    }

    if not dry_run:
        report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return report


def collect_session_dirs(root: Path, session_dir: Path | None, all_sessions: bool) -> list[Path]:
    if session_dir:
        return [session_dir]
    if not all_sessions:
        raise ValueError("Provide --session-dir or use --all-sessions.")
    dirs: list[Path] = []
    for d in sorted(root.glob("2026-*")):
        if not d.is_dir():
            continue
        if (d / ".pipeline" / "resource_manifest.json").exists():
            dirs.append(d)
    return dirs


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Authenticated resource enrichment for session resources.")
    parser.add_argument("--root", default=str(DEFAULT_ROOT), help="Zoom root directory")
    parser.add_argument("--session-dir", help="Single session directory to enrich")
    parser.add_argument("--all-sessions", action="store_true", help="Process every session with resource manifest")
    parser.add_argument("--dry-run", action="store_true", help="Do not write artifacts/reports")

    parser.add_argument("--cookies-json", help="Optional cookies JSON for authenticated generic requests")

    parser.add_argument(
        "--notion-token-v2",
        default=os.environ.get("NOTION_TOKEN_V2"),
        help="Notion token_v2 cookie value (or set NOTION_TOKEN_V2)",
    )
    parser.add_argument(
        "--notion-active-user",
        default=os.environ.get("NOTION_ACTIVE_USER"),
        help="Notion active user UUID (or set NOTION_ACTIVE_USER)",
    )
    parser.add_argument(
        "--playwright-storage-state",
        default=os.environ.get("RESOURCE_PLAYWRIGHT_STORAGE_STATE"),
        help="Playwright storage-state JSON for authenticated Canva capture",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    root = Path(args.root).resolve()
    session_dir = Path(args.session_dir).resolve() if args.session_dir else None
    cookies_json = Path(args.cookies_json).resolve() if args.cookies_json else None
    storage_state = Path(args.playwright_storage_state).resolve() if args.playwright_storage_state else None

    try:
        targets = collect_session_dirs(root=root, session_dir=session_dir, all_sessions=args.all_sessions)
    except ValueError as exc:
        print(f"ERROR: {exc}")
        return 2

    if not targets:
        print("No target sessions found.")
        return 0

    enriched = 0
    for target in targets:
        report = enrich_session(
            session_dir=target,
            notion_token_v2=args.notion_token_v2,
            notion_active_user=args.notion_active_user,
            playwright_storage_state=storage_state,
            cookies_json=cookies_json,
            dry_run=args.dry_run,
        )
        enriched += 1
        print(
            f"[resource-enrichment] {target.name}: "
            f"{report['resource_count']} resources, dry_run={report['dry_run']}"
        )

    print(f"Completed resource enrichment for {enriched} session(s).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
