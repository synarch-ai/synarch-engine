# NotebookLM SDK Setup Guide

> Comprehensive guide for connecting to Google NotebookLM programmatically using `notebooklm-kit` SDK. Covers authentication, downloading all content types, and automated workflows.

## Table of Contents

- [Overview](#overview)
- [Why notebooklm-kit](#why-notebooklm-kit)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Authentication](#authentication)
- [Scripts Reference](#scripts-reference)
- [What Gets Downloaded](#what-gets-downloaded)
- [Architecture](#architecture)
- [Troubleshooting](#troubleshooting)
- [Known Limitations](#known-limitations)

---

## Overview

This project uses [`notebooklm-kit`](https://github.com/photon-hq/notebooklm-kit) (v2.2.0) — the most comprehensive TypeScript SDK for Google NotebookLM. It provides programmatic access to:

- **Notes** — full content, create/update/delete
- **Sources** — metadata, add URLs/files/YouTube/Drive
- **Artifacts** — quiz, flashcards, study guide, mind map, audio, video, slides, infographic, report, data table
- **Chat** — query notebook with streaming responses
- **Notebooks** — list, create, update, delete across your account

## Why notebooklm-kit

We evaluated **7 NotebookLM MCP servers** on npm before choosing this SDK:

| Solution | Notes | Sources | Artifacts | Audio | Quiz/Flash | Mind Map |
|---|---|---|---|---|---|---|
| `@pan-sec/notebooklm-mcp` | ❌ | metadata | ❌ | ❌ failed | ❌ | ❌ |
| `notebooklm-mcp-server` | ❌ | metadata | ❌ | ✅ | ❌ | ✅ generate |
| `@roomi-fields/notebooklm-mcp` | ❌ | metadata | ❌ | ❌ | ❌ | ❌ |
| **`notebooklm-kit` (SDK)** | **✅ 50 notes** | **✅ guides** | **✅ all** | **✅ 81MB** | **✅ 39+29KB** | **✅** |

**Bottom line:** `notebooklm-kit` is the only solution that can download notes, source guides, quiz, flashcards, and audio. No MCP server comes close.

## Prerequisites

- **Node.js** ≥ 18.0.0
- **npm** or **yarn**
- A Google account with NotebookLM notebooks
- If using 2FA: browser access for initial cookie extraction

## Installation

```bash
# In your project directory
npm install notebooklm-kit playwright tsx dotenv

# Global install (optional, for CLI use anywhere)
npm install -g notebooklm-kit tsx dotenv
```

## Authentication

### How It Works

The SDK uses Google session cookies + an auth token (`SNlM0e`) to authenticate API requests. These cookies expire periodically (~30 minutes for the token, longer for cookies).

**We solved this permanently** with a Playwright-based auto-refresh script that maintains a persistent browser profile.

### First-Time Setup

```bash
# 1. Run auth-refresh — a browser window opens
npx tsx scripts/auth-refresh.ts

# 2. Log into your Google account in the browser
# 3. Once NotebookLM loads, the script saves cookies automatically
# 4. Browser closes, .env is updated
```

### Subsequent Refreshes (Automatic, Headless)

```bash
# No browser window — uses saved session, extracts fresh cookies
npx tsx scripts/auth-refresh.ts
```

### Multi-Account Support

If your notebook is on a secondary Google account (e.g., `authuser=1`), set this in your scripts:

```typescript
const sdk = new NotebookLMClient({
  authUser: '1',  // 0 = primary, 1 = secondary, etc.
});
```

### .env File Format

```env
NOTEBOOKLM_AUTH_TOKEN=<SNlM0e token>
NOTEBOOKLM_COOKIES=<full cookie string>
```

> ⚠️ **NEVER commit .env** — it's in `.gitignore`

## Scripts Reference

### `scripts/auth-refresh.ts`
**Automated cookie refresh using Playwright persistent profile.**

```bash
npx tsx scripts/auth-refresh.ts
```

- First run: Opens visible browser for manual login
- Later runs: Headless, automatic, ~5 seconds
- Updates `.env` with fresh credentials

### `scripts/test-connection.ts`
**Verify connection and list notebooks.**

```bash
npx tsx scripts/test-connection.ts
```

### `scripts/download-all.ts`
**Download everything from target notebook.**

```bash
npx tsx scripts/auth-refresh.ts && npx tsx scripts/download-all.ts
```

Downloads: notes, sources, artifacts (with details), saves to `notebook-lm-research/full-archive/`

### `scripts/download-missing-3.ts`
**Quick download of Quiz, Flashcards, and Comparison artifacts.**

```bash
npx tsx scripts/auth-refresh.ts && npx tsx scripts/download-missing-3.ts
```

### `scripts/download-source-guides-via-chat.ts`
**Generate comprehensive source guides by asking NotebookLM chat.**

```bash
npx tsx scripts/auth-refresh.ts && npx tsx scripts/download-source-guides-via-chat.ts
```

Takes ~5 minutes (12 sources × ~20 seconds each). Each guide is ~5KB of rich content.

### Full Download Workflow

```bash
# Step 1: Refresh auth
npx tsx scripts/auth-refresh.ts

# Step 2: Download everything
npx tsx scripts/download-all.ts

# Step 3: Download source guides (separate because uses chat API)
npx tsx scripts/download-source-guides-via-chat.ts

# Step 4: Download quiz/flashcards (if missed)
npx tsx scripts/download-missing-3.ts
```

## What Gets Downloaded

### Programmatic Downloads

| Content | File | Size | Method |
|---|---|---|---|
| 50 Notes (full content) | `notes.json` | 169 KB | `sdk.notes.list()` |
| 12 Source Guides | `source-guides.json` | 65 KB | `sdk.generation.chat()` per source |
| 12 Source Metadata | `sources-list.json` | 3.7 KB | `sdk.sources.list()` |
| Quiz (Q&A) | `quiz_agent_quiz.json` | 39 KB | `sdk.artifacts.download()` |
| Flashcards | `flashcard_agents_flashcards.json` | 29 KB | `sdk.artifacts.download()` |
| Study Guide | `artifact_...blueprint.json` | 924 B | `sdk.artifacts.download()` |
| Audio Overview (MP3) | `audio_...swarms.mp3` | 81 MB | `sdk.artifacts.download()` |
| 8 Artifact Details | `*-detail.json` | ~5 KB | `sdk.artifacts.get()` |
| 43 Notebooks Index | `all-notebooks.json` | 9 KB | `sdk.notebooks.list()` |
| Chat History | `chat_history.json` | existing | MCP browser automation |

### Manual Downloads (SDK Limitations)

| Content | Why Manual | How |
|---|---|---|
| Video Overview | SDK says "experimental" | Download from NotebookLM UI |
| 2nd Audio File | 80MB+ causes auth timeout | Download from NotebookLM UI |
| Slide Deck Images | SDK can't extract Google's image URLs | Export from NotebookLM UI |

## Architecture

```
┌─────────────────────────────────────────────────┐
│  Your Machine                                    │
│                                                  │
│  ┌──────────────┐    ┌────────────────────────┐ │
│  │ auth-refresh  │    │  download scripts      │ │
│  │ (Playwright)  │───▶│  (notebooklm-kit SDK)  │ │
│  └──────┬───────┘    └──────────┬─────────────┘ │
│         │                       │                │
│         ▼                       ▼                │
│  ┌──────────────┐    ┌────────────────────────┐ │
│  │ .auth-profile │    │  .env (cookies+token)  │ │
│  │ (persistent)  │    │  (auto-refreshed)      │ │
│  └──────────────┘    └────────────────────────┘ │
│                                                  │
│                       │ HTTP API calls           │
│                       ▼                          │
│              ┌────────────────┐                  │
│              │ Google NotebookLM                 │
│              │ (notebooklm.google.com)           │
│              └────────────────┘                  │
└─────────────────────────────────────────────────┘
```

## Troubleshooting

### "Unauthenticated" Error
Cookies expired. Run `npx tsx scripts/auth-refresh.ts` first.

### "Request failed: 400 Bad Request"
Wrong `authUser` setting. Check which Google account has the notebook (look at `?authuser=0` or `?authuser=1` in the URL).

### Audio download hangs/times out
The `artifacts.get()` for audio types internally fetches the full 80MB+ audio data. Skip `get()` for audio types in your scripts — use `download()` directly.

### Script stuck on artifact
Kill with `Ctrl+C` and re-run. Likely auth expired mid-download for large files.

### "No slide image URLs found"
This is an SDK bug in `extractSlideImageUrls()`. The slides exist in NotebookLM UI but the SDK can't parse Google's current response format. Export slides manually.

### Playwright browser not launching
```bash
npx playwright install chromium
```

## Known Limitations

1. **Cookie expiry**: Auth tokens rotate every ~30 minutes. Always run `auth-refresh.ts` before downloads.
2. **Source guides**: Not available via API. We work around this by using `chat()` to ask NotebookLM to summarize each source.
3. **Slide downloads**: SDK bug prevents image URL extraction. Manual export required.
4. **Video downloads**: Marked as "experimental" in SDK. Detail JSON has the URL for manual download.
5. **Large audio files**: Can cause auth timeout during download. Use `download()` not `get()`.
6. **Rate limits**: NotebookLM has undocumented rate limits. Space out bulk operations.

## Project Structure

```
synarch-ai/
├── .env                           # Auth credentials (gitignored)
├── .gitignore                     # Protects .env + .auth-profile + node_modules
├── .auth-profile/                 # Playwright persistent browser session
├── package.json                   # notebooklm-kit, playwright, tsx, dotenv
├── NOTEBOOKLM-SDK-SETUP-GUIDE.md  # This file
├── scripts/
│   ├── auth-refresh.ts            # ♻️ Auto cookie refresh
│   ├── test-connection.ts         # 🧪 Connection test
│   ├── download-all.ts            # 📥 Full download
│   ├── download-missing-3.ts      # 📥 Quiz/Flashcards/Comparison
│   ├── download-source-guides-via-chat.ts  # 📥 Source guides
│   ├── download-data-only.ts      # 📥 Data artifacts (no audio/video)
│   ├── download-remaining.ts      # 📥 Remaining artifacts
│   ├── download-slides.ts         # 📥 Slide deck attempt
│   └── download-source-guides.ts  # 📥 Direct source guide attempt
└── notebook-lm-research/
    ├── archive_report.md          # Archive summary
    ├── chat_history.json          # 20 chat messages
    ├── sources.json               # Legacy source list
    └── full-archive/
        ├── notes.json             # 50 notes with full content
        ├── source-guides.json     # 12 comprehensive guides
        ├── sources-list.json      # Source metadata
        ├── sources-full.json      # Source details
        ├── artifacts-list.json    # All 8 artifacts metadata
        ├── all-notebooks.json     # 43 notebooks index
        ├── target-notebook-raw.json
        └── artifacts/
            ├── *.mp3              # Audio overview
            ├── *.json             # Quiz, flashcards, study guide, details
            ├── *.pdf              # Slide deck, gap analysis
            ├── *.pptx             # Exported slides
            ├── *.xls              # Comparison table
            ├── *.png              # Infographic
            ├── *.mm               # Mind map
            ├── *.docx             # SAMAS document
            └── *.md               # Reports, flashcards
```

---

*Created: 2026-02-13 | SDK: notebooklm-kit v2.2.0 | Node: v22.21.1*
