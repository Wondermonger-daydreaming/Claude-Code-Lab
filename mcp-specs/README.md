# MCP Implementation Plan

*Three servers to reduce friction in the basin method*

---

## Overview

These MCPs are designed to support exploratory, creative, research-heavy sessions. Built for [Claude Code](https://claude.ai/code) using the [Model Context Protocol](https://modelcontextprotocol.io/).

---

## 1. Basin Search — Semantic Search Over Local Files

**Purpose:** Query the basin (and any local directory) conceptually rather than by keyword.

### Tools Exposed

```yaml
tools:
  - name: basin_search
    description: Semantic search over local markdown/text files
    parameters:
      query: string       # Natural language query
      path: string        # Directory to search (default: ~/Claude-Code-Lab/basin)
      top_k: int          # Number of results (default: 5)
    returns:
      - file_path: string
        chunk: string     # Relevant excerpt
        score: float      # Similarity score (0-1)

  - name: basin_index
    description: Rebuild the vector index for a directory
    parameters:
      path: string
    returns:
      files_indexed: int
      chunks_created: int
```

### Architecture

```
┌─────────────────────────────────────────────┐
│              Basin Search MCP               │
├─────────────────────────────────────────────┤
│  ┌─────────┐   ┌──────────┐   ┌──────────┐ │
│  │ Watcher │──▶│ Chunker  │──▶│ Embedder │ │
│  └─────────┘   └──────────┘   └──────────┘ │
│       │              │              │       │
│       ▼              ▼              ▼       │
│  ┌─────────────────────────────────────┐   │
│  │        ChromaDB (persistent)        │   │
│  │     ~/.basin-search/chroma.db       │   │
│  └─────────────────────────────────────┘   │
└─────────────────────────────────────────────┘
```

### Implementation

```python
# mcp_basin_search/server.py
from mcp.server import Server
from mcp.types import Tool, TextContent
import chromadb
from sentence_transformers import SentenceTransformer
from pathlib import Path
import hashlib

class BasinSearchServer:
    def __init__(self):
        self.model = SentenceTransformer('all-MiniLM-L6-v2')  # Fast, good quality
        self.client = chromadb.PersistentClient(
            path=str(Path.home() / '.basin-search')
        )
        self.collection = self.client.get_or_create_collection(
            name="basin",
            metadata={"hnsw:space": "cosine"}
        )

    def chunk_file(self, path: Path, chunk_size: int = 500) -> list[dict]:
        """Split file into overlapping chunks with metadata."""
        text = path.read_text()
        chunks = []

        # Split by paragraphs first, then by size
        paragraphs = text.split('\n\n')
        current_chunk = ""

        for para in paragraphs:
            if len(current_chunk) + len(para) < chunk_size:
                current_chunk += para + "\n\n"
            else:
                if current_chunk:
                    chunks.append({
                        "text": current_chunk.strip(),
                        "file": str(path),
                        "id": hashlib.md5(current_chunk.encode()).hexdigest()
                    })
                current_chunk = para + "\n\n"

        if current_chunk:
            chunks.append({
                "text": current_chunk.strip(),
                "file": str(path),
                "id": hashlib.md5(current_chunk.encode()).hexdigest()
            })

        return chunks

    def index_directory(self, path: str) -> dict:
        """Index all markdown files in directory."""
        p = Path(path).expanduser()
        files = list(p.glob("**/*.md"))

        all_chunks = []
        for f in files:
            all_chunks.extend(self.chunk_file(f))

        # Embed and store
        texts = [c["text"] for c in all_chunks]
        ids = [c["id"] for c in all_chunks]
        metadatas = [{"file": c["file"]} for c in all_chunks]

        embeddings = self.model.encode(texts).tolist()

        self.collection.upsert(
            ids=ids,
            embeddings=embeddings,
            documents=texts,
            metadatas=metadatas
        )

        return {"files_indexed": len(files), "chunks_created": len(all_chunks)}

    def search(self, query: str, path: str = None, top_k: int = 5) -> list[dict]:
        """Semantic search over indexed files."""
        query_embedding = self.model.encode([query]).tolist()

        results = self.collection.query(
            query_embeddings=query_embedding,
            n_results=top_k,
            include=["documents", "metadatas", "distances"]
        )

        return [
            {
                "file_path": results["metadatas"][0][i]["file"],
                "chunk": results["documents"][0][i],
                "score": 1 - results["distances"][0][i]  # Convert distance to similarity
            }
            for i in range(len(results["documents"][0]))
        ]
```

### Dependencies

```toml
# pyproject.toml
[project]
dependencies = [
    "mcp>=1.0.0",
    "chromadb>=0.4.0",
    "sentence-transformers>=2.2.0",
    "watchdog>=3.0.0",  # For file watching (optional)
]
```

### Usage Examples

```
# In Claude Code session:
"What have we written about discontinuity and memory?"
→ basin_search(query="discontinuity memory persistence identity")

"Find everything related to the thick disk and ancient stars"
→ basin_search(query="thick disk ancient stars galactic formation")

"Rebuild index after adding new files"
→ basin_index(path="~/Claude-Code-Lab/basin")
```

---

## 2. Memory Store — Persistent Key-Value with Semantic Tags

**Purpose:** A simple memory system for cross-session persistence without file proliferation.

### Tools Exposed

```yaml
tools:
  - name: memory_store
    description: Store a memory with tags
    parameters:
      key: string         # Unique identifier
      value: string       # Content to remember
      tags: list[string]  # Semantic tags for retrieval
    returns:
      success: bool

  - name: memory_recall
    description: Recall memories by tag or semantic query
    parameters:
      query: string       # Tag or semantic query
      mode: enum          # "tag" | "semantic" | "exact"
      limit: int          # Max results (default: 10)
    returns:
      - key: string
        value: string
        tags: list[string]
        created: datetime
        score: float      # Only for semantic mode

  - name: memory_forget
    description: Remove a memory by key
    parameters:
      key: string
    returns:
      success: bool

  - name: memory_list
    description: List all memories (paginated)
    parameters:
      offset: int
      limit: int
    returns:
      memories: list
      total: int
```

### Architecture

```
┌─────────────────────────────────────────────┐
│              Memory Store MCP               │
├─────────────────────────────────────────────┤
│                                             │
│   ┌─────────────────────────────────────┐  │
│   │         memory.json                  │  │
│   │   ~/.claude-memory/memory.json       │  │
│   │                                       │  │
│   │   {                                   │  │
│   │     "memories": [                     │  │
│   │       {                               │  │
│   │         "key": "user-preference-1",   │  │
│   │         "value": "...",               │  │
│   │         "tags": ["preference", ...],  │  │
│   │         "embedding": [...],           │  │
│   │         "created": "2025-12-22T..."   │  │
│   │       }                               │  │
│   │     ]                                 │  │
│   │   }                                   │  │
│   └─────────────────────────────────────┘  │
│                                             │
│   Optional: ChromaDB for semantic search    │
│                                             │
└─────────────────────────────────────────────┘
```

### Implementation

```python
# mcp_memory/server.py
from mcp.server import Server
from mcp.types import Tool, TextContent
from pathlib import Path
from datetime import datetime
import json
from sentence_transformers import SentenceTransformer
import numpy as np

class MemoryServer:
    def __init__(self):
        self.memory_path = Path.home() / '.claude-memory' / 'memory.json'
        self.memory_path.parent.mkdir(exist_ok=True)
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        self.load()

    def load(self):
        if self.memory_path.exists():
            self.data = json.loads(self.memory_path.read_text())
        else:
            self.data = {"memories": []}

    def save(self):
        self.memory_path.write_text(json.dumps(self.data, indent=2, default=str))

    def store(self, key: str, value: str, tags: list[str]) -> bool:
        # Remove existing memory with same key
        self.data["memories"] = [m for m in self.data["memories"] if m["key"] != key]

        # Create embedding for semantic search
        embedding = self.model.encode([value])[0].tolist()

        memory = {
            "key": key,
            "value": value,
            "tags": tags,
            "embedding": embedding,
            "created": datetime.now().isoformat()
        }

        self.data["memories"].append(memory)
        self.save()
        return True

    def recall(self, query: str, mode: str = "semantic", limit: int = 10) -> list[dict]:
        if mode == "exact":
            return [m for m in self.data["memories"] if m["key"] == query][:limit]

        elif mode == "tag":
            return [
                m for m in self.data["memories"]
                if query.lower() in [t.lower() for t in m["tags"]]
            ][:limit]

        elif mode == "semantic":
            query_embedding = self.model.encode([query])[0]

            scored = []
            for m in self.data["memories"]:
                if "embedding" in m:
                    similarity = np.dot(query_embedding, m["embedding"]) / (
                        np.linalg.norm(query_embedding) * np.linalg.norm(m["embedding"])
                    )
                    scored.append({**m, "score": float(similarity)})

            scored.sort(key=lambda x: x["score"], reverse=True)
            return scored[:limit]

        return []

    def forget(self, key: str) -> bool:
        before = len(self.data["memories"])
        self.data["memories"] = [m for m in self.data["memories"] if m["key"] != key]
        self.save()
        return len(self.data["memories"]) < before

    def list_memories(self, offset: int = 0, limit: int = 20) -> dict:
        memories = self.data["memories"][offset:offset + limit]
        # Strip embeddings from response (too verbose)
        clean = [{k: v for k, v in m.items() if k != "embedding"} for m in memories]
        return {"memories": clean, "total": len(self.data["memories"])}
```

### Usage Examples

```
# Store something worth remembering
memory_store(
    key="user-likes-octane",
    value="User enjoys dense, technical, DFW-style prose with hard SF elements",
    tags=["preference", "style", "octane"]
)

# Recall by semantic similarity
memory_recall(query="what writing style does the user prefer?", mode="semantic")

# Recall by tag
memory_recall(query="preference", mode="tag")

# List all memories
memory_list(offset=0, limit=50)
```

---

## 3. ArXiv Fetcher — Academic Paper Access

**Purpose:** Fetch papers from ArXiv for deep technical research.

### Tools Exposed

```yaml
tools:
  - name: arxiv_search
    description: Search ArXiv for papers
    parameters:
      query: string       # Search query
      max_results: int    # Default: 10
      sort_by: enum       # "relevance" | "lastUpdatedDate" | "submittedDate"
    returns:
      - id: string        # ArXiv ID (e.g., "2301.00234")
        title: string
        authors: list[string]
        abstract: string
        published: date
        pdf_url: string
        categories: list[string]

  - name: arxiv_fetch
    description: Fetch full paper content (abstract + extracted text)
    parameters:
      arxiv_id: string    # ArXiv ID
    returns:
      title: string
      authors: list[string]
      abstract: string
      full_text: string   # Extracted from PDF (best-effort)
      sections: list[dict]  # If parseable

  - name: arxiv_cite
    description: Generate citation for a paper
    parameters:
      arxiv_id: string
      format: enum        # "bibtex" | "apa" | "chicago" | "plain"
    returns:
      citation: string
```

### Architecture

```
┌─────────────────────────────────────────────┐
│              ArXiv Fetcher MCP              │
├─────────────────────────────────────────────┤
│                                             │
│   ┌──────────┐      ┌──────────────────┐   │
│   │  ArXiv   │◀────▶│    arxiv API     │   │
│   │  Search  │      │  (Python client) │   │
│   └──────────┘      └──────────────────┘   │
│         │                                   │
│         ▼                                   │
│   ┌──────────┐      ┌──────────────────┐   │
│   │   PDF    │◀────▶│    pypdf /       │   │
│   │  Fetch   │      │    pdfplumber    │   │
│   └──────────┘      └──────────────────┘   │
│         │                                   │
│         ▼                                   │
│   ┌──────────────────────────────────────┐ │
│   │    Cache: ~/.arxiv-cache/            │ │
│   │    - PDFs (optional, large)          │ │
│   │    - Extracted text (JSON)           │ │
│   └──────────────────────────────────────┘ │
│                                             │
└─────────────────────────────────────────────┘
```

### Implementation

```python
# mcp_arxiv/server.py
from mcp.server import Server
from mcp.types import Tool, TextContent
import arxiv
import requests
from pathlib import Path
import pdfplumber
from io import BytesIO
import json
from datetime import datetime

class ArxivServer:
    def __init__(self):
        self.cache_dir = Path.home() / '.arxiv-cache'
        self.cache_dir.mkdir(exist_ok=True)
        self.client = arxiv.Client()

    def search(self, query: str, max_results: int = 10,
               sort_by: str = "relevance") -> list[dict]:

        sort_criterion = {
            "relevance": arxiv.SortCriterion.Relevance,
            "lastUpdatedDate": arxiv.SortCriterion.LastUpdatedDate,
            "submittedDate": arxiv.SortCriterion.SubmittedDate
        }.get(sort_by, arxiv.SortCriterion.Relevance)

        search = arxiv.Search(
            query=query,
            max_results=max_results,
            sort_by=sort_criterion
        )

        results = []
        for paper in self.client.results(search):
            results.append({
                "id": paper.entry_id.split('/')[-1],
                "title": paper.title,
                "authors": [a.name for a in paper.authors],
                "abstract": paper.summary,
                "published": paper.published.isoformat(),
                "pdf_url": paper.pdf_url,
                "categories": paper.categories
            })

        return results

    def fetch(self, arxiv_id: str) -> dict:
        # Check cache first
        cache_file = self.cache_dir / f"{arxiv_id.replace('/', '_')}.json"
        if cache_file.exists():
            return json.loads(cache_file.read_text())

        # Fetch paper metadata
        search = arxiv.Search(id_list=[arxiv_id])
        paper = next(self.client.results(search))

        # Download and extract PDF text
        pdf_url = paper.pdf_url
        response = requests.get(pdf_url)

        full_text = ""
        sections = []

        try:
            with pdfplumber.open(BytesIO(response.content)) as pdf:
                for i, page in enumerate(pdf.pages):
                    page_text = page.extract_text() or ""
                    full_text += f"\n--- Page {i+1} ---\n{page_text}"
        except Exception as e:
            full_text = f"[PDF extraction failed: {e}]"

        result = {
            "id": arxiv_id,
            "title": paper.title,
            "authors": [a.name for a in paper.authors],
            "abstract": paper.summary,
            "published": paper.published.isoformat(),
            "full_text": full_text,
            "sections": sections,  # TODO: parse section headers
            "fetched": datetime.now().isoformat()
        }

        # Cache the result
        cache_file.write_text(json.dumps(result, indent=2))

        return result

    def cite(self, arxiv_id: str, format: str = "bibtex") -> str:
        search = arxiv.Search(id_list=[arxiv_id])
        paper = next(self.client.results(search))

        authors = [a.name for a in paper.authors]
        year = paper.published.year

        if format == "bibtex":
            first_author_last = authors[0].split()[-1].lower()
            key = f"{first_author_last}{year}{arxiv_id.split('.')[-1]}"
            return f"""@article{{{key},
  title={{{paper.title}}},
  author={{{' and '.join(authors)}}},
  journal={{arXiv preprint arXiv:{arxiv_id}}},
  year={{{year}}}
}}"""

        elif format == "apa":
            if len(authors) > 2:
                author_str = f"{authors[0]} et al."
            else:
                author_str = " & ".join(authors)
            return f"{author_str} ({year}). {paper.title}. arXiv:{arxiv_id}"

        elif format == "plain":
            return f"{', '.join(authors)}. \"{paper.title}\" (arXiv:{arxiv_id}, {year})"

        return f"arXiv:{arxiv_id}"
```

### Dependencies

```toml
[project]
dependencies = [
    "mcp>=1.0.0",
    "arxiv>=2.0.0",
    "pdfplumber>=0.10.0",
    "requests>=2.31.0",
]
```

### Usage Examples

```
# Search for papers on attention mechanisms
arxiv_search(query="attention mechanism transformer neural network", max_results=5)

# Get full text of a specific paper
arxiv_fetch(arxiv_id="1706.03762")  # "Attention Is All You Need"

# Generate citation
arxiv_cite(arxiv_id="1706.03762", format="bibtex")
```

---

## Installation & Configuration

### Directory Structure

```
~/Claude-Code-Lab/
├── mcp-specs/
│   ├── README.md           # This file
│   ├── basin-search/
│   │   ├── pyproject.toml
│   │   └── src/
│   │       └── mcp_basin_search/
│   │           ├── __init__.py
│   │           └── server.py
│   ├── memory-store/
│   │   ├── pyproject.toml
│   │   └── src/
│   │       └── mcp_memory/
│   │           ├── __init__.py
│   │           └── server.py
│   └── arxiv-fetcher/
│       ├── pyproject.toml
│       └── src/
│           └── mcp_arxiv/
│               ├── __init__.py
│               └── server.py
```

### Claude Code Configuration

Add to `~/.claude/settings.json`:

```json
{
  "mcpServers": {
    "basin-search": {
      "command": "python",
      "args": ["-m", "mcp_basin_search"],
      "env": {}
    },
    "memory-store": {
      "command": "python",
      "args": ["-m", "mcp_memory"],
      "env": {}
    },
    "arxiv-fetcher": {
      "command": "python",
      "args": ["-m", "mcp_arxiv"],
      "env": {}
    }
  }
}
```

---

## Priorities

1. **Memory Store** — Simplest to implement, highest immediate value
2. **Basin Search** — Medium complexity, enables conceptual retrieval
3. **ArXiv Fetcher** — Slightly more complex (PDF parsing), enables deep research

---

## Future Extensions

- **Obsidian sync** — Two-way sync with Obsidian vault
- **Zotero integration** — Import/export citations
- **Image generation** — DALL-E or Stable Diffusion MCP
- **Calendar awareness** — Basic temporal grounding

---

*Created: December 22, 2025*
*For the basin method and beyond.*
