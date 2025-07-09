# 🎬 MoviesYouDidntWatch.com

**A conversational movie recommender built with FastAPI + React + OpenAI**  
Discover great films you've *never seen before* — in natural language.

---

## 🚀 What Is It?

**MoviesYouDidntWatch.com** is an intelligent, chat-based movie recommendation app designed for cinephiles. Using natural language, users can describe the kind of movie they want — and the system will reply with high-quality, unseen suggestions. It avoids repetition by keeping track of watched movies and leverages the power of OpenAI's GPT, TMDB, and OMDB APIs to recommend, filter, and enrich results.

---

## 🧠 Features

- 🎙️ **Conversational Discovery**  
  Ask for movies by genre, rating, mood, actor, etc. ("Give me a crime drama rated 8+")

- 🙈 **Avoids Repetition**  
  Automatically filters out movies you've already seen

- ⭐ **High-Quality Results**  
  Uses IMDb ratings and TMDB metadata to sort by quality

- ▶️ **Watch Trailers Instantly**  
  Pulls YouTube/TMDB trailers for instant previews

- 🔐 **JWT-Based Auth System**  
  Register/login with secure password handling

- 🌐 **Multi-Language Ready**  
  English/French toggle (frontend ready, backend integration WIP)

---

## 🏗 Architecture Overview

```
movie-recommender-chatbot/
├── app/
│   ├── backend/
│   │   ├── api/
│   │   │   ├── __init__.py
│   │   │   ├── auth.py x            # Defines /auth/register and /auth/login endpoints, Receives credentials, calls auth_service, returns JWT
│   │   │   ├── chat.py x            # Defines/chat endpoint, Accepts user message, calls LLM service and movie_service
│   │   │   ├── seen.py x            # Defines /seen POST and GET, Lets user mark a movie as seen or fetch seen movies
│   │   │   ├── users.py x           # Has a Route you can  call to get Information about you (as a user)
│   │   │   ├── router.py x          # Gathers all routers (auth, chat, seen), Mounts them on the main FastAPI app
│   │   │   └── 
│   │   ├── core/
│   │   │   ├── config.py x          # Loads and exposes app settings (.env vars, secrets)
│   │   │   ├── openai_client.py x   # Wraps OpenAI GPT API calls (chat completions etc.)
│   │   │   ├── tmdb_client.py x     # wraps tmdb requests calls ( discover_movies, get_trailers, get_genre_to_id, etc .. )
│   │   │   ├── omdb_client.py x     # wraps omdb requests calls ( get_imdb_ratings.. )
│   │   │   ├── database.py x        # Contains all SQL Database Init engine, Session, getdb, etc..
│   │   │   ├── dependancies.py x    # Contains def to get_user_by_token ..
│   │   │   └── security.py x        # Password hashing (bcrypt), JWT encode/decode logic
│   │   │
│   │   ├── models/
│   │   │   ├── user.py x            # SQLAlchemy User model with id, name, email, password_hash
│   │   │   ├── chat_session.py x    # (Optional) SQLAlchemy model to store conversations
│   │   │   └── seen.py x            # SQLAlchemy model to store user_id + movie_id pairs
│   │   │
│   │   ├── schemas/
│   │   │   ├── user.py x            # Pydantic models: UserRegister, UserLogin, UserResponse
│   │   │   ├── chat.py x            # Pydantic models: ChatRequest, ChatResponse
│   │   │   ├── movie.py x           # Pydantic models: MovieCard
│   │   │   └── seen.py x            # Pydantic models for marking movies as seen (movie_id)
│   │   │
│   │   ├── services/
│   │   │   ├── auth_service.py x    # Business logic for registering, logging in users, Verifies password, returns JWT.
│   │   │   ├── llm_service.py x     # Sends message to OpenAI, Can include parsing/guiding the output
│   │   │   ├── movie_service.py x   # Filters movie data based on query
│   │   │   ├── session_service.py x # Optional for storing conversations
│   │   │   └── seen_service.py x    # Tracks seen movies per user
│   │   │
│   │   ├── utils/
│   │   │   └── utils.py x           # Generic helper functions
│   │   │
│   │   └── main.py                 # FastAPI app entrypoint
│
│   ├── frontend/
│   │   ├── public/
│   │   ├── src/
│   │   │   ├── components/
│   │   │   │   ├── ChatBox.jsx            # Chat UI (left panel)
│   │   │   │   ├── MovieCard.jsx          # Card for each movie result (right panel)
│   │   │   │   ├── AuthForm.jsx           # Shared form for login/register
│   │   │   │   └── LanguageSelector.jsx   # French/English toggle button
│   │   │   ├── pages/
│   │   │   │   ├── Hero.jsx               # Landing page with language + auth buttons
│   │   │   │   ├── Login.jsx              # Login form page
│   │   │   │   ├── Register.jsx           # Registration page
│   │   │   │   └── ChatPage.jsx           # Main app page – left: chat, right: movie grid
│   │   │   ├── context/
│   │   │   │   └── AuthContext.js         # Auth provider and JWT handling
│   │   │   ├── App.jsx
│   │   │   └── main.jsx
│   │   └── tailwind.config.js
│
├── data/                         # Movie data (raw & processed)
│   ├── raw/
│   └── processed/
│     └── genres_mapping.json     # dict to map id to genre and vice versa
│
├── storage/                      # Optional model or session storage
├── tests/                        # Unit and integration tests
├── .env                          # Environment variables: API keys, secrets
├── .gitignore                    # Ignore __pycache__, .env, node_modules, etc.
├── api_test.py                   # Quick script to test endpoints (curl, requests)
├── DevNotes.md                   # This file you're reading
├── Dockerfile                    # For containerizing the backend app
├── README.md                     # Project intro, how to run, screenshots
└── requirements.txt              # Python dependencies

```

