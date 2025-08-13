---
title: LocalTrip
emoji: 🐠
colorFrom: indigo
colorTo: green
sdk: docker
pinned: false
short_description: For PAN-SEA POC demo
---

# SealionAI Travel Planning Service

AI-powered travel planning service using SEA-LION LLM and RAG (Retrieval-Augmented Generation) technology. This service extracts travel information from YouTube videos and generates personalized trip plans.

## Features

- 🎯 **Intelligent Trip Planning**: Generate detailed itineraries using AI
- 🎥 **YouTube Integration**: Extract travel content from YouTube videos
- 🔍 **Semantic Search**: Find similar travel content using vector embeddings
- 💬 **Chat Interface**: Interactive travel assistance
- 🌏 **Multi-language Support**: English and Thai transcript extraction

## Quick Start

### With uv (Recommended)

```bash
# Install uv
curl -LsSf https://astral.sh/uv/install.sh | sh

# Clone and setup
git clone <repository-url>
cd SealionAiService
uv sync

# Create environment file
cp .env.example .env
# Edit .env with your API keys

# Run the service
uv run uvicorn app.app:app --reload
```

## Environment Variables

Create a `.env` file with the following variables:

```env
SEALION_API=your_sealion_api_key
SEALION_BASE_URL=https://api.sea-lion.ai/v1
QDRANT_HOST=localhost
```

## API Documentation

Base URL: `https://localtrip.taspolsd.dev/v1`

### 1. Health Check

**GET** `/v1`

