# 🌟 Core Features — MoviesYouDidntWatch.com

This document outlines the core features available to users — across discovery, filtering, user experience, and personalization — as well as intelligent backend behavior.

---

## 🔍 1. Movie Discovery

### 🧠 Chat-Based Search

- Users can ask in **natural language**:
  - _“Show me 90s sci-fi movies with great ratings”_
  - _“Something like The Lobster or Black Mirror”_
- The assistant understands:
  - Genre
  - Year range
  - Rating & vote thresholds
  - Style/tone-based hints (e.g. “underrated”, “disturbing”, etc.)

### 🎯 Manual Filtering

- Genre dropdown
- IMDb rating slider (e.g., 6.5–10.0)
- Vote count minimum
- Release year range
- Sort by: rating, popularity, vote count, date
- Optional language filter

### 🧠 Smart Chat Awareness

- The chatbot is **context-aware** of the **currently displayed movies**.
- You can ask:
  - _“Which of these do you recommend?”_
  - _“Any hidden gems on this page?”_
- The assistant will respond based on:
  - Genre match
  - Rating vs popularity
  - User preferences (if learned over time)

---

## 🎛️ 2. Hybrid UX (Chat + Filters)

- Manual filters and chatbot stay in **sync**
- Chat updates filters visually
- Filters reflect current chatbot state
- Either tool can drive the movie list

---

## 🎬 3. Movie Cards

Each movie card displays:

- 🎞️ Poster
- 📛 Release Year
- ⭐ IMDb Rating
- 🗳️ Vote count

### Quick Actions (on card and expand view):

- 👁 **Seen**
- ⏱ **Watch Later**
- ❌ **Not Interested**

### Expandable View:

- Full description
- Genre tags
- Runtime
- Year
- Embedded YouTube trailer
- IMDb link

---

## 📁 4. User Movie Lists

Users can manage their movie experience through:

### ✅ Seen
- Movies marked as watched
- Filterable by genre, rating, year

### ⏱ Watch Later
- A personal queue
- Can remove or mark as seen

### ❌ Not Interested
- Excludes suggestions
- Can undo if needed

---

## 📊 5. Personal Stats (Optional)

- 🎥 Total movies watched
- 📈 Average IMDb rating
- 🎭 Top genres
- 📅 Most watched years
- ⏱️ Total hours watched
- (Future) Top actor or director

---

## 🌐 6. Multilingual Support

- 🌍 Language toggle (🇬🇧 / 🇫🇷)
- UI and chatbot fully localized
- TMDB/OMDB data fetched in the correct language
- Future: support for more languages

---

## 🧠 7. Behind-the-Scenes Logic

### 🔒 Intelligent Filtering

- Genre must be **1st or 2nd** in TMDB metadata
- Enforced thresholds:
  - Minimum IMDb rating
  - Minimum vote count
- Cached and enriched with OMDB (for better quality control)

### 🧠 Smart Movie Memory

- Each user has:
  - `Seen` movies
  - `Watch Later` queue
  - `Not Interested` list

✅ These are **always excluded** from recommendations  
✅ Helps prevent repeated or unwanted suggestions

---

## 💬 8. Chat Session Tracking

- Conversations are stored per user session
- Assistant can remember your query context
- Potential to improve personalization over time

---