### ✨ Tech Stack

| Layer        | Technology                             |
|--------------|----------------------------------------|
| Frontend     | React + TailwindCSS                    |
| Backend      | FastAPI, Pydantic, SQLAlchemy          |
| Database     | SQLite (dev), PostgreSQL (prod)        |
| Auth         | JWT-based (bcrypt + token decoding)    |
| LLM          | OpenAI GPT-4 via OpenAI API            |
| Movie APIs   | TMDB (core data), OMDB (IMDb ratings)  |
| Deployment   | AWS (Amplify/S3 + EC2/ECS + RDS)       |

---

## 🧭 User Journey

1. **Landing Page**  
   - Choose language (EN/FR), log in or register

2. **Register / Login**  
   - Secure credentials sent to FastAPI auth endpoints

3. **Main App: Chat Interface**  
   - Chat with the bot: "Find me a romantic comedy from the 90s"
   - Get 10 smart suggestions in the movie grid
   - Click ✅ **Seen** to mark a movie as watched
   - ▶️ **Watch Trailer** to preview movies instantly

4. **Seen Movies**  
   - Seen movies are excluded from future suggestions  
   - View future stats on `/me` page (planned)

---

## 🛠 Key Endpoints

| Endpoint         | Method | Auth? | Description                              |
|------------------|--------|-------|------------------------------------------|
| `/auth/register` | POST   | ❌    | Register a new user                      |
| `/auth/login`    | POST   | ❌    | Authenticate user, return JWT            |
| `/chat`          | POST   | ✅    | Submit message, receive movie suggestions|
| `/seen`          | POST   | ✅    | Mark movie as seen                       |
| `/seen`          | GET    | ✅    | Get all seen movies                      |
| `/users/me`      | GET    | ✅    | Get current user info                    |

---

## ⚙️ How to Run Locally

### 1. Backend (FastAPI)

```bash
cd app/backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env  # Add your TMDB, OMDB, OpenAI keys
uvicorn main:app --reload
```

### 2. Frontend (React)

```bash
cd app/frontend
npm install
npm run dev
```

---

## 🧪 Testing

```bash
cd app/backend
pytest
```

Or run the manual API tester:

```bash
python api_test.py
```

---

## 📈 Roadmap

- [x] Auth system (JWT-based)
- [x] Movie engine (filtering, seen-tracking)
- [x] LLM + OpenAI integration
- [ ] Regex fallback for filter extraction
- [ ] `/me` route for user stats
- [ ] Language-aware recommendations
- [ ] Unit & integration tests
- [ ] Frontend → backend wiring

---

## 📄 License

MIT License © 2025 [Your Name or Team Name]

---

## 🤝 Contributing

Pull requests are welcome!  
If you're interested in contributing, check out `DevNotes.md` for architecture and file structure.

---

## 📬 Contact

Have suggestions, questions, or feedback?  
Open an issue or reach out at: **you@example.com**

---

**MoviesYouDidntWatch.com** – _Helping you find your next favorite movie, not just the same old ones._
