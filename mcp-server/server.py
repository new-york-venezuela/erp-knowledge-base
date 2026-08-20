"""
mcp-server/server.py — MCP server exposing Profit Plus RAG tools to Claude Code.

Tools:
  search_profit_docs(query)        Semantic search over /docs
  get_table_schema(table_name)     Return full Markdown doc for a table
  get_sql_recipe(intent)           Find pre-written SQL recipes by intent

Transport: streamable HTTP (not stdio). Start the server, then point Claude
Code at the printed URL.

Start:
    python mcp-server/server.py

Env vars:
    MCP_HOST   Bind host (default 127.0.0.1)
    MCP_PORT   Bind port (default 8000)
    MCP_PATH   HTTP path for the MCP endpoint (default /mcp)

Register with Claude Code (claude_desktop_config.json / .claude/settings.json):
    {
      "mcpServers": {
        "profit-rag": {
          "url": "http://127.0.0.1:8000/mcp"
        }
      }
    }

Or via the CLI:
    claude mcp add --transport http profit-rag http://127.0.0.1:8000/mcp
"""

import os
import sys
from pathlib import Path

# Resolve project root (parent of mcp-server/)
_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(_ROOT))


def _load_dotenv() -> None:
    try:
        from dotenv import load_dotenv
        for name in (".env.local", ".env"):
            p = _ROOT / name
            if p.exists():
                load_dotenv(p)
                break
    except ImportError:
        pass


_load_dotenv()

QDRANT_URL = os.environ.get("QDRANT_URL", "http://localhost:6333")
COLLECTION = os.environ.get("COLLECTION_NAME", "profit_docs")
DOCS_DIR = Path(os.environ.get("DOCS_DIR", str(_ROOT / "docs")))
EMBED_MODEL = os.environ.get("EMBED_MODEL", "jinaai/jina-embeddings-v2-base-es")

MCP_HOST = os.environ.get("MCP_HOST", "127.0.0.1")
MCP_PORT = int(os.environ.get("MCP_PORT", "8000"))
MCP_PATH = os.environ.get("MCP_PATH", "/mcp")

try:
    from mcp.server.mcpserver import MCPServer
except ImportError:
    sys.exit("mcp not installed or too old (need mcp>=2.0 for MCPServer). Run: pip install -U mcp")

try:
    from fastembed import TextEmbedding
except ImportError:
    sys.exit("fastembed not installed. Run: pip install fastembed")

try:
    from qdrant_client import QdrantClient
except ImportError:
    sys.exit("qdrant-client not installed. Run: pip install qdrant-client")


# ── Lazy singletons ──────────────────────────────────────────────────────────

_embedder: "TextEmbedding | None" = None
_qdrant: "QdrantClient | None" = None


def _get_embedder() -> "TextEmbedding":
    global _embedder
    if _embedder is None:
        _embedder = TextEmbedding(model_name=EMBED_MODEL)
    return _embedder


def _get_qdrant() -> "QdrantClient":
    global _qdrant
    if _qdrant is None:
        _qdrant = QdrantClient(url=QDRANT_URL)
    return _qdrant


# ── MCP server setup ─────────────────────────────────────────────────────────

app = MCPServer("profit-rag")


def _embed(text: str) -> list[float]:
    return list(_get_embedder().embed([text]))[0].tolist()


@app.tool(
    description=(
        "Semantic search over Profit Plus 2k12 documentation (tables, "
        "stored procedures, triggers, workflows). Use for general questions "
        "about schema, business logic, or module behavior."
    )
)
def search_profit_docs(query: str, limit: int = 5) -> str:
    """Semantic search over indexed Profit Plus documentation."""
    vector = _embed(query)
    response = _get_qdrant().query_points(
        collection_name=COLLECTION,
        query=vector,
        limit=limit,
        with_payload=True,
    )
    hits = response.points
    if not hits:
        return "No results found."

    parts: list[str] = []
    for hit in hits:
        payload = hit.payload or {}
        score = round(hit.score, 3)
        path = payload.get("path", "")
        text = payload.get("text", "")
        parts.append(f"**[score={score}] {path}**\n{text}")
    return "\n\n---\n\n".join(parts)


@app.tool(
    description=(
        "Return the full schema documentation for a specific Profit Plus table, "
        "including columns, triggers, stored procedures, and SQL recipes."
    )
)
def get_table_schema(table_name: str) -> str:
    """Return the full Markdown documentation for a specific table."""
    # Try exact match first
    candidates = [
        DOCS_DIR / "tables" / f"{table_name}.md",
        DOCS_DIR / "tables" / f"{table_name.lower()}.md",
    ]
    for path in candidates:
        if path.exists():
            return path.read_text(encoding="utf-8")

    # Fall back to semantic search
    return search_profit_docs(f"tabla {table_name} schema columns", limit=3)


@app.tool(
    description=(
        "Find pre-built SQL queries for common Profit Plus reporting tasks: "
        "retenciones, libros de ventas/compras, cuentas por cobrar, saldos USD, inventario."
    )
)
def get_sql_recipe(intent: str) -> str:
    """Find pre-written SQL recipes matching a business intent."""
    query = f"SQL recipe query {intent} recetario"
    vector = _embed(query)
    response = _get_qdrant().query_points(
        collection_name=COLLECTION,
        query=vector,
        limit=8,
        with_payload=True,
    )

    sql_parts: list[str] = []
    for hit in response.points:
        text = (hit.payload or {}).get("text", "")
        # Extract SQL blocks
        if "```sql" in text.lower():
            sql_parts.append(f"[from {(hit.payload or {}).get('path', '')}]\n{text}")

    if sql_parts:
        return "\n\n---\n\n".join(sql_parts[:4])
    return search_profit_docs(intent, limit=4)


if __name__ == "__main__":
    url = f"http://{MCP_HOST}:{MCP_PORT}{MCP_PATH}"
    print(f"Starting profit-rag MCP server (streamable HTTP)...")
    print(f"Connect Claude Code with:")
    print(f"  claude mcp add --transport http profit-rag {url}")
    print(f"URI: {url}")
    app.run(transport="streamable-http", host=MCP_HOST, port=MCP_PORT, streamable_http_path=MCP_PATH)
