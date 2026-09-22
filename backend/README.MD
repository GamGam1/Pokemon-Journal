# Pokémon Journal API

A Django REST API that analyzes journal entries using Claude AI to detect emotional themes and match them to Pokémon songs.

## Tech Stack
- Django + Django REST Framework
- PostgreSQL
- Claude API (Anthropic)
- JWT Authentication (simplejwt)

## Local Setup

1. Clone the repo and cd into backend/
2. Create and activate virtual environment:
   python -m venv venv
   source venv/bin/activate
3. Install dependencies:
   pip install -r requirements.txt
4. Create .env file (see .env.example)
5. Create PostgreSQL database:
   createdb pokemon_journal
6. Run migrations:
   python manage.py migrate
7. Start server:
   python manage.py runserver

## Environment Variables
ANTHROPIC_API_KEY=
DB_NAME=
DB_USER=
DB_PASSWORD=
DB_HOST=
DB_PORT=
SECRET_KEY=

## API Endpoints

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| POST | /api/register/ | Create account | No |
| POST | /api/token/ | Login, get JWT | No |
| POST | /api/token/refresh/ | Refresh token | No |
| GET | /api/entries/ | List your entries | Yes |
| POST | /api/entries/ | Create entry + AI analysis | Yes |
| GET | /api/entries/{id}/ | Get one entry | Yes |
| PUT | /api/entries/{id}/ | Update entry | Yes |
| DELETE | /api/entries/{id}/ | Delete entry | Yes |
| GET | /api/entries/patterns/ | Theme frequency analytics | Yes |

## Running Tests
pytest