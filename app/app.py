from fastapi import FastAPI

from interface import PlanRequest, PlanResponse, PlanStep, TransportInfo, TripPlan , YoutubeLinkRequest, YoutubeLinkResponse, ChatRequest
from data_importer import DataImporter
from utils.llm_caller import LLMCaller
import os
import json
import asyncio

app = FastAPI()
data_importer = DataImporter()
agent = LLMCaller()

def load_mock_data(path: str = "plan_mock.json") -> dict:
    """Load mock data from plan_mock.json"""
    try:
        file_path = os.path.join(os.path.dirname(__file__), path)
        with open(file_path, 'r', encoding='utf-8') as file:
            return json.load(file)
    except FileNotFoundError:
        # Return default mock data if file not found
        print("Mock data file not found. Using default mock data.")
        return {"error": "Invalid JSON format"}


@app.get("/v1")
def greet_json():
    return {"Hello": "World!"}

@app.post("/v1/generateTripPlan", response_model=PlanResponse)
def generate_trip_plan(request: PlanRequest):
    try:
        trip_plan = asyncio.run(agent.query_with_rag(request))
        return trip_plan
    except Exception as e:
        print(f"Error in generate_trip_plan: {e}")
        # Return error response
        return PlanResponse(
            tripOverview=f"Error: {str(e)}",
            query_params=request,
            retrieved_data=[],
            trip_plan=TripPlan(overview="Error occurred", total_estimated_cost=0.0, steps=[]),
            meta={"status": "error", "error": str(e)}
        )

@app.post("/v1/addYoutubeLink", response_model=YoutubeLinkResponse)
def add_youtube_link(request: YoutubeLinkRequest):
    try:
        data_importer.insert_from_youtube(request.video_id)
    except Exception as e:
        return YoutubeLinkResponse(
            message="Failed to add YouTube link",
            video_url=None
        )
    return YoutubeLinkResponse(
        message="add successfully",
        video_url=f"https://www.youtube.com/watch?v={request.video_id}"
    )

@app.post("/v1/searchSimilar", response_model=list[dict])
def search_similar(request: YoutubeLinkRequest):
    try:
        results = data_importer.search_similar(query=request.video_id)
        return results
    except Exception as e:
        print(f"Error during search: {e}")
        return {"error": "Search failed"}
    return []

@app.post("/v1/basicChat", response_model=str)
def basic_chat(request: ChatRequest):
    user_message = request.message
    llm_response = asyncio.run(agent.basic_query(
        user_prompt=user_message
    ))
    return llm_response

