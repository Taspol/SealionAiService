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

### With pip

```bash
# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run the service
uvicorn app.app:app --reload
```

## Environment Variables

Create a `.env` file with the following variables:

```env
SEALION_API=your_sealion_api_key
SEALION_BASE_URL=https://api.sea-lion.ai/v1
QDRANT_HOST=localhost
```

## API Documentation

Base URL: `http://localhost:8000`

### 1. Health Check

**GET** `/v1`

Simple health check endpoint.

**Response:**
```json
{
  "Hello": "World!"
}
```

---

### 2. Generate Trip Plan

**POST** `/v1/generateTripPlan`

Generate a comprehensive AI-powered trip plan using RAG technology.

**Request Body:**
```json
{
  "start_place": "Singapore",
  "destination_place": "Tokyo",
  "trip_price": 2000.0,
  "trip_context": "adventure and culture",
  "trip_duration_days": 5,
  "group_size": 2,
  "preferences": ["temples", "food", "shopping", "museums"],
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
  "tripOverview": "Your 5-day Tokyo adventure from Singapore offers an exciting blend of traditional culture and modern experiences...",
  "query_params": {
    "start_place": "Singapore",
    "destination_place": "Tokyo",
    "trip_price": 2000.0,
    "trip_context": "adventure and culture",
    "trip_duration_days": 5,
    "group_size": 2,
    "preferences": ["temples", "food", "shopping"],
    "top_k": 3
  },
  "retrieved_data": [
    {
      "place_id": "1",
      "place_name": "Senso-ji Temple",
      "description": "Ancient Buddhist temple in Asakusa district",
      "score": 0.92,
      "metadata": {"district": "Asakusa", "type": "temple"}
    }
  ],
  "trip_plan": {
    "overview": "5-day cultural adventure in Tokyo",
    "total_estimated_cost": 1850.0,
    "steps": [
      {
        "day": 1,
        "title": "Arrival and Shibuya Exploration",
        "description": "Land in Tokyo, check into hotel, explore Shibuya crossing...",
        "transport": {
          "mode": "Flight + Train",
          "departure": "Singapore Changi Airport",
          "arrival": "Tokyo Haneda Airport",
          "duration_minutes": 420,
          "price": 600.0,
          "details": "Direct flight followed by airport express"
        },
        "map_coordinates": {"lat": 35.6762, "lon": 139.6503},
        "images": ["shibuya_crossing.jpg"],
        "tips": ["Get JR Pass for unlimited train travel", "Download Google Translate app"]
      }
    ]
  },
  "meta": {
    "status": "success",
    "query_text": "Trip from Singapore to Tokyo for adventure and culture for 5 days with budget 2000.0",
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

### 4. Search Similar Content

**POST** `/v1/searchSimilar`

Search for similar travel content in the vector database using semantic similarity.

**Request Body:**
```json
{
  "video_id": "DGHila4P0Vs"
}
```

**Parameters:**
- `video_id` (string, required): YouTube video ID to use as search query

**Response:**
```json
[
  {
    "id": "1",
    "score": 0.95,
    "payload": {
      "text": "Tokyo is known for its vibrant culture, amazing food scene...",
      "place_name": "Tokyo",
      "video_id": "DGHila4P0Vs",
      "timestamp": "2024-01-15T10:30:00Z"
    }
  },
  {
    "id": "2",
    "score": 0.87,
    "payload": {
      "text": "The temples in Kyoto offer a glimpse into Japan's rich history...",
      "place_name": "Kyoto",
      "video_id": "another_video_id",
      "timestamp": "2024-01-14T15:20:00Z"
    }
  }
]
```

**Error Response:**
```json
{
  "error": "Search failed"
}
```

---

### 5. Basic Chat

**POST** `/v1/basicChat`

Interactive chat interface with the SEA-LION LLM for general travel assistance.

**Request Body:**
```json
{
  "message": "What are the best places to visit in Tokyo for first-time travelers?"
}
```

**Parameters:**
- `message` (string, required): Your travel-related question or message

**Response:**
```json
"For first-time visitors to Tokyo, I recommend starting with these iconic destinations: Shibuya Crossing for the bustling city experience, Senso-ji Temple in Asakusa for traditional culture, Tokyo Skytree for panoramic views, and Harajuku for unique fashion and youth culture. Don't miss trying authentic sushi at Tsukiji Outer Market and experiencing the efficiency of the JR train system..."
```

## Example Usage

### cURL Examples

**Generate Trip Plan:**
```bash
curl -X POST "http://localhost:8000/v1/generateTripPlan" \
  -H "Content-Type: application/json" \
  -d '{
    "start_place": "Bangkok",
    "destination_place": "Chiang Mai",
    "trip_price": 1500.0,
    "trip_context": "cultural exploration",
    "trip_duration_days": 4,
    "group_size": 2,
    "preferences": ["temples", "local food", "markets"]
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
  -d '{"message": "What should I pack for a trip to Thailand?"}'
```

### Python Client Example

```python
import requests

# Generate trip plan
response = requests.post("http://localhost:8000/v1/generateTripPlan", json={
    "start_place": "Singapore",
    "destination_place": "Bali",
    "trip_duration_days": 7,
    "trip_price": 2500.0,
    "preferences": ["beaches", "culture", "adventure"]
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