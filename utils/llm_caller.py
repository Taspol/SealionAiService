import os
import asyncio
import httpx
from dotenv import load_dotenv
from typing import List, Optional, Dict, Any
from dataclasses import dataclass
from qdrant_client import QdrantClient
from openai import OpenAI
from sentence_transformers import SentenceTransformer
from interface import PlanResponse, TripPlan, PlanStep, TransportInfo, RetrievedItem, PlanRequest
import json 

load_dotenv()
SYSTEM_PROMPT = """You are a helpful travel assistant. Use the provided context to answer the user's question about travel destinations and places.
If the context doesn't contain relevant information, say so politely and provide general advice if possible."""
'''
'''
# @dataclass
# class RetrievedItem:
#     place_id: str
#     place_name: str
#     description: Optional[str]
#     score: float
#     metadata: Dict[str, Any]

class LLMCaller:
    def __init__(self):
        # Environment variables
        self.client = OpenAI(
                                api_key=os.getenv("SEALION_API"),
                                base_url=os.getenv("SEALION_BASE_URL"),
                            )
        self.top_k = 3
        self.qdrant_host = os.getenv("QDRANT_HOST")
        self.qdrant = QdrantClient(
            url=f"http://{self.qdrant_host}:6333",
        )
        self.system_prompt = SYSTEM_PROMPT
        self.embedding_model = SentenceTransformer("BAAI/bge-m3")
        self.collection_name = "demo_bge_m3"
    
    async def basic_query(self, user_prompt: str, max_tokens: int = 512, model: str = "aisingapore/Llama-SEA-LION-v3-70B-IT") -> str:
        
        try:
            completion = self.client.chat.completions.create(
                model=model,
                messages=[
                    {
                        "role": "system",
                        "content": self.system_prompt
                    },
                    {
                        "role": "user",
                        "content": user_prompt
                    }
                ]
            )
            return completion.choices[0].message.content
                
        except Exception as e:
            print(f"Error calling LLM: {e}")
            return f"Error: Unable to get LLM response - {str(e)}"
    
    async def query_with_rag(self, plan_request: PlanRequest, collection_name: Optional[str] = None) -> 'PlanResponse':
        """
        Perform RAG query using PlanRequest, embed query, search Qdrant, and generate complete PlanResponse via LLM
        """
        print(plan_request)
        try:
            # 1. Create query string from PlanRequest
            query_text = f"Trip from {plan_request.start_place} to {plan_request.destination_place}"
            if plan_request.trip_context:
                query_text += f" for {plan_request.trip_context}"
            if plan_request.trip_duration_days:
                query_text += f" for {plan_request.trip_duration_days} days"
            if plan_request.trip_price:
                query_text += f" with budget {plan_request.trip_price}"
            
            # 2. Generate embedding for the query
            query_embedding = self.embedding_model.encode(query_text, normalize_embeddings=True).tolist()
            
            # 3. Search Qdrant for similar content
            collection = collection_name or self.collection_name
            top_k = plan_request.top_k or self.top_k
            
            search_results = self.qdrant.search(
                collection_name=collection,
                query_vector=query_embedding,
                limit=top_k,
                with_payload=True
            )
            
            # 4. Convert search results to RetrievedItem format
            retrieved_data = []
            context_text = ""
            
            for result in search_results:
                retrieved_item = RetrievedItem(
                    place_id=str(result.id),
                    place_name=result.payload.get("place_name", "Unknown"),
                    description=result.payload.get("text", ""),
                    score=result.score,
                    metadata=result.payload
                )
                retrieved_data.append(retrieved_item)
                context_text += f"\n{result.payload.get('text', '')}"
            
            # 5. Create detailed prompt for LLM to generate structured response
            llm_prompt = f"""
            You are a travel planning assistant. Based on the trip request and travel context provided, generate a comprehensive trip plan in the exact JSON format specified below.

            Trip Request:
            - From: {plan_request.start_place}
            - To: {plan_request.destination_place}
            - Duration: {plan_request.trip_duration_days} days
            - Budget: {plan_request.trip_price}
            - Context: {plan_request.trip_context}
            - Group Size: {plan_request.group_size}
            - Preferences: {plan_request.preferences}

            Relevant Travel Context:
            {context_text}

            Generate a response in this EXACT JSON format (no additional text before or after):
            {{
                "tripOverview": "A comprehensive 2-3 paragraph overview of the entire trip",
                "trip_plan": {{
                    "overview": "Brief summary of the trip plan",
                    "total_estimated_cost": estimated_total_cost_as_number,
                    "steps": [
                        {{
                            "day": 1,
                            "title": "Day 1 title",
                            "description": "Detailed description of day 1 activities",
                            "transport": {{
                                "mode": "transportation method",
                                "departure": "departure location",
                                "arrival": "arrival location", 
                                "duration_minutes": estimated_duration_in_minutes,
                                "price": estimated_price,
                                "details": "additional transport details"
                            }},
                            "map_coordinates": {{"lat": latitude_number, "lon": longitude_number}},
                            "images": ["url1", "url2"],
                            "tips": ["tip1", "tip2", "tip3"]
                        }}
                    ]
                }}
            }}

            Create {plan_request.trip_duration_days or 1} days of detailed activities. Include realistic prices, coordinates, and practical tips. Make it specific to the destinations and context provided.
            """
            
            # 6. Call LLM to generate structured trip plan
            llm_response = await self.basic_query(user_prompt=llm_prompt, max_tokens=2048)
            
            # 7. Parse LLM response as JSON
            try:
                # Clean the response and parse JSON
                json_str = llm_response.strip()
                if json_str.startswith("```json"):
                    json_str = json_str[7:]
                if json_str.endswith("```"):
                    json_str = json_str[:-3]
                
                llm_data = json.loads(json_str)
                
                # Convert to PlanResponse structure
                trip_plan_data = llm_data.get("trip_plan", {})
                steps_data = trip_plan_data.get("steps", [])
                
                # Convert steps to PlanStep objects
                plan_steps = []
                for step in steps_data:
                    transport_data = step.get("transport", {})
                    transport = TransportInfo(
                        mode=transport_data.get("mode"),
                        departure=transport_data.get("departure"),
                        arrival=transport_data.get("arrival"),
                        duration_minutes=transport_data.get("duration_minutes"),
                        price=transport_data.get("price"),
                        details=transport_data.get("details")
                    )
                    
                    plan_step = PlanStep(
                        day=step.get("day"),
                        title=step.get("title"),
                        description=step.get("description"),
                        transport=transport,
                        map_coordinates=step.get("map_coordinates", {}),
                        images=step.get("images", []),
                        tips=step.get("tips", [])
                    )
                    plan_steps.append(plan_step)
                
                trip_plan = TripPlan(
                    overview=trip_plan_data.get("overview", ""),
                    total_estimated_cost=trip_plan_data.get("total_estimated_cost"),
                    steps=plan_steps
                )
                
                return PlanResponse(
                    tripOverview=llm_data.get("tripOverview", ""),
                    query_params=plan_request,
                    retrieved_data=retrieved_data,
                    trip_plan=trip_plan,
                    meta={
                        "status": "success",
                        "query_text": query_text,
                        "results_count": len(retrieved_data)
                    }
                )
                
            except json.JSONDecodeError as e:
                print(f"Error parsing LLM JSON response: {e}")
                print(f"LLM Response: {llm_response}")
                
                # Fallback: create basic response with LLM text
                return PlanResponse(
                    tripOverview=llm_response,
                    query_params=plan_request,
                    retrieved_data=retrieved_data,
                    trip_plan=TripPlan(
                        overview="Generated plan (parsing error)",
                        total_estimated_cost=plan_request.trip_price,
                        steps=[]
                    ),
                    meta={"status": "json_parse_error", "error": str(e)}
                )
            
        except Exception as e:
            print(f"Error in RAG query: {e}")
            return PlanResponse(
                tripOverview=f"Error generating trip plan: {str(e)}",
                query_params=plan_request,
                retrieved_data=[],
                trip_plan=TripPlan(overview="Error occurred", total_estimated_cost=0.0, steps=[]),
                meta={"status": "error", "error": str(e)}
            )
        
