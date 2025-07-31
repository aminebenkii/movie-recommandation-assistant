# ✅ Backend Progress — MoviesYouDidntWatch.com

Tracking which Python files are implemented, need testing, or still require work.

---

## 📁 `api/`

| File               | Status   | Notes |
|--------------------|----------|-------|
| `auth_routes.py`   | ✅ DONE  |       |
| `chat_routes.py`   | ✅ DONE  |       |
| `user_routes.py`   | ✅ DONE  |       |
| `movie_routes.py`  | ✅ DONE  |       |
| `tvshow_routes.py` | ✅ DONE  |       |
| `router.py`        | ✅ DONE  |       |


---

## 📁 `core/`

| File               | Status   | Notes                                                                 |
|--------------------|----------|-----------------------------------------------------------------------|
| `config.py`        | ✅ DONE  |                                                                       |
| `openai_client.py` | ✅ DONE  |                                                                       |
| `tmdb_client.py`   | ✅ DONE  |                                                                       |
| `omdb_client.py`   | ✅ DONE  |                                                                       |
| `database.py`      | ✅ DONE  | Need to discuss schema change handling and support for multiple DBs   |
| `dependencies.py`  | ✅ DONE  |                                                                       |
| `security.py`      | ✅ DONE  |                                                                       |

---

## 📁 `models/`

| File                    | Status                  | Notes                                      |
|-------------------------|-------------------------|--------------------------------------------|
| `user_model.py`         | ✅ DONE                 |                                            |
| `movie_model.py`        | ✅ DONE                 |                                            |
| `tvshow_model.py`       | ✅ DONE                 |                                            |
| `chat_session_model.py` | ✅ DONE                 |                                            |
| `user_media_model.py`   | ✅ DONE                 |                                            |


---

## 📁 `schemas/`

| File               | Status                  | Notes |
|--------------------|--------------------------|-------|
| `movie_schemas.py` | ✅ DONE                  |       |
| `tvshow_schemas.py`| ✅ DONE                  |       |
| `user_schemas.py`  | ✅ DONE                  |       |
| `chat_schemas.py`  | ✅ DONE                  |       |
| `stats_schemas.py` | ❌ NOT STARTED           |       |


---

## 📁 `services/`

| File                   | Status                     | Notes                     |
|------------------------|----------------------------|---------------------------|
| `auth_service.py`      | ✅ DONE                    | Solid                     |
| `movie_service.py`     | ✅ DONE                    | Solid                     |
| `tvshow_service.py`    | ✅ DONE                    |                           |
| `session_service.py`   | ✅ DONE                    |                           |
| `llm_service.py`       | 🔧 NEEDS REWORK            |                           |
| `chat_service.py`      | 🔧 NEEDS REWORK            |                           |
| `user_media_service.py`| ✅ DONE                    |                           |

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



- [] Completely remake Chat Route and Logic
- [] Start writing unit and integration tests in `tests/`
- [] Set up CI/CD pipeline using GitHub Actions
