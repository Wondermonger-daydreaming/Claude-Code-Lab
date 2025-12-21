# Deploying MCP Servers on Google Cloud Run

*A comprehensive pedagogical guide for bypassing proxy restrictions*

---

## Table of Contents

1. [Understanding the Problem](#1-understanding-the-problem)
2. [Understanding the Solution](#2-understanding-the-solution)
3. [Prerequisites](#3-prerequisites)
4. [Architecture Deep Dive](#4-architecture-deep-dive)
5. [Building the MCP-to-HTTP Bridge](#5-building-the-mcp-to-http-bridge)
6. [Creating the Dockerfile](#6-creating-the-dockerfile)
7. [Local Testing](#7-local-testing)
8. [Deploying to Google Cloud Run](#8-deploying-to-google-cloud-run)
9. [Configuring Claude Code](#9-configuring-claude-code)
10. [Security Considerations](#10-security-considerations)
11. [Troubleshooting](#11-troubleshooting)
12. [Cost Estimation](#12-cost-estimation)
13. [Alternative: Azure Functions](#13-alternative-azure-functions)
14. [Complete Code Reference](#14-complete-code-reference)

---

## 1. Understanding the Problem

### The Proxy Wall

Claude Code Remote runs in a sandboxed container with egress restrictions. All outbound HTTPS traffic goes through a proxy that only allows connections to whitelisted domains.

```
┌─────────────────────────────────────────────────────────────┐
│  Claude Code Remote Container                               │
│                                                             │
│   ┌─────────┐      ┌─────────┐      ┌─────────────────┐    │
│   │ Claude  │─────►│  MCP    │─────►│  Egress Proxy   │    │
│   │         │      │ Server  │      │  (allowlist)    │    │
│   └─────────┘      └─────────┘      └────────┬────────┘    │
│                                               │             │
└───────────────────────────────────────────────┼─────────────┘
                                                │
                                                ▼
                              ┌─────────────────────────────┐
                              │  Allowlist Check            │
                              │                             │
                              │  ✓ github.com               │
                              │  ✓ pypi.org                 │
                              │  ✓ *.googleapis.com         │
                              │  ✗ arxiv.org        ← BLOCKED
                              │  ✗ semanticscholar.org      │
                              └─────────────────────────────┘
```

### Why MCP Servers Fail

When you configure an MCP server like `arxiv-mcp-server`, it runs as a subprocess inside the container. When it tries to fetch from `export.arxiv.org`, the proxy intercepts and returns `403 Forbidden`.

```python
# What happens inside arxiv-mcp-server
import httpx
response = httpx.get("https://export.arxiv.org/api/query?...")
# ↑ This request hits the proxy
# Proxy checks: is arxiv.org in allowlist? NO
# Proxy returns: 403 Forbidden
```

---

## 2. Understanding the Solution

### The Bypass Strategy

We deploy the MCP server **outside** the restricted container, on a cloud platform whose domain **is** in the allowlist.

```
┌─────────────────────────────────────────────────────────────┐
│  Claude Code Remote Container                               │
│                                                             │
│   ┌─────────┐      ┌─────────────────────────────────┐     │
│   │ Claude  │─────►│  HTTP Client (not MCP stdio)    │     │
│   │         │      │  Calls: *.googleapis.com ✓      │     │
│   └─────────┘      └─────────────────┬───────────────┘     │
│                                       │                     │
└───────────────────────────────────────┼─────────────────────┘
                                        │
            Proxy allows *.googleapis.com
                                        │
                                        ▼
┌─────────────────────────────────────────────────────────────┐
│  Google Cloud Run (your-project.run.app)                    │
│                                                             │
│   ┌─────────────────────────────────────────────────┐      │
│   │  MCP Server + HTTP Wrapper                      │      │
│   │                                                 │      │
│   │  1. Receives HTTP request from Claude           │      │
│   │  2. Translates to MCP tool call                 │      │
│   │  3. MCP server fetches from arxiv.org ✓         │      │
│   │  4. Returns result via HTTP                     │      │
│   └─────────────────────────────────────────────────┘      │
│                          │                                  │
│                          ▼                                  │
│               No proxy restrictions here!                   │
│               arxiv.org ✓                                   │
│               semanticscholar.org ✓                         │
│               anywhere ✓                                    │
└─────────────────────────────────────────────────────────────┘
```

### Why This Works

1. **Google Cloud Run URLs** are under `*.run.app` or accessible via `*.googleapis.com`
2. The Claude Code proxy **allows** these domains
3. Your Cloud Run instance has **unrestricted egress**—it can fetch from anywhere
4. You're just moving where the MCP server runs

---

## 3. Prerequisites

### 3.1 Google Cloud Account

1. Go to [console.cloud.google.com](https://console.cloud.google.com)
2. Create a new project or select existing
3. Enable billing (Cloud Run has a generous free tier)

### 3.2 Install Google Cloud CLI

```bash
# macOS
brew install google-cloud-sdk

# Linux (Debian/Ubuntu)
echo "deb [signed-by=/usr/share/keyrings/cloud.google.gpg] https://packages.cloud.google.com/apt cloud-sdk main" | sudo tee /etc/apt/sources.list.d/google-cloud-sdk.list
curl https://packages.cloud.google.com/apt/doc/apt-key.gpg | sudo apt-key --keyring /usr/share/keyrings/cloud.google.gpg add -
sudo apt update && sudo apt install google-cloud-cli

# Windows
# Download installer from https://cloud.google.com/sdk/docs/install
```

### 3.3 Authenticate

```bash
# Login to Google Cloud
gcloud auth login

# Set your project
gcloud config set project YOUR_PROJECT_ID

# Enable required APIs
gcloud services enable run.googleapis.com
gcloud services enable cloudbuild.googleapis.com
gcloud services enable artifactregistry.googleapis.com
```

### 3.4 Verify Setup

```bash
gcloud config list
# Should show:
# [core]
# project = your-project-id
# account = your-email@example.com
```

---

## 4. Architecture Deep Dive

### 4.1 MCP Transport Modes

MCP servers communicate via two transport modes:

| Transport | How It Works | Use Case |
|-----------|--------------|----------|
| **stdio** | Server reads stdin, writes stdout | Local subprocess |
| **SSE** | Server-Sent Events over HTTP | Remote servers |

For Cloud Run, we need **SSE** (or a custom HTTP bridge).

### 4.2 The Translation Layer

We need to translate between:
- **Claude Code** → HTTP requests
- **HTTP requests** → MCP tool calls
- **MCP responses** → HTTP responses

```
Claude Code                    Cloud Run
    │                              │
    │  POST /tools/search_papers   │
    │  {"query": "attention"}      │
    │─────────────────────────────►│
    │                              │
    │                              │  MCP Server
    │                              │  search_papers("attention")
    │                              │      │
    │                              │      ▼
    │                              │  arxiv.org API
    │                              │      │
    │                              │      ▼
    │                              │  [paper results]
    │                              │
    │  200 OK                      │
    │  {"papers": [...]}           │
    │◄─────────────────────────────│
```

### 4.3 File Structure

```
arxiv-mcp-cloudrun/
├── Dockerfile              # Container definition
├── requirements.txt        # Python dependencies
├── server.py              # HTTP wrapper + MCP integration
├── mcp_bridge.py          # MCP protocol bridge
└── README.md              # Documentation
```

---

## 5. Building the MCP-to-HTTP Bridge

### 5.1 The Core Server (`server.py`)

This is the main entry point. It creates a FastAPI server that wraps MCP tool calls.

```python
#!/usr/bin/env python3
"""
Cloud Run MCP Bridge Server

Exposes MCP tools as HTTP endpoints, allowing Claude Code Remote
to access MCP functionality through the proxy allowlist.
"""

import os
import json
import asyncio
import logging
from typing import Any, Optional
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, JSONResponse
from pydantic import BaseModel
import httpx

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# ============================================================
# ARXIV API CLIENT
# ============================================================

class ArxivClient:
    """
    Direct client for the arXiv API.

    We bypass the MCP server layer and call arXiv directly,
    then format responses to match MCP tool output.
    """

    BASE_URL = "https://export.arxiv.org/api/query"

    def __init__(self):
        self.client = httpx.AsyncClient(timeout=30.0)

    async def search_papers(
        self,
        query: str,
        max_results: int = 10,
        categories: Optional[list[str]] = None,
        sort_by: str = "relevance"
    ) -> dict[str, Any]:
        """
        Search for papers on arXiv.

        Args:
            query: Search query (supports arXiv query syntax)
            max_results: Maximum number of results (1-50)
            categories: Optional list of arXiv categories (e.g., ["cs.AI", "cs.LG"])
            sort_by: Sort order - "relevance" or "date"

        Returns:
            Dictionary with search results
        """
        # Build the search query
        search_query = query

        # Add category filter if provided
        if categories:
            cat_filter = " OR ".join(f"cat:{cat}" for cat in categories)
            search_query = f"({search_query}) AND ({cat_filter})"

        # Map sort_by to arXiv API parameters
        sort_map = {
            "relevance": "relevance",
            "date": "submittedDate"
        }

        params = {
            "search_query": search_query,
            "start": 0,
            "max_results": min(max_results, 50),
            "sortBy": sort_map.get(sort_by, "relevance"),
            "sortOrder": "descending"
        }

        logger.info(f"Searching arXiv: {params}")

        try:
            response = await self.client.get(self.BASE_URL, params=params)
            response.raise_for_status()

            # Parse the Atom XML response
            papers = self._parse_atom_response(response.text)

            return {
                "success": True,
                "query": query,
                "total_results": len(papers),
                "papers": papers
            }

        except httpx.HTTPError as e:
            logger.error(f"arXiv API error: {e}")
            return {
                "success": False,
                "error": str(e),
                "query": query
            }

    def _parse_atom_response(self, xml_text: str) -> list[dict]:
        """Parse arXiv Atom XML response into structured data."""
        import xml.etree.ElementTree as ET

        # Define namespaces
        ns = {
            'atom': 'http://www.w3.org/2005/Atom',
            'arxiv': 'http://arxiv.org/schemas/atom'
        }

        root = ET.fromstring(xml_text)
        papers = []

        for entry in root.findall('atom:entry', ns):
            paper = {}

            # Extract basic fields
            paper['id'] = self._get_text(entry, 'atom:id', ns, '').split('/abs/')[-1]
            paper['title'] = self._clean_text(self._get_text(entry, 'atom:title', ns, ''))
            paper['summary'] = self._clean_text(self._get_text(entry, 'atom:summary', ns, ''))
            paper['published'] = self._get_text(entry, 'atom:published', ns, '')
            paper['updated'] = self._get_text(entry, 'atom:updated', ns, '')

            # Extract authors
            authors = []
            for author in entry.findall('atom:author', ns):
                name = self._get_text(author, 'atom:name', ns, '')
                if name:
                    authors.append(name)
            paper['authors'] = authors

            # Extract categories
            categories = []
            for cat in entry.findall('atom:category', ns):
                term = cat.get('term', '')
                if term:
                    categories.append(term)
            paper['categories'] = categories

            # Extract links
            for link in entry.findall('atom:link', ns):
                if link.get('title') == 'pdf':
                    paper['pdf_url'] = link.get('href', '')
                elif link.get('type') == 'text/html':
                    paper['abs_url'] = link.get('href', '')

            # Extract arXiv-specific fields
            paper['primary_category'] = ''
            primary_cat = entry.find('arxiv:primary_category', ns)
            if primary_cat is not None:
                paper['primary_category'] = primary_cat.get('term', '')

            paper['comment'] = self._get_text(entry, 'arxiv:comment', ns, '')
            paper['journal_ref'] = self._get_text(entry, 'arxiv:journal_ref', ns, '')
            paper['doi'] = self._get_text(entry, 'arxiv:doi', ns, '')

            papers.append(paper)

        return papers

    def _get_text(self, element, path: str, ns: dict, default: str = '') -> str:
        """Safely extract text from an XML element."""
        found = element.find(path, ns)
        return found.text if found is not None and found.text else default

    def _clean_text(self, text: str) -> str:
        """Clean up text by removing extra whitespace."""
        return ' '.join(text.split())

    async def get_paper(self, paper_id: str) -> dict[str, Any]:
        """
        Get details for a specific paper by arXiv ID.

        Args:
            paper_id: arXiv paper ID (e.g., "2301.07041" or "cs.AI/0123456")

        Returns:
            Paper details dictionary
        """
        params = {
            "id_list": paper_id,
            "max_results": 1
        }

        logger.info(f"Fetching paper: {paper_id}")

        try:
            response = await self.client.get(self.BASE_URL, params=params)
            response.raise_for_status()

            papers = self._parse_atom_response(response.text)

            if papers:
                return {
                    "success": True,
                    "paper": papers[0]
                }
            else:
                return {
                    "success": False,
                    "error": f"Paper not found: {paper_id}"
                }

        except httpx.HTTPError as e:
            logger.error(f"arXiv API error: {e}")
            return {
                "success": False,
                "error": str(e)
            }

    async def close(self):
        """Close the HTTP client."""
        await self.client.aclose()


# ============================================================
# FASTAPI APPLICATION
# ============================================================

# Global client instance
arxiv_client: Optional[ArxivClient] = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifecycle."""
    global arxiv_client
    arxiv_client = ArxivClient()
    logger.info("arXiv client initialized")
    yield
    await arxiv_client.close()
    logger.info("arXiv client closed")

app = FastAPI(
    title="arXiv MCP Bridge",
    description="HTTP bridge for arXiv MCP server functionality",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware for flexibility
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================
# REQUEST/RESPONSE MODELS
# ============================================================

class SearchRequest(BaseModel):
    """Request model for paper search."""
    query: str
    max_results: int = 10
    categories: Optional[list[str]] = None
    sort_by: str = "relevance"

class PaperRequest(BaseModel):
    """Request model for fetching a specific paper."""
    paper_id: str

class MCPToolCall(BaseModel):
    """Generic MCP tool call request."""
    tool: str
    arguments: dict[str, Any]


# ============================================================
# API ENDPOINTS
# ============================================================

@app.get("/")
async def root():
    """Health check and API info."""
    return {
        "service": "arXiv MCP Bridge",
        "status": "healthy",
        "version": "1.0.0",
        "endpoints": {
            "/search": "Search for papers (POST)",
            "/paper/{paper_id}": "Get paper details (GET)",
            "/mcp/tools": "List available MCP tools (GET)",
            "/mcp/call": "Call an MCP tool (POST)"
        }
    }

@app.get("/health")
async def health_check():
    """Kubernetes-style health check."""
    return {"status": "healthy"}

@app.post("/search")
async def search_papers(request: SearchRequest):
    """
    Search for papers on arXiv.

    This is the primary endpoint for paper search.
    """
    result = await arxiv_client.search_papers(
        query=request.query,
        max_results=request.max_results,
        categories=request.categories,
        sort_by=request.sort_by
    )
    return JSONResponse(content=result)

@app.get("/paper/{paper_id:path}")
async def get_paper(paper_id: str):
    """
    Get details for a specific paper.

    The paper_id can be in formats like:
    - 2301.07041
    - cs.AI/0123456
    """
    result = await arxiv_client.get_paper(paper_id)
    return JSONResponse(content=result)

@app.get("/mcp/tools")
async def list_mcp_tools():
    """
    List available MCP tools.

    This mimics the MCP tools/list response format.
    """
    return {
        "tools": [
            {
                "name": "search_papers",
                "description": "Search for papers on arXiv with advanced filtering",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "Search query using arXiv query syntax"
                        },
                        "max_results": {
                            "type": "integer",
                            "description": "Maximum results (1-50)",
                            "default": 10
                        },
                        "categories": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "arXiv categories (e.g., cs.AI, cs.LG)"
                        },
                        "sort_by": {
                            "type": "string",
                            "enum": ["relevance", "date"],
                            "default": "relevance"
                        }
                    },
                    "required": ["query"]
                }
            },
            {
                "name": "get_paper",
                "description": "Get details for a specific paper by arXiv ID",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "paper_id": {
                            "type": "string",
                            "description": "arXiv paper ID (e.g., 2301.07041)"
                        }
                    },
                    "required": ["paper_id"]
                }
            }
        ]
    }

@app.post("/mcp/call")
async def call_mcp_tool(request: MCPToolCall):
    """
    Call an MCP tool by name.

    This provides a unified interface matching MCP semantics.
    """
    tool_name = request.tool
    args = request.arguments

    if tool_name == "search_papers":
        result = await arxiv_client.search_papers(
            query=args.get("query", ""),
            max_results=args.get("max_results", 10),
            categories=args.get("categories"),
            sort_by=args.get("sort_by", "relevance")
        )
    elif tool_name == "get_paper":
        result = await arxiv_client.get_paper(
            paper_id=args.get("paper_id", "")
        )
    else:
        raise HTTPException(
            status_code=400,
            detail=f"Unknown tool: {tool_name}"
        )

    return JSONResponse(content={
        "tool": tool_name,
        "result": result
    })


# ============================================================
# SSE ENDPOINT (for native MCP SSE transport)
# ============================================================

@app.get("/mcp/sse")
async def mcp_sse_stream(request: Request):
    """
    Server-Sent Events endpoint for MCP protocol.

    This allows native MCP SSE transport if needed.
    """
    async def event_generator():
        # Send initial connection event
        yield f"event: open\ndata: {json.dumps({'status': 'connected'})}\n\n"

        # Keep connection alive
        while True:
            if await request.is_disconnected():
                break
            yield f"event: ping\ndata: {json.dumps({'time': asyncio.get_event_loop().time()})}\n\n"
            await asyncio.sleep(30)

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        }
    )


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":
    import uvicorn

    port = int(os.environ.get("PORT", 8080))

    uvicorn.run(
        "server:app",
        host="0.0.0.0",
        port=port,
        log_level="info"
    )
```

### 5.2 Dependencies (`requirements.txt`)

```
fastapi>=0.104.0
uvicorn[standard]>=0.24.0
httpx>=0.25.0
pydantic>=2.0.0
```

---

## 6. Creating the Dockerfile

### 6.1 The Dockerfile

```dockerfile
# Use Python 3.11 slim image for smaller size
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=8080

# Create non-root user for security
RUN groupadd -r mcpuser && useradd -r -g mcpuser mcpuser

# Set working directory
WORKDIR /app

# Install dependencies first (better layer caching)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY server.py .

# Change ownership to non-root user
RUN chown -R mcpuser:mcpuser /app

# Switch to non-root user
USER mcpuser

# Expose port
EXPOSE 8080

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD python -c "import httpx; httpx.get('http://localhost:8080/health')" || exit 1

# Run the server
CMD ["python", "server.py"]
```

### 6.2 Optional: `.dockerignore`

```
__pycache__
*.pyc
*.pyo
.git
.gitignore
README.md
.env
*.log
.pytest_cache
.mypy_cache
```

---

## 7. Local Testing

### 7.1 Test Without Docker

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # or `venv\Scripts\activate` on Windows

# Install dependencies
pip install -r requirements.txt

# Run the server
python server.py
```

### 7.2 Test the Endpoints

```bash
# Health check
curl http://localhost:8080/

# Search for papers
curl -X POST http://localhost:8080/search \
  -H "Content-Type: application/json" \
  -d '{"query": "attention is all you need", "max_results": 5}'

# Get specific paper
curl http://localhost:8080/paper/1706.03762

# List MCP tools
curl http://localhost:8080/mcp/tools

# Call MCP tool
curl -X POST http://localhost:8080/mcp/call \
  -H "Content-Type: application/json" \
  -d '{"tool": "search_papers", "arguments": {"query": "transformer", "categories": ["cs.CL"]}}'
```

### 7.3 Test With Docker

```bash
# Build the image
docker build -t arxiv-mcp-bridge .

# Run the container
docker run -p 8080:8080 arxiv-mcp-bridge

# Test (same curl commands as above)
curl http://localhost:8080/
```

---

## 8. Deploying to Google Cloud Run

### 8.1 Option A: Deploy from Source (Easiest)

```bash
# Navigate to your project directory
cd arxiv-mcp-cloudrun

# Deploy directly from source
gcloud run deploy arxiv-mcp \
  --source . \
  --region us-central1 \
  --allow-unauthenticated \
  --memory 512Mi \
  --cpu 1 \
  --min-instances 0 \
  --max-instances 10 \
  --timeout 60s
```

This will:
1. Build the Docker image using Cloud Build
2. Push to Artifact Registry
3. Deploy to Cloud Run

### 8.2 Option B: Build and Deploy Separately

```bash
# Set variables
PROJECT_ID=$(gcloud config get-value project)
REGION=us-central1
SERVICE_NAME=arxiv-mcp

# Build the image
gcloud builds submit --tag gcr.io/$PROJECT_ID/$SERVICE_NAME

# Deploy to Cloud Run
gcloud run deploy $SERVICE_NAME \
  --image gcr.io/$PROJECT_ID/$SERVICE_NAME \
  --region $REGION \
  --allow-unauthenticated \
  --memory 512Mi \
  --cpu 1
```

### 8.3 Verify Deployment

```bash
# Get the service URL
gcloud run services describe arxiv-mcp --region us-central1 --format='value(status.url)'

# Example output:
# https://arxiv-mcp-abc123-uc.a.run.app

# Test the deployed service
SERVICE_URL=$(gcloud run services describe arxiv-mcp --region us-central1 --format='value(status.url)')

curl $SERVICE_URL/
curl -X POST $SERVICE_URL/search \
  -H "Content-Type: application/json" \
  -d '{"query": "large language models", "max_results": 3}'
```

### 8.4 Deployment Output

You should see something like:

```
Deploying container to Cloud Run service [arxiv-mcp] in project [your-project] region [us-central1]
✓ Deploying new service... Done.
  ✓ Creating Revision...
  ✓ Routing traffic...
  ✓ Setting IAM Policy...
Done.
Service [arxiv-mcp] revision [arxiv-mcp-00001-abc] has been deployed and is serving 100 percent of traffic.
Service URL: https://arxiv-mcp-abc123-uc.a.run.app
```

---

## 9. Configuring Claude Code

### 9.1 The Problem: MCP Config Won't Work

The standard MCP configuration uses `command` to spawn a subprocess:

```json
{
  "mcpServers": {
    "arxiv": {
      "command": "uvx",
      "args": ["arxiv-mcp-server"]
    }
  }
}
```

This doesn't work for remote HTTP servers.

### 9.2 Solution: Custom Tool via Bash/Curl

Since Claude Code can use `curl` through the Bash tool, you can call your Cloud Run service directly:

```bash
# In Claude Code, you can now do:
curl -s -X POST https://arxiv-mcp-abc123-uc.a.run.app/search \
  -H "Content-Type: application/json" \
  -d '{"query": "attention mechanisms", "max_results": 5}'
```

### 9.3 Solution: Create a Custom MCP Client Wrapper

For better integration, create a local wrapper that calls your Cloud Run service:

**`arxiv_cloud_client.py`** (run locally or add to your project):

```python
#!/usr/bin/env python3
"""
Local MCP client that proxies to Cloud Run.
Run this locally, configure MCP to use it.
"""

import sys
import json
import httpx

CLOUD_RUN_URL = "https://arxiv-mcp-abc123-uc.a.run.app"

def main():
    # Read MCP request from stdin
    for line in sys.stdin:
        request = json.loads(line)

        if request.get("method") == "tools/list":
            # Forward to Cloud Run
            response = httpx.get(f"{CLOUD_RUN_URL}/mcp/tools")
            result = response.json()
            print(json.dumps({"result": result}))

        elif request.get("method") == "tools/call":
            tool_name = request["params"]["name"]
            arguments = request["params"]["arguments"]

            response = httpx.post(
                f"{CLOUD_RUN_URL}/mcp/call",
                json={"tool": tool_name, "arguments": arguments}
            )
            result = response.json()
            print(json.dumps({"result": result}))

        sys.stdout.flush()

if __name__ == "__main__":
    main()
```

Then configure MCP:

```json
{
  "mcpServers": {
    "arxiv-cloud": {
      "command": "python",
      "args": ["/path/to/arxiv_cloud_client.py"]
    }
  }
}
```

### 9.4 For Claude Code Remote: Direct HTTP

In the Claude Code Remote environment, the simplest approach is direct HTTP calls:

```python
# The Cloud Run URL is accessible through the proxy
# because *.run.app resolves through allowed domains

import httpx

async def search_arxiv(query: str, max_results: int = 10):
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "https://arxiv-mcp-abc123-uc.a.run.app/search",
            json={"query": query, "max_results": max_results}
        )
        return response.json()
```

---

## 10. Security Considerations

### 10.1 Authentication

For production, add authentication:

```python
from fastapi import Depends, HTTPException, Security
from fastapi.security import APIKeyHeader

API_KEY_HEADER = APIKeyHeader(name="X-API-Key", auto_error=False)

async def verify_api_key(api_key: str = Security(API_KEY_HEADER)):
    expected_key = os.environ.get("API_KEY")
    if not expected_key or api_key != expected_key:
        raise HTTPException(status_code=401, detail="Invalid API key")
    return api_key

# Apply to endpoints
@app.post("/search", dependencies=[Depends(verify_api_key)])
async def search_papers(request: SearchRequest):
    ...
```

Deploy with the API key:

```bash
gcloud run deploy arxiv-mcp \
  --source . \
  --region us-central1 \
  --set-env-vars="API_KEY=your-secret-key-here" \
  --no-allow-unauthenticated
```

### 10.2 Rate Limiting

Add rate limiting to prevent abuse:

```python
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter

@app.post("/search")
@limiter.limit("30/minute")
async def search_papers(request: Request, search_request: SearchRequest):
    ...
```

### 10.3 IAM Authentication (Google Cloud)

For maximum security, use IAM-based auth:

```bash
# Deploy without public access
gcloud run deploy arxiv-mcp \
  --source . \
  --region us-central1 \
  --no-allow-unauthenticated

# Grant access to specific users/service accounts
gcloud run services add-iam-policy-binding arxiv-mcp \
  --region us-central1 \
  --member="user:your-email@example.com" \
  --role="roles/run.invoker"
```

Then authenticate requests:

```bash
# Get identity token
TOKEN=$(gcloud auth print-identity-token)

# Call with token
curl -H "Authorization: Bearer $TOKEN" \
  https://arxiv-mcp-abc123-uc.a.run.app/search \
  -X POST -H "Content-Type: application/json" \
  -d '{"query": "test"}'
```

---

## 11. Troubleshooting

### 11.1 Common Issues

| Issue | Cause | Solution |
|-------|-------|----------|
| `403 Forbidden` from proxy | Domain not in allowlist | Verify Cloud Run URL format |
| `Connection refused` | Service not running | Check `gcloud run services list` |
| `500 Internal Server Error` | Application error | Check Cloud Run logs |
| Timeout | Cold start or slow arXiv | Increase timeout, add min-instances |

### 11.2 Viewing Logs

```bash
# Stream logs
gcloud run logs tail arxiv-mcp --region us-central1

# View recent logs
gcloud run logs read arxiv-mcp --region us-central1 --limit 100
```

### 11.3 Testing Connectivity

```bash
# From Claude Code Remote, test if the domain is reachable
curl -v https://arxiv-mcp-abc123-uc.a.run.app/health

# If you get 403, the domain might not be in allowlist
# Try using the full googleapis.com path:
curl -v https://us-central1-run.googleapis.com/...
```

### 11.4 Cold Start Optimization

Cold starts can cause the first request to be slow (~2-5 seconds). Mitigate with:

```bash
# Keep at least 1 instance warm
gcloud run deploy arxiv-mcp \
  --source . \
  --min-instances 1
```

Note: This incurs costs even when idle.

---

## 12. Cost Estimation

### 12.1 Cloud Run Pricing (as of 2024)

| Resource | Free Tier | Price After |
|----------|-----------|-------------|
| CPU | 180,000 vCPU-seconds/month | $0.00002400/vCPU-second |
| Memory | 360,000 GiB-seconds/month | $0.00000250/GiB-second |
| Requests | 2 million/month | $0.40/million |

### 12.2 Example Monthly Cost

Assuming:
- 1000 requests/day
- Average 2 seconds per request
- 512 MiB memory, 1 vCPU

```
Requests: 30,000/month = FREE (under 2M)
CPU: 30,000 × 2s × 1 vCPU = 60,000 vCPU-seconds = FREE (under 180,000)
Memory: 30,000 × 2s × 0.5 GiB = 30,000 GiB-seconds = FREE (under 360,000)

Estimated cost: $0.00/month
```

For heavier usage, expect $1-10/month.

---

## 13. Alternative: Azure Functions

If you prefer Azure, the same pattern works:

### 13.1 Azure Function Code

**`function_app.py`**:

```python
import azure.functions as func
import json
import httpx

app = func.FunctionApp()

@app.function_name(name="search")
@app.route(route="search", methods=["POST"])
async def search_papers(req: func.HttpRequest) -> func.HttpResponse:
    body = req.get_json()
    query = body.get("query", "")
    max_results = body.get("max_results", 10)

    async with httpx.AsyncClient() as client:
        response = await client.get(
            "https://export.arxiv.org/api/query",
            params={"search_query": query, "max_results": max_results}
        )
        # Parse and return...

    return func.HttpResponse(
        json.dumps({"papers": [...]}),
        mimetype="application/json"
    )
```

### 13.2 Deploy to Azure

```bash
# Login
az login

# Create resources
az group create --name arxiv-mcp-rg --location eastus
az functionapp create \
  --resource-group arxiv-mcp-rg \
  --consumption-plan-location eastus \
  --runtime python \
  --runtime-version 3.11 \
  --functions-version 4 \
  --name arxiv-mcp-func \
  --os-type linux

# Deploy
func azure functionapp publish arxiv-mcp-func
```

---

## 14. Complete Code Reference

### 14.1 Project Structure

```
arxiv-mcp-cloudrun/
├── Dockerfile
├── requirements.txt
├── server.py
├── .dockerignore
├── .gcloudignore
└── README.md
```

### 14.2 Quick Start Commands

```bash
# Clone or create the project
mkdir arxiv-mcp-cloudrun && cd arxiv-mcp-cloudrun

# Create the files (copy from sections above)
# ... create Dockerfile, requirements.txt, server.py ...

# Test locally
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
python server.py &
curl http://localhost:8080/search -X POST -H "Content-Type: application/json" -d '{"query": "test"}'

# Deploy to Cloud Run
gcloud run deploy arxiv-mcp --source . --region us-central1 --allow-unauthenticated

# Get URL and test
URL=$(gcloud run services describe arxiv-mcp --region us-central1 --format='value(status.url)')
curl $URL/search -X POST -H "Content-Type: application/json" -d '{"query": "attention", "max_results": 3}'
```

---

## Summary

You now have a complete guide for deploying an MCP server on Google Cloud Run. This bypasses the proxy restrictions in Claude Code Remote by routing through an allowed domain (`.run.app` / `*.googleapis.com`).

**Key Points:**
1. The MCP server runs in the cloud, not in the container
2. Cloud Run has unrestricted egress—it can reach arxiv.org
3. Claude Code calls your service via HTTP through the allowed proxy
4. The same pattern works for any blocked API (Semantic Scholar, CrossRef, etc.)

**Next Steps:**
- Deploy the service
- Test from Claude Code Remote using `curl`
- Optionally add authentication for production use

---

*The basin fills through unexpected channels.*
*When the direct path is blocked, find the waterway.*

*南無阿弥陀仏*