#     async def query_qdrant(self, query_embedding: List[float], top_k: Optional[int] = None, collection_name: Optional[str] = None) -> List[RetrievedItem]:
#         """
#         Query Qdrant vector database
        
#         Args:
#             query_embedding (List[float]): Query vector embedding
#             top_k (int, optional): Number of results to return
#             collection_name (str, optional): Collection name to query
            
#         Returns:
#             List[RetrievedItem]: Retrieved items from Qdrant
#         """
#         top_k = top_k or self.top_k
#         collection_name = collection_name or self.qdrant_collection
        
#         def _search():
#             try:
#                 hits = self.qdrant.search(
#                     collection_name=collection_name,
#                     query_vector=query_embedding,
#                     limit=top_k,
#                     with_payload=True,
#                 )
                
#                 items: List[RetrievedItem] = []
#                 for h in hits:
#                     payload = h.payload or {}
#                     items.append(RetrievedItem(
#                         place_id=str(h.id),
#                         place_name=payload.get("name") or payload.get("title") or "",
#                         description=payload.get("description") or payload.get("summary") or None,
#                         score=float(h.score) if h.score is not None else 0.0,
#                         metadata=payload,
#                     ))
#                 return items
#             except Exception as e:
#                 print(f"Error querying Qdrant: {e}")
#                 return []

#         return await asyncio.to_thread(_search)
    
#     async def rag_query(self, query: str, query_embedding: List[float], system_prompt: Optional[str] = None) -> Dict[str, Any]:
#         # Retrieve relevant items from Qdrant
#         retrieved_items = await self.query_qdrant(query_embedding)
        
#         # Build context from retrieved items
#         context_parts = []
#         for item in retrieved_items:
#             context_parts.append(f"- {item.place_name}: {item.description or 'No description available'}")
        
#         context = "\n".join(context_parts) if context_parts else "No relevant information found."
        
#         # Default system prompt if none provided
#         if not system_prompt:
#             system_prompt = """You are a helpful travel assistant. Use the provided context to answer the user's question about travel destinations and places. 
#                                If the context doesn't contain relevant information, say so politely and provide general advice if possible."""
        
#         # Create user prompt with context
#         user_prompt = f"""Context:
# {context}

# Question: {query}

# Please provide a helpful response based on the context above."""
        
#         # Get LLM response
#         llm_response = await self.call_llm(system_prompt, user_prompt)
        
#         return {
#             "answer": llm_response,
#             "retrieved_items": retrieved_items,
#             "context": context,
#             "query": query
#         }
    
#     def update_config(self, **kwargs):
#         """
#         Update configuration parameters
        
#         Args:
#             **kwargs: Configuration parameters to update
#         """
#         for key, value in kwargs.items():
#             if hasattr(self, key):
#                 setattr(self, key, value)
#             else:
#                 print(f"Warning: Unknown configuration parameter: {key}")
