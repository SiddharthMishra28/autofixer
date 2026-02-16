# Complete Beginner Guide: Build and Use Your FastMCP Maintenance Agent

This guide is written for **absolute beginners**.

If you can copy/paste terminal commands, you can complete this setup.

---

## Table of Contents

1. [What you are building](#1-what-you-are-building)
2. [Concepts in plain English](#2-concepts-in-plain-english)
3. [Prerequisites checklist](#3-prerequisites-checklist)
4. [Step-by-step install (Windows/macOS/Linux)](#4-step-by-step-install-windowsmacoslinux)
5. [Run the MCP server](#5-run-the-mcp-server)
6. [Connect from VS Code](#6-connect-from-vs-code)
7. [Load your first knowledge into RAG](#7-load-your-first-knowledge-into-rag)
8. [Query your knowledge](#8-query-your-knowledge)
9. [Fetch GitLab issue + MR context](#9-fetch-gitlab-issue--mr-context)
10. [Use with Copilot/custom agent workflows](#10-use-with-copilotcustom-agent-workflows)
11. [Real maintenance workflow example](#11-real-maintenance-workflow-example)
12. [Troubleshooting](#12-troubleshooting)
13. [Security and production best practices](#13-security-and-production-best-practices)
14. [FAQ](#14-faq)

---

## 1) What you are building

You are building a local MCP server named `autofixer-maintenance-agent` that exposes tools to:

- read Excel files,
- read text documents,
- read source code directories,
- convert all of them to consistent chunks,
- store those chunks in ChromaDB (vector store),
- query that knowledge later,
- combine it with GitLab issue/MR data for patch generation.

In practical terms, this gives your coding assistant much better context for maintenance tasks.

---

## 2) Concepts in plain English

### MCP
MCP (Model Context Protocol) is a standard way for AI assistants to call tools.

### FastMCP
FastMCP is a Python framework for quickly creating MCP servers and tools.

### RAG
RAG = Retrieval-Augmented Generation. Instead of relying only on model memory, the assistant can retrieve relevant chunks from your knowledge base first.

### ChromaDB
ChromaDB is where your vectorized document/code chunks are stored and queried.

### Why this matters for maintenance
Ticket text + code diff alone is often not enough. RAG adds framework conventions, historical docs, and known failure patterns.

---

## 3) Prerequisites checklist

Before starting, ensure:

- [ ] You have Python 3.10+ (`python --version`)
- [ ] You can open a terminal (PowerShell, Terminal, bash, etc.)
- [ ] You have this repository cloned locally
- [ ] (Optional) You have a GitLab PAT token with API scope
- [ ] (Optional) You use VS Code and want MCP integration there

---

## 4) Step-by-step install (Windows/macOS/Linux)

> Run commands from the repository root.

### 4.1 Check Python version

```bash
python --version
```

If Python is below 3.10, install a newer version first.

### 4.2 Create virtual environment

```bash
python -m venv .venv
```

### 4.3 Activate virtual environment

#### macOS/Linux

```bash
source .venv/bin/activate
```

#### Windows PowerShell

```powershell
.\.venv\Scripts\Activate.ps1
```

#### Windows CMD

```cmd
.venv\Scripts\activate.bat
```

After activation, your shell usually shows `(.venv)` prefix.

### 4.4 Install package in editable mode

```bash
pip install -e .
```

Editable mode means local code changes are picked up without reinstalling each time.

---

## 5) Run the MCP server

Start server:

```bash
autofixer-mcp
```

Expected behavior:
- process stays running,
- waiting for MCP client requests over stdio.

To stop server: press `Ctrl + C`.

---

## 6) Connect from VS Code

This repository includes `.vscode/mcp.json` with two servers preconfigured:

1. `autofixer-maintenance-agent` (this project)
2. `gitlab` (official GitLab MCP server via `npx @gitlab-org/gitlab-mcp`)

### 6.1 Token setup

You must provide token input used by config:
- `GITLAB_TOKEN` for custom server tool,
- `GITLAB_PAT` for GitLab MCP server.

### 6.2 Verify MCP server registration

In VS Code MCP-compatible UI:
- confirm server appears,
- run a simple tool call like query after ingestion.

If server does not appear, see troubleshooting section.

---

## 7) Load your first knowledge into RAG

Use an MCP-capable client/chat to call tools.

### 7.1 Ingest a code repository

```text
ingest_codebase_to_rag(path="/absolute/path/to/framework-repo", collection="maintenance_knowledge")
```

Reads supported files:
- `.java`, `.feature`, `.xml`, `.py`, `.js`, `.jsx`, `.ts`, `.tsx`

### 7.2 Ingest an Excel file

```text
ingest_excel_to_rag(path="/absolute/path/to/test-mapping.xlsx", collection="maintenance_knowledge")
```

The ingestor keeps:
- merged range information,
- cell coordinates and values,
- sheet metadata.

### 7.3 Ingest text docs

```text
ingest_text_to_rag(path="/absolute/path/to/runbook.pdf", collection="maintenance_knowledge")
```

Supports:
- txt/md/rst/log/yaml/yml/csv/json/html/xml/pdf/docx

---

## 8) Query your knowledge

After ingestion:

```text
query_rag(collection="maintenance_knowledge", query="How is retry logic implemented for flaky login tests?", n_results=5)
```

You should receive top matching chunks + metadata.

Tip: ask precise questions using class names, feature names, modules, or exact failures.

---

## 9) Fetch GitLab issue + MR context

### 9.1 Set token first

macOS/Linux:

```bash
export GITLAB_TOKEN="<your_pat_here>"
```

Windows PowerShell:

```powershell
$env:GITLAB_TOKEN="<your_pat_here>"
```

### 9.2 Call tool

```text
gitlab_issue_and_mr_context(project_id="group/project", issue_iid=123, merge_request_iid=456)
```

Returns:
- issue title/description/state/labels/url,
- MR title/description/branches/url/changes list.

---

## 10) Use with Copilot/custom agent workflows

This repository includes `.github/copilot-instructions.md` to enforce behavior:

1. fetch ticket + diff from GitLab,
2. query RAG for supporting framework knowledge,
3. generate minimal patch + tests,
4. explain root cause and risks.

Recommended custom prompt style:

```text
Act as Autofixer maintenance agent.
- Pull GitLab issue #123 and MR #456.
- Query RAG for LoginTest retry logic and related cucumber steps.
- Suggest minimal, backward-compatible fix.
- Include tests and explain impact.
```

---

## 11) Real maintenance workflow example

Imagine: Login flow is flaky after a recent merge.

### Step A: Index context
- ingest framework repo,
- ingest flaky test report spreadsheet,
- ingest runbook PDF.

### Step B: Pull live issue/MR
- fetch issue + MR changes from GitLab.

### Step C: Ask focused RAG query
- “Show existing retry wrapper and timeout policy for login-related tests.”

### Step D: Generate patch
Assistant now has:
- current diff context,
- historical framework rules,
- operational guidance.

This usually produces more accurate patches than ticket-only prompting.

---

## 12) Troubleshooting

### Problem: `autofixer-mcp` command not found

Cause: package not installed in active environment.

Fix:
1. activate `.venv`,
2. run `pip install -e .` again.

### Problem: GitLab tool fails with token error

Cause: `GITLAB_TOKEN` not set.

Fix:
- set env var in current shell,
- ensure token has API permission.

### Problem: VS Code GitLab MCP fails

Cause: Node/npm not available for `npx` command.

Fix:
- install Node.js LTS,
- verify `npx --version` works,
- restart VS Code.

### Problem: PDF/DOCX ingestion returns little text

Cause: scanned PDF or complex formatting.

Fix:
- OCR document first,
- prefer text-native files when possible.

### Problem: Slow indexing for very large repositories

Fix:
- ingest module-by-module,
- create per-domain collections (`ui_tests`, `api_tests`, `core_framework`).

### Problem: Query quality is weak

Fix:
- ask narrower query,
- include class/test names,
- add more domain-specific docs,
- use collection separation by domain and version.

---

## 13) Security and production best practices

For enterprise use, add:

1. **PII/secret filtering** before indexing.
2. **Collection versioning** (`framework_v1`, `framework_v2`).
3. **Access controls** for ingestion/query tools.
4. **Audit logs** for who indexed and queried what.
5. **Backup strategy** for Chroma persistence directory.
6. **Dedicated embedding model** tuned to your domain.

---

## 14) FAQ

### Q: Do I need all tools?
No. You can start with only code ingestion + query.

### Q: Can I index multiple repositories?
Yes. You can ingest many repos into one collection or separate collections.

### Q: Can this replace GitLab MCP server?
No. This complements it. GitLab MCP gives live issue/MR context; this server gives your private RAG knowledge tools.

### Q: Where is data stored?
In local `.chroma` folder by default (configurable with `CHROMA_PERSIST_DIR`).

### Q: Is this cloud-only?
No. It can run locally.

---

## Final checklist

- [ ] Server starts with `autofixer-mcp`
- [ ] At least one code repo ingested
- [ ] At least one doc ingested
- [ ] `query_rag` returns relevant chunks
- [ ] GitLab context tool works with your token
- [ ] Copilot/custom prompt includes ticket + RAG workflow

You now have a complete beginner-to-practical setup for automated maintenance assistance.
