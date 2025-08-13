from utils.youtube_extractor import YoutubeExtractor
from sentence_transformers import SentenceTransformer
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
from typing import List, Dict, Optional, Union
import uuid

class DataImporter:
    def __init__(self, qdrant_url: str = "http://localhost:6333", collection_name: str = "demo_bge_m3"):
        self.model = SentenceTransformer("BAAI/bge-m3")
        self.client = QdrantClient(url=qdrant_url)
        self.collection_name = collection_name
        self.youtube_extractor = YoutubeExtractor()
        
        # Create collection if it doesn't exist
        self._create_collection()
    
    def _create_collection(self):
        try:
            collections = self.client.get_collection(self.collection_name)
            if collections:
                print(f"Collection '{self.collection_name}' already exists.")
                return

            self.client.recreate_collection(
                collection_name=self.collection_name,
                vectors_config=VectorParams(size=1024, distance=Distance.COSINE)
            )
            print(f"Collection '{self.collection_name}' created successfully")
        except Exception as e:
            print(f"Error creating collection: {e}")
    
    def encode_text(self, texts: Union[str, List[str]]) -> List[List[float]]:
        if isinstance(texts, str):
            texts = [texts]
        
        embeddings = self.model.encode(texts, normalize_embeddings=True)
        return embeddings.tolist()
    
    def insert_text(self, text: str, metadata: Optional[Dict] = None, custom_id: Optional[str] = None) -> str:
        point_id = custom_id or str(uuid.uuid4())
        embedding = self.encode_text(text)[0]
        
        payload = {"text": text}
        if metadata:
            payload.update(metadata)
        
        self.client.upsert(
            collection_name=self.collection_name,
            points=[PointStruct(id=point_id, vector=embedding, payload=payload)]
        )
        
        print(f"Inserted text with ID: {point_id}")
        return point_id
    
    def insert_texts(self, texts: List[str], metadata_list: Optional[List[Dict]] = None) -> List[str]:
        embeddings = self.encode_text(texts)
        point_ids = [str(uuid.uuid4()) for _ in texts]
        
        points = []
        for i, (text, embedding, point_id) in enumerate(zip(texts, embeddings, point_ids)):
            payload = {"text": text}
            if metadata_list and i < len(metadata_list):
                payload.update(metadata_list[i])
            
            points.append(PointStruct(id=point_id, vector=embedding, payload=payload))
        
        self.client.upsert(collection_name=self.collection_name, points=points)
        print(f"Inserted {len(texts)} texts")
        return point_ids
    
    def insert_from_youtube(self, video_id: str, metadata: Optional[Dict] = None) -> Optional[str]:
        try:
            # Extract text from YouTube (assuming your YoutubeExtractor has this method)
            text = self.youtube_extractor.get_full_text(video_id)
            if text:
                video_metadata = {"source": "youtube", "video_id": video_id}
                if metadata:
                    video_metadata.update(metadata)
                
                return self.insert_text(text, video_metadata)
            return None
        except Exception as e:
            print(f"Error extracting from YouTube: {e}")
            return None
    
    def search_similar(self, query: str, limit: int = 5) -> List[Dict]:
        query_embedding = self.encode_text(query)[0]
        
        results = self.client.search(
            collection_name=self.collection_name,
            query_vector=query_embedding,
            limit=limit
        )
        
        return [
            {
                "id": result.id,
                "score": result.score,
                "text": result.payload.get("text", ""),
                "metadata": {k: v for k, v in result.payload.items() if k != "text"}
            }
            for result in results
        ]
