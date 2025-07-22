# 🧪 Testing Plan — MoviesYouDidntWatch.com

A clean guide to testing your backend — written for someone starting from scratch.

---

## ✅ Goals of Testing

- Make sure the code does what it’s supposed to do
- Catch bugs before deploying
- Avoid breaking stuff when making changes
- Prepare for CI/CD automation

---

## 🧪 Types of Tests (Keep It Simple)

| Type           | What It Means                                   | Tools We'll Use          |
|----------------|--------------------------------------------------|---------------------------|
| 🧱 Unit Tests   | Test a single function or method (e.g. a service) | `pytest`                  |
| 🔗 Integration | Test how parts work together (e.g. route + DB)    | `pytest`, `httpx.AsyncClient` |
| ❌ E2E / Frontend | We are **NOT** testing React for now             |                         |

---

## 🔧 Testing Tools

- ✅ `pytest` → Run your tests
- ✅ `pytest-asyncio` → For async FastAPI routes
- ✅ `httpx.AsyncClient` → Simulate real HTTP requests
- ✅ `faker` → Fake user/email/password data
- ✅ `pytest-cov` → See how much code is tested (optional, later)
- ✅ SQLite in-memory → Temporary test database

---

## 🗂️ Folder Structure

```
tests/
├── conftest.py               # Shared test setup: DB, fake users, clients
├── test_auth.py              # /auth/signup and /auth/login
├── test_movies.py            # /movies/search with filters
├── test_user_movies.py       # /me/movies/update_status
├── test_chat.py              # /chat route and assistant replies
├── test_stats.py             # /users/me/stats
└── services/
    ├── test_auth_service.py
    ├── test_movie_service.py
    ├── test_user_movie_service.py
    ├── test_chat_service.py       ✅ Tests assistant logic (LLM + filters)
    ├── test_llm_service.py        ✅ Mocks OpenAI
```

---

## 📌 What Are We Testing?

### 1. ✅ API ROUTES (`/api`)

| File               | What to Test                              |
|--------------------|-------------------------------------------|
| `auth.py`          | Signup/login success & failures           |
| `movies.py`        | Does filtering work? Are seen movies excluded? |
| `user_movies.py`   | Can we mark movies as seen/later/hidden?  |
| `chat.py`          | Does the assistant respond correctly?     |
| `stats.py`         | Are personal stats calculated correctly?  |

---

### 2. ✅ SERVICES (`/services`)

| Service File              | What to Test                                        |
|---------------------------|-----------------------------------------------------|
| `movie_service.py`        | Main pipeline: fetch → enrich → rerank              |
| `auth_service.py`         | Password hashing, token creation                    |
| `user_movie_service.py`   | Marking and reading movie statuses                  |
| `chat_service.py`         | Prepares final assistant message + recommendations  |
| `llm_service.py`          | Interacts with OpenAI (mock responses here)         |

---

### 3. ✅ SCHEMAS (`/schemas`)

- Validate fields like email, password, status
- Try invalid values to confirm rejection

---

## 🧪 About the Test DB

We use **SQLite in memory** for testing:
- Creates a clean DB every time
- No risk of breaking your real data
- Fast and auto-resets after each test

In `conftest.py`, we’ll define:
- Fake user creation
- Test database session
- Auth token setup

---

## 🔌 Mocking External APIs

To avoid hitting real services in tests:

| Service   | Mock It? | Why? |
|-----------|----------|------|
| TMDB      | ✅ Yes    | Don’t waste requests / deal with live changes |
| OMDB      | ✅ Yes    | No need to hit external for IMDb rating       |
| OpenAI    | ✅ Yes    | Saves money + makes tests fast and stable     |

We’ll use Python’s `unittest.mock` or `pytest-mock`.

---

## 🌍 Multilingual Support

We will:
- Run some tests in `Accept-Language: fr`
- Confirm French fields are returned (title, overview, trailer)

Example:

```python
headers = {"Authorization": f"Bearer {token}", "Accept-Language": "fr"}
```

---

## ✅ GitHub Actions: Run Tests Automatically

Once tests are in place, we’ll add:

```
.github/workflows/tests.yml
```

It will:
- Trigger on every push or pull request
- Run `pytest` using a clean Python environment
- Fail the build if tests fail

---

## 🚧 Roadmap (Checklist)

- [ ] Set up `tests/` folder
- [ ] Add `conftest.py` with test DB + helpers
- [ ] Write 1 simple test for `auth_service`
- [ ] Write 1 API test for `/auth/signup`
- [ ] Mock OpenAI in `llm_service` tests
- [ ] Add GitHub Actions for auto-testing

---

## 💡 Tips

- Start with just **one test** at a time.
- Use `print()` in tests if you're stuck — it’s okay!
- If a test fails, that’s a win: you found a bug.

---

👋 Testing is **not about being smart** — it's about being *consistent*.

You'll get better with every test you write.
