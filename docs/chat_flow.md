# 💬 Chat Flow — `chat_service.py`

This document outlines how user chat queries are handled by the backend assistant logic.

---
## 🧠 Overview

The goal of the chat assistant route is to help users discover **movies or TV shows** in an **interactive and natural way**.

Instead of using dropdowns or filters manually, the user can just type what they want — and the assistant will:

- **Understand their intent** (e.g. a title, a vibe, a genre filter)
- **Classify** that query into one of four possible modes:
  - `exact_title`: Find a specific movie or show (even with typos)
  - `similar_media`: Recommend titles similar to another one
  - `filters_parsing`: Extract structured filters from natural language
  - `free_description_suggestion`: Suggest titles based on a mood, plot, or open description
- **Route** the request to the right logic block
- **Return** a `ChatResponse` containing:
  - A smart `message` (what the assistant would say)
  - A list of `results` (MovieCard or TvShowCard)
  - Optional `filters` (if parsed from the query)
  - And the `media_type` (`movie` or `tv`)

The full flow looks like this:

```
User Query → Classify Intent → Route to Handler → Return ChatResponse
```
---

## 🧩 Step-by-Step Logic

### `process_chat_query(payload: ChatQuery, user: User, db: Session, language: str) → ChatResponse`

This is the core function that processes a user message, determines the user’s intent, and returns the appropriate content response.

---

#### 1. Get or create session
- Fetch the `ChatSession` using `session_id` from the request
- If the session doesn't exist, create a new one for the user
- Append the user’s latest message to the conversation history (as a `user` role)

---

#### 2. Prune conversation
- For efficiency and relevance, keep only the **last 2 full exchanges** (max 4 messages)
- This context is passed to the LLM to maintain short-term memory

---

#### 3. Classify intent
Call `classify_chat_intent(query, media_type)` to determine how to route the request:

```python
{
  "intent": "filters_parsing",
  "media_type": "movie",
  "message_to_user": "Sure! Here are some French thrillers from the 2010s."
}
```

The classification model returns:
- `intent`: One of five supported types (see below)
- `media_type`: `"movie"` or `"tv"` if known or inferred
- `message_to_user`: Friendly response text the assistant should say

---

#### 4. Route to the appropriate logic handler

Depending on the returned `intent`, the assistant routes the query to one of these blocks:

| Intent                      | Handler(s)                                                                 | Description                                                                 |
|-----------------------------|----------------------------------------------------------------------------|-----------------------------------------------------------------------------|
| `exact_title`               | `search_movies_by_title()` / `search_tvshows_by_title()`                  | Resolve a specific title, even if misspelled                               |
| `similar_media`             | `recommend_similar_movies()` / `recommend_similar_tvshows()`              | Recommend titles similar to a given movie or show                          |
| `filters_parsing`           | `parse_filters_with_llm()` → `recommend_movies_by_filters()` / `recommend_tvshows_by_filters()` | Extract structured filters using LLM, then return matching content         |
| `free_description_suggestion` | `recommend_movies_from_description()` / `recommend_tvshows_from_description()` | Suggest titles from a mood, plot, or free-form description                 |
| `error`                     | None — return only message                                                | Assistant couldn't classify or needed clarification (e.g., media type)     |

---

#### 5. Enrich and return

For all cases except `error`, the flow ends by:

- Resolving titles into TMDB IDs
- Enriching and caching full metadata (TMDB + OMDB)
- Returning a structured `ChatResponse` object with:
  - A `message` from the assistant
  - A list of `results` (MovieCard or TvShowCard)
  - An optional `filters` object
  - The `media_type` (always included)

---

#### 6. Update assistant reply in the session

- After generating a response, the assistant reply (`message_to_user`) is also added to the session as a `assistant` role message
- This helps preserve context and maintain continuity across the conversation



---

## 🧠 Supported Intents

| Intent              | Description                                                                 |
|---------------------|-----------------------------------------------------------------------------|
| `exact_title`       | User wants to find a specific movie/show (even if misspelled)              |
| `similar_media`     | User wants recommendations *like* another title                             |
| `filters_parsing`   | User uses structured filters (e.g. genre, date, language, rating)           |
| `titles_suggestion` | User describes a mood, plot, or vibe — open-ended title suggestions         |
| `error`             | LLM cannot classify or media type is missing and unclear                    |

---
## ⚙️ Routing Logic (Core Switch Block)

### 1. `error`
- No movie or show is returned.
- The assistant responds with a **clarification message**, usually asking the user to specify their intent or media type.
```python
return ChatResponse(message="Could you clarify if you’re looking for movies or TV shows?")
```

---

### 2. `exact_title`
- The user likely mentioned a specific movie or show title (even with typos).
- Call either:
  - `search_movies_by_title()` if media_type is `"movie"`
  - `search_tvshows_by_title()` if media_type is `"tv"`
- Return up to 3 matching titles (cached and enriched).

---

### 3. `similar_media`
- The user asked for titles like another one they’ve seen.
- Call:
  - `recommend_similar_movies(title)` or  
  - `recommend_similar_tvshows(title)`
- Title spelling may be fixed using LLM.
- Return a list of similar titles, filtered for unseen items.

---

### 4. `filters_parsing`
- The query describes structured preferences (genre, rating, year, language).
- Use the LLM to extract a valid `MovieSearchFilters` or `TvShowSearchFilters` object.
- Call:
  - `recommend_movies_by_filters(filters)` or
  - `recommend_tvshows_by_filters(filters)`
- Return matching titles + the filters used.

---

### 5. `free_description_suggestion`
- The user provided a **free-form description** (e.g. mood, scenario, theme).
- LLM suggests a list of relevant titles.
- Each title is resolved to a TMDB ID and enriched.
- Call:
  - `search_movies_by_title([title1, title2, ...])` or
  - `search_tvshows_by_title([...])`
- Return a set of suggestion cards.

---


## 💬 Final Response Format

Every route returns a `ChatResponse` object:

```python
ChatResponse(
    message="Here are some suggestions...",
    results=[MovieCard | TvShowCard, ...],
    filters=MovieSearchFilters | TvShowSearchFilters,
    media_type="movie" or "tv"
)
```

---

## 🧠 Notes

- If no `media_type` is passed and cannot be guessed → return `error`
- Each LLM sub-function returns either:
  - a list of `{title, year}` items
  - or a filter dictionary
- All movie/show metadata is cached + enriched before returning

---
