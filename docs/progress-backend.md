# ✅ Backend Progress — MoviesYouDidntWatch.com

Tracking which Python files are implemented, need testing, or still require work.

---

## 📁 `api/`

| File              | Status             | Notes |
|-------------------|--------------------|-------|
| `__init__.py`     | ✅ DONE             | |
| `auth.py`         | ✅ DONE             | All good |
| `chat.py`         | 🔧 TODO             | Lots missing |
| `users.py`        | 🧪 DONE, to be tested | Routes in place |
| `movies.py`       | 🧪 DONE, to be tested | Functional |
| `user_movies.py`  | 🧪 DONE, to be tested | Functional |
| `router.py`       | ✅ DONE             | Assembles routes |

---

## 📁 `core/`

| File               | Status             | Notes |
|--------------------|--------------------|-------|
| `config.py`        | ✅ DONE             | |
| `openai_client.py` | ✅ DONE (will rename later) | Rename some defs during chat integration |
| `tmdb_client.py`   | ✅ DONE             | |
| `omdb_client.py`   | ✅ DONE             | |
| `database.py`      | ✅ DONE             | Need to discuss what happens if schema changes |
| `dependencies.py`  | 🔧 TODO             | Add `get_language()` |
| `security.py`      | ✅ DONE             | All good |

---

## 📁 `models/`

| File               | Status             | Notes |
|--------------------|--------------------|-------|
| `user.py`          | ✅ DONE             | |
| `movie.py`         | 🔍 REVIEW           | Might need updates for movie list display |
| `chat_session.py`  | 🔍 REVIEW           | Probably DONE — needs checking |
| `user_movie.py`    | 🧪 DONE, to be tested | |

---

## 📁 `schemas/`

| File         | Status             | Notes |
|--------------|--------------------|-------|
| `user.py`    | ✅ DONE             | |
| `chat.py`    | ✅ DONE (may evolve) | Might change during chat logic |
| `stats.py`   | ❌ NOT STARTED      | |
| `movie.py`   | 🧪 DONE, to be tested | |

---

## 📁 `services/`

| File                   | Status             | Notes |
|------------------------|--------------------|-------|
| `auth_service.py`      | ✅ DONE             | Solid |
| `llm_service.py`       | 🔧 TODO             | Rework during chat phase |
| `movie_service.py`     | 🧪 DONE, to be tested | Logic ready, needs testing |
| `session_service.py`   | 🔧 TODO             | To be handled in chat phase |
| `parser.py`            | 🔧 TODO             | Same as above |
| `user_movie_service.py`| 🔧 HIGH PRIORITY    | Next big thing to tackle |

---

## 📁 `utils/`

| File          | Status     | Notes |
|---------------|------------|-------|
| `utils.py`    | ✅ DONE     | Generic helpers done |

---

## 🧩 `main.py`

| File      | Status     | Notes |
|-----------|------------|-------|
| `main.py` | ✅ DONE     | Entrypoint is working |

---

## 🎯 Next Steps

- [ ] Finish `user_movie_service.py`
- [ ] Add `get_language()` in `dependencies.py`
- [ ] Start writing unit + integration tests in `tests/`
- [ ] Set up CI/CD with GitHub Actions
