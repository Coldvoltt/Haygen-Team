# Haygen-Team

A full-stack web application that generates AI video avatar introductions for team members using the [HeyGen API](https://www.heygen.com/).

## Features

- Create teams with multiple members and custom introduction text
- Automatically assigns random HeyGen avatars and matching voices to each member
- Generates avatar videos concurrently in the background
- Watch each member's AI-generated video introduction in a modal player

## Tech Stack

- **Backend** — Python, FastAPI, httpx, Pydantic
- **Frontend** — React 19, Vite
- **API** — HeyGen v2 (avatars, voices, video generation)

## Project Structure

```
backend/
  main.py              # FastAPI app, endpoints, CORS config
  heygen_service.py    # HeyGen API client (avatars, voices, video generation)
  models.py            # Pydantic request/response models
  requirements.txt     # Python dependencies
  .env.example         # Environment variable template
frontend/
  src/
    App.jsx            # Root component (team creation / team view)
    api.js             # API client functions
    components/
      CreateTeam.jsx   # Team creation form
      TeamGrid.jsx     # Grid layout of team member cards
      MemberCard.jsx   # Individual member card with avatar preview
      VideoModal.jsx   # Video playback modal
```

## Prerequisites

- Python 3.10+
- Node.js 18+
- A [HeyGen API key](https://www.heygen.com/)

## Getting Started

### Backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env        # Add your HEYGEN_API_KEY
python main.py              # Runs on http://localhost:8000
```

### Frontend

```bash
cd frontend
npm install
npm run dev                 # Runs on http://localhost:5173
```

Open [http://localhost:5173](http://localhost:5173) in your browser.

## API Endpoints

| Method | Endpoint                     | Description                          |
|--------|------------------------------|--------------------------------------|
| GET    | `/api/avatars`               | List available HeyGen avatars        |
| POST   | `/api/team`                  | Create a team with member data       |
| GET    | `/api/team/{team_id}`        | Get a team by ID                     |
| GET    | `/api/teams`                 | List all teams                       |
| POST   | `/api/generate-intro`        | Check/trigger video for a member     |
| GET    | `/api/video-status/{video_id}` | Check video generation status     |

## License

This project is licensed under the Apache License 2.0 — see [LICENSE](LICENSE) for details.
