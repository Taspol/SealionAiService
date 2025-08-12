from pydantic import BaseModel, Field
from typing import List, Optional, Any, Dict

class TripPlanRequest(BaseModel):
    destination: str
    duration: int
    budget: float
    preferences: list[str] = []

class TripPlanResponse(BaseModel):
    message: str
    plan: dict

class YoutubeLinkRequest(BaseModel):
    video_id: str

class YoutubeLinkResponse(BaseModel):
    message: str
    video_url: str


class PlanRequest(BaseModel):
    start_place: str
    destination_place: str
    trip_price: Optional[float] = Field(None, description="Total budget in local currency")
    trip_context: Optional[str] = Field(None, description="e.g. adventure, rest, date")
    trip_duration_days: Optional[int] = 1
    group_size: Optional[int] = 1
    preferences: Optional[List[str]] = None
    top_k: Optional[int] = 3


class RetrievedItem(BaseModel):
    place_id: str
    place_name: str
    description: Optional[str]
    score: float
    metadata: Optional[Dict[str, Any]] = None

class TransportInfo(BaseModel):
    mode: Optional[str]
    departure: Optional[str]
    arrival: Optional[str]
    duration_minutes: Optional[int]
    price: Optional[float]
    details: Optional[str]

class PlanStep(BaseModel):
    day: Optional[int]
    title: Optional[str]
    description: Optional[str]
    transport: Optional[TransportInfo]
    map_coordinates: Optional[Dict[str, float]]
    images: Optional[List[str]]
    tips: Optional[List[str]]

class TripPlan(BaseModel):
    overview: str
    total_estimated_cost: Optional[float]
    steps: List[PlanStep]

class PlanResponse(BaseModel):
    tripOverview: str
    query_params: PlanRequest
    retrieved_data: List[RetrievedItem]
    trip_plan: TripPlan
    meta: Dict[str, Any]