Simple health check endpoint.

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2025-08-13T18:52:51.699007",
  "service": "SealionAI Travel Planning Service",
  "version": "1.0.0",
  "checks": {

  }
}
```

---

### 2. Generate Trip Plan

**POST** `/v1/generateTripPlan`

Generate a comprehensive AI-powered trip plan using RAG technology.

**Request Body:**
```json
{
  "start_place": "Bangkok",
  "destination_place": "Doi laung ChiangDao",
  "trip_price": 4000.0,
  "trip_context": "adventure and culture",
  "trip_duration_days": 4,
  "group_size": 3,
  "preferences": ["hiking", "natural"],
  "top_k": 3
}
```

**Parameters:**
- `start_place` (string, required): Starting location
- `destination_place` (string, required): Destination location
- `trip_price` (float, optional): Budget for the trip
- `trip_context` (string, optional): Trip theme (e.g., "adventure", "business", "family")
- `trip_duration_days` (integer, optional): Duration in days
- `group_size` (integer, optional): Number of travelers
- `preferences` (array, optional): List of interests/preferences
- `top_k` (integer, optional): Number of similar documents to retrieve (default: 3)

**Response:**
```json
{
  "tripOverview": "Your 4-day adventure from Bangkok to Doi Luang Chiang Dao offers an incredible blend of cultural immersion and natural exploration. Starting from Thailand's bustling capital, you'll journey north to one of the country's most spectacular mountain peaks, experiencing traditional hill tribe culture, pristine hiking trails, and breathtaking mountain vistas.",
  "query_params": {
    "start_place": "Bangkok",
    "destination_place": "Doi Luang Chiang Dao",
    "trip_price": 4000.0,
    "trip_context": "adventure and culture",
    "trip_duration_days": 4,
    "group_size": 3,
    "preferences": ["hiking", "natural"],
    "top_k": 3
  },
  "retrieved_data": [
    {
      "place_id": "1",
      "place_name": "Doi Luang Chiang Dao",
      "description": "Thailand's third highest peak offering challenging hiking trails and stunning mountain views",
      "score": 0.95,
      "metadata": {"elevation": "2175m", "type": "mountain", "difficulty": "challenging"}
    },
    {
      "place_id": "2",
      "place_name": "Chiang Dao Cave",
      "description": "Extensive limestone cave system with Buddhist shrines and spectacular formations",
      "score": 0.89,
      "metadata": {"type": "cave", "cultural_significance": "buddhist_shrine"}
    }
  ],
  "trip_plan": {
    "overview": "4-day mountain adventure and cultural exploration",
    "total_estimated_cost": 3800.0,
    "steps": [
      {
        "day": 1,
        "title": "Bangkok to Chiang Dao - Journey North",
        "description": "Depart Bangkok early morning, travel to Chiang Dao. Check into mountain lodge and explore Chiang Dao Cave temple complex.",
        "transport": {
          "mode": "Flight + Car",
          "departure": "Bangkok",
          "arrival": "Chiang Mai Airport + Drive to Chiang Dao",
          "duration_minutes": 480,
          "price": 350.0,
          "details": "1-hour flight + 1.5-hour scenic drive through mountain roads"
        },
        "map_coordinates": {"lat": 19.3668, "lon": 98.9206},
        "images": ["chiang_dao_cave.jpg", "mountain_lodge.jpg"],
        "tips": [
          "Book mountain lodge in advance",
          "Bring warm clothes for mountain evenings",
          "Cash needed for local vendors"
        ]
      },
            {
        "day": 2,
        "title": "Doi Luang Summit Attempt - Day 1",
        "description": "Early morning start for the challenging hike to Doi Luang peak. Set up camp at designated camping area below summit.",
        "transport": {
          "mode": "Hiking",
          "departure": "Chiang Dao Base",
          "arrival": "Mountain Camp (1800m)",
          "duration_minutes": 360,
          "price": 0.0,
          "details": "6-hour challenging hike through tropical forest to mountain camp"
        },
        "map_coordinates": {"lat": 19.4053, "lon": 98.9211},
        "images": ["mountain_trail.jpg", "forest_canopy.jpg"],
        "tips": [
          "Start before 6 AM to avoid afternoon heat",
          "Carry plenty of water (3L minimum per person)",
          "Hire local guide for safety and navigation",
          "Pack lightweight camping gear"
        ]
      },
      {
        "day": 3,
        "title": "Summit Day & Cultural Village Visit",
        "description": "Pre-dawn summit attempt to catch sunrise from Thailand's 3rd highest peak. Descend to visit local hill tribe village.",
        "transport": {
          "mode": "Hiking + Walking",
          "departure": "Mountain Camp",
          "arrival": "Hill Tribe Village",
          "duration_minutes": 480,
          "price": 100.0,
          "details": "2-hour summit climb + 6-hour descent to village with homestay"
        },
        "map_coordinates": {"lat": 19.4108, "lon": 98.9234},
        "images": ["doi_luang_summit.jpg", "hill_tribe_village.jpg"],
        "tips": [
          "Start summit attempt at 4 AM for sunrise",
          "Bring headlamp and warm layers",
          "Respect local customs in hill tribe village",
          "Try traditional Karen/Shan cuisine"
        ]
      },
      {
        "day": 4,
        "title": "Village Culture & Return to Bangkok",
        "description": "Morning cultural activities with hill tribe community. Traditional weaving and cooking demonstrations. Afternoon return journey.",
        "transport": {
          "mode": "Car + Flight",
          "departure": "Chiang Dao Village",
          "arrival": "Bangkok",
          "duration_minutes": 420,
          "price": 380.0,
          "details": "Drive to Chiang Mai Airport + direct flight to Bangkok"
        },
        "map_coordinates": {"lat": 13.7563, "lon": 100.5018},
        "images": ["traditional_weaving.jpg", "village_cooking.jpg"],
        "tips": [
          "Purchase authentic handicrafts directly from artisans",
          "Learn basic Thai phrases for better cultural exchange",
          "Bring gifts for host family (school supplies appreciated)",
          "Depart village by 1 PM for evening flight"
        ]
      }
    ]
  },
  "meta": {
    "status": "success",
    "query_text": "Trip from Bangkok to Doi Luang Chiang Dao for adventure and culture for 4 days with budget 4000.0",
    "results_count": 3
  }
}
```

---

### 3. Add YouTube Link

**POST** `/v1/addYoutubeLink`

Extract transcript from a YouTube video and store it in the vector database for future trip planning.

**Request Body:**
```json
{
  "video_id": "DGHila4P0Vs"
}
```

**Parameters:**
- `video_id` (string, required): YouTube video ID (extract from URL: `https://www.youtube.com/watch?v=VIDEO_ID`)

