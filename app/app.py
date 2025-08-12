from fastapi import FastAPI

from interface import PlanRequest, PlanResponse, PlanStep, TransportInfo, TripPlan , YoutubeLinkRequest, YoutubeLinkResponse
from data_importer import DataImporter
import os
import json

app = FastAPI()
data_importer = DataImporter()

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
    mock_trip_plan = load_mock_data()
    print(mock_trip_plan)
    return PlanResponse(
        tripOverview="Sample trip overview.",
        query_params=request,
        retrieved_data=[],
        trip_plan=TripPlan(
            overview="Sample trip overview",
            total_estimated_cost=1000.0,
            steps=[PlanStep(
            day=1,
            title="Arrival in New York",
            description="Arrive at JFK Airport and check-in at the hotel.",
            transport=TransportInfo(
                mode="Plane",
                departure="Your hometown airport",
                arrival="JFK Airport",
                duration_minutes=300,
                price=300.0,
                details="Non-stop flight"
            ),
            map_coordinates={"lat": 40.6413, "lon": -73.7781},
            images=["https://example.com/images/jfk_airport.jpg"],
            tips=["Bring a valid ID", "Confirm your hotel reservation"]
        )]),
        meta={"status": "success"}
    )

# @app.post("/v1/addYoutubeLink", response_model=YoutubeLinkResponse)
# def add_youtube_link(request: YoutubeLinkRequest):
#     try:
#         data_importer.insert_from_youtube(request.video_id)
#     except Exception as e:
#         return YoutubeLinkResponse(
#             message="Failed to add YouTube link",
#             video_url=None
#         )
#     return YoutubeLinkResponse(
#         message="add successfully",
#         video_url=f"https://www.youtube.com/watch?v={request.video_id}"
#     )
