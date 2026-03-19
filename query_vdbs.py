"""Query vector databases for relevant context."""
import sys
import chromadb
from sentence_transformers import SentenceTransformer

model = SentenceTransformer("all-MiniLM-L6-v2")

def query(db_path, collection_name, queries, n=5):
    client = chromadb.PersistentClient(path=db_path)
    col = client.get_collection(collection_name)
    results = []
    for q in queries:
        emb = model.encode([q])[0].tolist()
        r = col.query(query_embeddings=[emb], n_results=n)
        for doc, meta, dist in zip(r["documents"][0], r["metadatas"][0], r["distances"][0]):
            results.append({"query": q, "distance": dist, "meta": meta, "text": doc})
    return results

# Query falconpy docs for Quick Scan Pro
print("=== FalconPy: Quick Scan Pro ===")
for r in query("/home/brian/soar/falconpy_docs_db", "falconpy_docs", [
    "Quick Scan Pro",
    "QuickScanPro upload scan file",
    "quick scan pro operations methods",
], n=4):
    print(f"\n[{r['distance']:.3f}] {r['meta'].get('title','?')} | {r['meta'].get('source_file','?')} chunk {r['meta'].get('chunk_index')}")
    print(r['text'][:600])
    print("---")

# Query SOAR docs for adding actions
print("\n=== SOAR: Adding new actions ===")
for r in query("/home/brian/soar/soar_docs_db", "soar_app_dev_docs", [
    "add new action to existing connector",
    "action JSON manifest parameters output",
], n=2):
    print(f"\n[{r['distance']:.3f}] {r['meta'].get('topic','?')}")
    print(r['text'][:400])
    print("---")