**Response:**
```json
{
  "message": "add successfully",
  "video_url": "https://www.youtube.com/watch?v=DGHila4P0Vs"
}
```

**Error Response:**
```json
{
  "message": "Failed to add YouTube link",
  "video_url": null
}
```

**Language Priority:**
The system automatically selects transcripts in the following order:
1. English (manual or auto-generated)
2. Thai (manual or auto-generated)
3. Any auto-generated transcript
4. First available transcript

---

### 5. Basic Chat

**POST** `/v1/basicChat`

Interactive chat interface with the SEA-LION LLM for general travel assistance.

**Request Body:**
```json
{
  "message": "What should I pack for hiking Doi Luang Chiang Dao?"
}
```

**Parameters:**
- `message` (string, required): Your travel-related question or message

**Response:**
```json
"For hiking Doi Luang Chiang Dao, pack these essentials: sturdy hiking boots with good ankle support, lightweight but warm layers (temperatures drop significantly at night), waterproof rain gear, plenty of water (3L minimum), high-energy snacks, headlamp with extra batteries, first aid kit, and camping gear if doing the 2-day trek. Don't forget insect repellent, sunscreen, and a portable water filter. The trail can be challenging and weather changes quickly at elevation."
```

## Example Usage

### cURL Examples

**Generate Trip Plan:**
```bash
curl -X POST "http://localhost:8000/v1/generateTripPlan" \
  -H "Content-Type: application/json" \
  -d '{
    "start_place": "Bangkok",
    "destination_place": "Doi Luang Chiang Dao",
    "trip_price": 4000.0,
    "trip_context": "adventure and culture",
    "trip_duration_days": 4,
    "group_size": 3,
    "preferences": ["hiking", "natural"]
  }'
```

**Add YouTube Content:**
```bash
curl -X POST "http://localhost:8000/v1/addYoutubeLink" \
  -H "Content-Type: application/json" \
  -d '{"video_id": "DGHila4P0Vs"}'
```

**Chat:**
```bash
curl -X POST "http://localhost:8000/v1/basicChat" \
  -H "Content-Type: application/json" \
  -d '{"message": "What is the best season to hike Doi Luang Chiang Dao?"}'
```

### Python Client Example

```python
import requests

# Generate trip plan
response = requests.post("http://localhost:8000/v1/generateTripPlan", json={
    "start_place": "Bangkok",
    "destination_place": "Doi Luang Chiang Dao",
    "trip_duration_days": 4,
    "trip_price": 4000.0,
    "trip_context": "adventure and culture",
    "group_size": 3,
    "preferences": ["hiking", "natural", "mountain climbing"]
})

trip_plan = response.json()
print(f"Trip Overview: {trip_plan['tripOverview']}")
```

## Architecture

- **FastAPI**: Modern Python web framework
- **SEA-LION LLM**: Large Language Model for trip planning
- **Qdrant**: Vector database for semantic search
- **BGE-M3**: Embedding model for text vectorization
- **YouTube Transcript API**: Extract video transcripts

## Error Handling

All endpoints return appropriate HTTP status codes:

- `200`: Success
- `422`: Validation Error (invalid request format)
- `500`: Internal Server Error

**Validation Error Example:**
```json
{
  "detail": [
    {
      "type": "missing",
      "loc": ["body", "video_id"],
      "msg": "Field required",
      "input": {}
    }
  ]
}
```

## Development

```bash
# Add new dependency
uv add package-name

# Run tests
uv run pytest

# Format code
uv run black .

# Start development server
uv run uvicorn app.app:app --reload --host 0.0.0.0 --port 8000
```

## Docker Deployment

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY . .

RUN pip install uv
RUN uv sync

EXPOSE 8000

CMD ["uv", "run", "uvicorn", "app.app:app", "--host", "0.0.0.0", "--port", "8000"]
```

## Configuration Reference

Check out the configuration reference at https://huggingface.co/docs/hub/spaces-config-reference

## License

MIT License

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request