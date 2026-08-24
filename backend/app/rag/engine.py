import os
import re
import math
import json
import logging
from collections import Counter
from typing import List, Dict, Any, Optional
from dataclasses import dataclass

from backend.app.config import settings

logger = logging.getLogger(__name__)

@dataclass
class ChunkResult:
    chunk_id: str
    filename: str
    title: str
    guest: str
    date: str
    post_url: str
    content: str
    score: float

class RAGEngine:
    def __init__(self, transcript_dir: Optional[str] = None):
        self.transcript_dir = transcript_dir or settings.TRANSCRIPT_DIR
        self.chunks: List[Dict[str, Any]] = []
        self.doc_tokens: List[List[str]] = []
        self.df: Counter = Counter()
        self.is_indexed = False

    def parse_markdown_file(self, file_path: str) -> Optional[Dict[str, Any]]:
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                raw_text = f.read()

            metadata = {
                "title": os.path.basename(file_path).replace(".md", "").replace("-", " ").title(),
                "guest": "Unknown",
                "date": "N/A",
                "post_url": "",
                "description": ""
            }

            body = raw_text
            # Parse YAML frontmatter if present
            if raw_text.startswith("---"):
                parts = raw_text.split("---", 2)
                if len(parts) >= 3:
                    frontmatter_lines = parts[1].strip().split("\n")
                    for line in frontmatter_lines:
                        if ":" in line:
                            k, v = line.split(":", 1)
                            k = k.strip().lower()
                            v = v.strip().strip('"').strip("'")
                            if k in metadata:
                                metadata[k] = v
                    body = parts[2].strip()

            return {
                "filename": os.path.basename(file_path),
                "metadata": metadata,
                "body": body
            }
        except Exception as e:
            logger.error(f"Error parsing {file_path}: {e}")
            return None

    def create_chunks(self, document: Dict[str, Any], chunk_size: int = 700, overlap: int = 150) -> List[Dict[str, Any]]:
        doc_chunks = []
        body = document["body"]
        filename = document["filename"]
        metadata = document["metadata"]

        paragraphs = re.split(r'\n\s*\n', body)
        current_chunk = ""
        chunk_idx = 0

        for para in paragraphs:
            para = para.strip()
            if not para:
                continue

            if len(current_chunk) + len(para) <= chunk_size:
                current_chunk += "\n\n" + para if current_chunk else para
            else:
                if current_chunk:
                    doc_chunks.append({
                        "chunk_id": f"{filename}_{chunk_idx}",
                        "filename": filename,
                        "title": metadata.get("title", filename),
                        "guest": metadata.get("guest", "Lenny's Guest"),
                        "date": metadata.get("date", "N/A"),
                        "post_url": metadata.get("post_url", ""),
                        "content": current_chunk.strip()
                    })
                    chunk_idx += 1
                if len(para) > chunk_size:
                    for i in range(0, len(para), chunk_size - overlap):
                        sub_para = para[i:i + chunk_size]
                        doc_chunks.append({
                            "chunk_id": f"{filename}_{chunk_idx}",
                            "filename": filename,
                            "title": metadata.get("title", filename),
                            "guest": metadata.get("guest", "Lenny's Guest"),
                            "date": metadata.get("date", "N/A"),
                            "post_url": metadata.get("post_url", ""),
                            "content": sub_para.strip()
                        })
                        chunk_idx += 1
                    current_chunk = ""
                else:
                    current_chunk = para

        if current_chunk:
            doc_chunks.append({
                "chunk_id": f"{filename}_{chunk_idx}",
                "filename": filename,
                "title": metadata.get("title", filename),
                "guest": metadata.get("guest", "Lenny's Guest"),
                "date": metadata.get("date", "N/A"),
                "post_url": metadata.get("post_url", ""),
                "content": current_chunk.strip()
            })

        return doc_chunks

    def tokenize(self, text: str) -> List[str]:
        return re.findall(r'\w+', text.lower())

    def build_index(self) -> int:
        if self.is_indexed and self.chunks:
            return len(self.chunks)

        if not os.path.exists(self.transcript_dir):
            os.makedirs(self.transcript_dir, exist_ok=True)
            logger.warning(f"Transcript directory {self.transcript_dir} was empty.")
            return 0

        files = [f for f in os.listdir(self.transcript_dir) if f.endswith(".md")]
        if not files:
            logger.warning(f"No markdown files found in {self.transcript_dir}")
            return 0

        self.chunks = []
        for fname in files:
            full_path = os.path.join(self.transcript_dir, fname)
            parsed = self.parse_markdown_file(full_path)
            if parsed:
                file_chunks = self.create_chunks(parsed)
                self.chunks.extend(file_chunks)

        if not self.chunks:
            logger.warning("No chunks generated from transcripts.")
            return 0

        # Build pure Python TF-IDF term statistics
        self.doc_tokens = [self.tokenize(c["content"]) for c in self.chunks]
        self.df = Counter()
        for tokens in self.doc_tokens:
            for term in set(tokens):
                self.df[term] += 1

        self.is_indexed = True
        logger.info(f"Indexed {len(self.chunks)} transcript chunks across {len(files)} files.")
        return len(self.chunks)

    def search(self, query: str, top_k: int = 5) -> List[ChunkResult]:
        if not self.is_indexed or not self.chunks:
            self.build_index()

        if not self.chunks:
            return []

        query_tokens = self.tokenize(query)
        if not query_tokens:
            return []

        q_tf = Counter(query_tokens)
        N = len(self.chunks)

        scores = []
        for idx, d_tokens in enumerate(self.doc_tokens):
            d_tf = Counter(d_tokens)
            dot_product = 0.0
            q_norm = 0.0
            d_norm = 0.0

            for term, q_count in q_tf.items():
                if term in self.df:
                    idf = math.log((N + 1) / (self.df[term] + 1)) + 1.0
                    q_val = q_count * idf
                    d_val = d_tf.get(term, 0) * idf
                    dot_product += q_val * d_val
                    q_norm += q_val ** 2

            for term, d_count in d_tf.items():
                if term in self.df:
                    idf = math.log((N + 1) / (self.df[term] + 1)) + 1.0
                    d_norm += (d_count * idf) ** 2

            q_norm = math.sqrt(q_norm)
            d_norm = math.sqrt(d_norm)

            score = (dot_product / (q_norm * d_norm)) if (q_norm > 0 and d_norm > 0) else 0.0
            scores.append((score, idx))

        scores.sort(key=lambda x: x[0], reverse=True)
        results = []

        for score, idx in scores[:top_k]:
            if score > 0.01:
                item = self.chunks[idx]
                results.append(ChunkResult(
                    chunk_id=item["chunk_id"],
                    filename=item["filename"],
                    title=item["title"],
                    guest=item["guest"],
                    date=item["date"],
                    post_url=item["post_url"],
                    content=item["content"],
                    score=round(score, 3)
                ))

        return results

rag_engine = RAGEngine()
