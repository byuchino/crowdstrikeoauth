"""
Build ChromaDB vector database from FalconPy HTML documentation.
"""
import os
import sys
import re
from pathlib import Path

# Add the crowdstrikeoauth directory to path for vectordb_registry import
sys.path.insert(0, "/home/brian/soar/crowdstrikeoauth")

from bs4 import BeautifulSoup
import chromadb
from sentence_transformers import SentenceTransformer
from vectordb_registry import register_vdb, init_registry

DOCS_DIR = Path("/home/brian/test/falconpy_docs")
CHROMA_PATH = "/home/brian/soar/falconpy_docs_db"
COLLECTION_NAME = "falconpy_docs"
MODEL_NAME = "all-MiniLM-L6-v2"
CHUNK_SIZE = 4000   # ~1000 tokens
CHUNK_OVERLAP = 200
BATCH_SIZE = 100


def infer_category(filename: str) -> str:
    if filename.startswith("Service-Collections__"):
        return "Service Collection"
    if filename.startswith("Usage__"):
        return "Usage"
    if filename in ("All-Operations.html", "index.html"):
        return "Reference"
    return "API Reference"


def infer_service(filename: str) -> str:
    name = filename.replace(".html", "")
    if name.startswith("Service-Collections__"):
        name = name[len("Service-Collections__"):]
    elif name.startswith("Usage__"):
        name = name[len("Usage__"):]
    return name


def extract_content(html_path: Path) -> dict | None:
    try:
        html = html_path.read_text(encoding="utf-8", errors="replace")
    except Exception as e:
        print(f"  [WARN] Could not read {html_path.name}: {e}")
        return None

    soup = BeautifulSoup(html, "html.parser")

    # Remove nav, scripts, styles, headers, footers
    for tag in soup.find_all(["nav", "script", "style", "header", "footer",
                               "aside", "noscript"]):
        tag.decompose()

    # Extract title
    title = ""
    title_tag = soup.find("title")
    if title_tag:
        title = title_tag.get_text(strip=True)
    if not title:
        h1 = soup.find("h1")
        if h1:
            title = h1.get_text(strip=True)
    if not title:
        title = html_path.stem

    # Try to find main content area
    main = (soup.find("main") or
            soup.find("article") or
            soup.find("div", {"role": "main"}) or
            soup.find("div", class_=re.compile(r"content|main|body|article", re.I)) or
            soup.find("body") or
            soup)

    text = main.get_text(separator="\n", strip=True)

    # Collapse excessive whitespace
    text = re.sub(r"\n{3,}", "\n\n", text)
    text = re.sub(r" {2,}", " ", text)
    text = text.strip()

    if not text:
        return None

    return {"title": title, "text": text}


def chunk_text(text: str, chunk_size: int = CHUNK_SIZE, overlap: int = CHUNK_OVERLAP) -> list[str]:
    if len(text) <= chunk_size:
        return [text]
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end]
        chunks.append(chunk)
        if end >= len(text):
            break
        start = end - overlap
    return chunks


def main():
    print(f"Loading SentenceTransformer model: {MODEL_NAME}")
    model = SentenceTransformer(MODEL_NAME)

    print(f"Connecting to ChromaDB at: {CHROMA_PATH}")
    client = chromadb.PersistentClient(path=CHROMA_PATH)
    collection = client.get_or_create_collection(
        name=COLLECTION_NAME,
        metadata={"hnsw:space": "cosine"}
    )

    html_files = sorted(DOCS_DIR.glob("*.html"))
    print(f"Found {len(html_files)} HTML files\n")

    all_ids = []
    all_embeddings = []
    all_documents = []
    all_metadatas = []

    doc_ids_and_topics = []  # one per source file
    skipped = 0

    for i, html_path in enumerate(html_files):
        filename = html_path.name
        category = infer_category(filename)
        service = infer_service(filename)

        result = extract_content(html_path)
        if result is None:
            print(f"  [SKIP] {filename} — empty content")
            skipped += 1
            continue

        title = result["title"]
        text = result["text"]
        chunks = chunk_text(text)

        total_chunks = len(chunks)

        # Register this source file
        doc_ids_and_topics.append({
            "id": filename,
            "topic": title,
            "source_url": f"https://falconpy.io/{filename}"
        })

        for chunk_idx, chunk in enumerate(chunks):
            doc_id = f"{filename}__chunk_{chunk_idx}"
            embedding = model.encode(chunk).tolist()

            all_ids.append(doc_id)
            all_embeddings.append(embedding)
            all_documents.append(chunk)
            all_metadatas.append({
                "title": title,
                "category": category,
                "service": service,
                "source_file": filename,
                "chunk_index": chunk_idx,
                "total_chunks": total_chunks,
            })

        if (i + 1) % 50 == 0:
            print(f"  Processed {i + 1}/{len(html_files)} files, "
                  f"{len(all_ids)} chunks so far...")

    print(f"\nUpserting {len(all_ids)} chunks in batches of {BATCH_SIZE}...")

    for batch_start in range(0, len(all_ids), BATCH_SIZE):
        batch_end = batch_start + BATCH_SIZE
        collection.upsert(
            ids=all_ids[batch_start:batch_end],
            embeddings=all_embeddings[batch_start:batch_end],
            documents=all_documents[batch_start:batch_end],
            metadatas=all_metadatas[batch_start:batch_end],
        )
        print(f"  Upserted batch {batch_start // BATCH_SIZE + 1} "
              f"({min(batch_end, len(all_ids))}/{len(all_ids)})")

    total_in_collection = collection.count()
    print(f"\nTotal chunks in collection: {total_in_collection}")
    print(f"Source files processed: {len(doc_ids_and_topics)} (skipped: {skipped})")

    # Register in registry
    print("\nRegistering VDB in registry...")
    init_registry()
    register_vdb(
        name="falconpy_docs",
        path=CHROMA_PATH,
        description="FalconPy Python SDK documentation for the CrowdStrike Falcon API",
        model=MODEL_NAME,
        collection=COLLECTION_NAME,
        tags=["falconpy", "crowdstrike", "falcon", "sdk", "python", "api"],
        doc_ids_and_topics=doc_ids_and_topics,
    )

    # Sanity check query
    print("\n--- Sanity Check Query ---")
    query = "how to authenticate with OAuth2"
    print(f"Query: '{query}'")
    query_embedding = model.encode(query).tolist()
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=3,
        include=["documents", "metadatas", "distances"]
    )

    for rank, (doc, meta, dist) in enumerate(zip(
            results["documents"][0],
            results["metadatas"][0],
            results["distances"][0]), start=1):
        print(f"\n  Result #{rank}")
        print(f"    Title:    {meta['title']}")
        print(f"    Category: {meta['category']}")
        print(f"    Service:  {meta['service']}")
        print(f"    File:     {meta['source_file']} (chunk {meta['chunk_index']}/{meta['total_chunks']})")
        print(f"    Distance: {dist:.4f}")
        print(f"    Snippet:  {doc[:200].replace(chr(10), ' ')}...")

    print("\nDone.")


if __name__ == "__main__":
    main()
