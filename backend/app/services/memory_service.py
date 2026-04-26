"""
MindOS AI - Memory Service
Pinecone vector database for long-term conversational memory (RAG).
Falls back to in-memory store when Pinecone is not configured.
"""

import logging
import time
from typing import Optional, List, Dict
from datetime import datetime

logger = logging.getLogger(__name__)


class MemoryService:
    """Vector memory for persistent semantic conversation recall."""

    def __init__(self, pinecone_key="", openai_key="",
                 index_name="mindos-memory", embed_model="text-embedding-3-small",
                 dims=1536):
        self.index = None
        self.openai_client = None
        self.embed_model = embed_model
        self._pc_ok = False
        self._oai_ok = False
        self._store: Dict[str, List[dict]] = {}

        if openai_key:
            try:
                from openai import AsyncOpenAI
                self.openai_client = AsyncOpenAI(api_key=openai_key)
                self._oai_ok = True
            except Exception as e:
                logger.warning(f"Memory OpenAI init failed: {e}")

        if pinecone_key and self._oai_ok:
            try:
                from pinecone import Pinecone, ServerlessSpec
                pc = Pinecone(api_key=pinecone_key)
                existing = [i.name for i in pc.list_indexes()]
                if index_name not in existing:
                    pc.create_index(name=index_name, dimension=dims,
                                    metric="cosine",
                                    spec=ServerlessSpec(cloud="aws", region="us-east-1"))
                self.index = pc.Index(index_name)
                self._pc_ok = True
                logger.info(f"Memory: Pinecone index '{index_name}' ready")
            except Exception as e:
                logger.warning(f"Pinecone init failed: {e}")

        if not self._pc_ok:
            logger.info("Memory: using in-memory fallback")

    @property
    def is_available(self):
        return self._pc_ok

    async def _embed(self, text: str):
        if not self._oai_ok:
            return None
        try:
            r = await self.openai_client.embeddings.create(input=text, model=self.embed_model)
            return r.data[0].embedding
        except Exception as e:
            logger.error(f"Embed failed: {e}")
            return None

    async def store_memory(self, user_id, text, emotion="neutral", session_id="", metadata=None):
        mid = f"{user_id}_{int(time.time()*1000)}"
        meta = {"user_id": user_id, "text": text[:1000], "emotion": emotion,
                "session_id": session_id, "timestamp": datetime.utcnow().isoformat(),
                **(metadata or {})}

        if self._pc_ok:
            try:
                emb = await self._embed(text)
                if emb:
                    self.index.upsert(vectors=[(mid, emb, meta)])
                    return True
            except Exception as e:
                logger.error(f"Pinecone upsert failed: {e}")

        if user_id not in self._store:
            self._store[user_id] = []
        self._store[user_id].append({"id": mid, "text": text, **meta})
        self._store[user_id] = self._store[user_id][-100:]
        return True

    async def recall_memories(self, user_id, query, top_k=5):
        if self._pc_ok:
            try:
                emb = await self._embed(query)
                if emb:
                    r = self.index.query(vector=emb, top_k=top_k,
                                         filter={"user_id": {"$eq": user_id}},
                                         include_metadata=True)
                    return [f"[{m.metadata.get('timestamp','')[:10]}] {m.metadata.get('text','')}"
                            for m in r.matches if m.score > 0.3]
            except Exception as e:
                logger.error(f"Pinecone query failed: {e}")

        mems = self._store.get(user_id, [])
        if not mems:
            return []
        q = set(query.lower().split())
        scored = [(len(q & set(m["text"].lower().split())), m["text"]) for m in mems]
        scored.sort(key=lambda x: x[0], reverse=True)
        return [s[1] for s in scored[:top_k] if s[0] > 0]

    async def delete_user_data(self, user_id):
        if self._pc_ok:
            try:
                self.index.delete(filter={"user_id": {"$eq": user_id}})
            except Exception as e:
                logger.error(f"Pinecone delete failed: {e}")
        self._store.pop(user_id, None)
        return True


memory_service: Optional[MemoryService] = None

def init_memory(pc_key, oai_key, index="mindos-memory", model="text-embedding-3-small", dims=1536):
    global memory_service
    memory_service = MemoryService(pc_key, oai_key, index, model, dims)
    return memory_service
