import os
import asyncio
import httpx
from typing import List, Optional, Dict, Any
from dataclasses import dataclass
from qdrant_client import QdrantClient

SYSTEM_PROMPT = """You are a helpful travel assistant. Use the provided context to answer the user's question about travel destinations and places.
If the context doesn't contain relevant information, say so politely and provide general advice if possible."""
'''
'''
@dataclass
class RetrievedItem:
    place_id: str
    place_name: str
    description: Optional[str]
    score: float
    metadata: Dict[str, Any]

class LLMCaller:
    def __init__(self):
        # Environment variables
        self.qdrant_host = os.getenv("QDRANT_HOST", "localhost")
        self.qdrant_api_key = os.getenv("QDRANT_API_KEY", None)
        self.qdrant_collection = os.getenv("QDRANT_COLLECTION", "trip_places")
        self.embedding_dim = int(os.getenv("EMBEDDING_DIM", "1024"))
        self.top_k = int(os.getenv("TOP_K", "6"))
        
        # LLM configuration
        self.llm_api_url = os.getenv("LLM_API_URL", "https://api.openai.com/v1/chat/completions")
        self.llm_api_key = os.getenv("LLM_API_KEY", "sk-REPLACE_ME")
        
        # Initialize Qdrant client
        self.qdrant = QdrantClient(
            host=self.qdrant_host,
            api_key=self.qdrant_api_key
        )
    
    async def call_llm(self, system_prompt: str, user_prompt: str, max_tokens: int = 512, model: str = "sea-lion-7b-instruct") -> str:
        """
        Call LLM with system and user prompts
        
        Args:
            system_prompt (str): System message for the LLM
            user_prompt (str): User message/question
            max_tokens (int): Maximum tokens to generate
            model (str): Model to use
            
        Returns:
            str: LLM response text
        """
        headers = {
            "Authorization": f"Bearer {self.llm_api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            "max_tokens": max_tokens,
            "temperature": 0.7,
        }
        
        try:
            async with httpx.AsyncClient(timeout=30) as client:
                resp = await client.post(self.llm_api_url, json=payload, headers=headers)
                resp.raise_for_status()
                data = resp.json()
                
                # Handle OpenAI-like response format
                if "choices" in data and len(data["choices"]) > 0:
                    return data["choices"][0]["message"]["content"]
                
                # Fallback for other formats
                return data.get("text", "")
                
        except Exception as e:
            print(f"Error calling LLM: {e}")
            return f"Error: Unable to get LLM response - {str(e)}"
    
    async def query_qdrant(self, query_embedding: List[float], top_k: Optional[int] = None, collection_name: Optional[str] = None) -> List[RetrievedItem]:
        """
        Query Qdrant vector database
        
        Args:
            query_embedding (List[float]): Query vector embedding
            top_k (int, optional): Number of results to return
            collection_name (str, optional): Collection name to query
            
        Returns:
            List[RetrievedItem]: Retrieved items from Qdrant
        """
        top_k = top_k or self.top_k
        collection_name = collection_name or self.qdrant_collection
        
        def _search():
            try:
                hits = self.qdrant.search(
                    collection_name=collection_name,
                    query_vector=query_embedding,
                    limit=top_k,
                    with_payload=True,
                )
                
                items: List[RetrievedItem] = []
                for h in hits:
                    payload = h.payload or {}
                    items.append(RetrievedItem(
                        place_id=str(h.id),
                        place_name=payload.get("name") or payload.get("title") or "",
                        description=payload.get("description") or payload.get("summary") or None,
                        score=float(h.score) if h.score is not None else 0.0,
                        metadata=payload,
                    ))
                return items
            except Exception as e:
                print(f"Error querying Qdrant: {e}")
                return []

        return await asyncio.to_thread(_search)
    
    async def rag_query(self, query: str, query_embedding: List[float], system_prompt: Optional[str] = None) -> Dict[str, Any]:
        # Retrieve relevant items from Qdrant
        retrieved_items = await self.query_qdrant(query_embedding)
        
        # Build context from retrieved items
        context_parts = []
        for item in retrieved_items:
            context_parts.append(f"- {item.place_name}: {item.description or 'No description available'}")
        
        context = "\n".join(context_parts) if context_parts else "No relevant information found."
        
        # Default system prompt if none provided
        if not system_prompt:
            system_prompt = """You are a helpful travel assistant. Use the provided context to answer the user's question about travel destinations and places. 
                               If the context doesn't contain relevant information, say so politely and provide general advice if possible."""
        
        # Create user prompt with context
        user_prompt = f"""Context:
{context}

Question: {query}

Please provide a helpful response based on the context above."""
        
        # Get LLM response
        llm_response = await self.call_llm(system_prompt, user_prompt)
        
        return {
            "answer": llm_response,
            "retrieved_items": retrieved_items,
            "context": context,
            "query": query
        }
    
    def update_config(self, **kwargs):
        """
        Update configuration parameters
        
        Args:
            **kwargs: Configuration parameters to update
        """
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
            else:
                print(f"Warning: Unknown configuration parameter: {key}")

# Example usage
if __name__ == "__main__":
    async def main():
        # Initialize LLM caller
        llm_caller = LLMCaller()
        
        # Example embedding (replace with actual embedding)
        query_embedding = [0.1] * 1024  # Dummy embedding
        
        # Perform RAG query
        result = await llm_caller.rag_query(
            query="What are the best places to visit in Thailand?",
            query_embedding=query_embedding
        )
        
        print("Answer:", result["answer"])
        print(f"Found {len(result['retrieved_items'])} relevant items")
        
        # Direct LLM call
        response = await llm_caller.call_llm(
            system_prompt="You are a helpful assistant.",
            user_prompt="What is the capital of Thailand?"
        )
        print("Direct LLM Response:", response)
    
    asyncio.run(main())