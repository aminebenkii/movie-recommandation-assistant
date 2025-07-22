# 🌟 Core Features — MoviesYouDidntWatch.com

A smart movie discovery app that actually gets your taste.  
No more endless scrolling. No more repeated suggestions.  
Just **great films**, powered by **IMDb ratings**, your **watch history**, and a clever chat assistant.

---

## 📑 Table of Contents

1. [🎬 Intelligent Movie Discovery (IMDb + AI)](#-1-intelligent-movie-discovery-imdb--ai)
2. [🧠 Personalized & User-Aware](#-2-personalized--user-aware)
3. [💬 Smart Assistant = Your Movie Concierge](#-3-smart-assistant--your-movie-concierge)
4. [🎯 Manual Filtering (If You Want It)](#-4-manual-filtering-if-you-want-it)
5. [🎛️ Rich Hybrid UX (Chat + Filters)](#-5-rich-hybrid-ux-chat--filters)
6. [🎬 Movie Cards with Quick Actions](#-6-movie-cards-with-quick-actions)
7. [📁 User Movie Lists](#-7-user-movie-lists)
8. [📊 Personal Stats](#-8-personal-stats)
9. [🌍 Multilingual Support (EN/FR)](#-9-multilingual-support-enfr)
10. [🚀 Powered by Real Tech](#-10-powered-by-real-tech)

---

## 🎬 1. Intelligent Movie Discovery (IMDb + AI)

We don’t suggest random blockbusters.  
We **enrich every movie** with real-world quality data:

- ✅ **IMDb ratings** and **vote counts** from OMDB
- 🎯 Only show movies with:
  - High rating (e.g. 7.0+)
  - Enough votes to be reliable
  - Genre in top 2 TMDB tags
- 🧠 Results are **reranked** based on your sort preference (rating, votes, popularity)

---

## 🧠 2. Personalized & User-Aware

Your taste matters. Your history is remembered.

Every user has their own:

- ✅ `Seen` movies
- ⏱ `Watch Later` list
- ❌ `Not Interested` movies

These are:

- 🔒 **Always excluded** from future recommendations
- 🎯 Used behind the scenes to **tailor every result**
- 📊 Available for filtering, tracking, and stats

No duplicates. No spam. Just stuff you haven’t watched.

---

## 💬 3. Smart Assistant = Your Movie Concierge

Talk to your assistant like a friend.  
Let it **filter**, **search**, and **recommend** for you.

Ask for:

- _“Underrated 90s sci-fi with deep themes”_
- _“More movies like The Lobster”_
- _“Which of these should I actually watch?”_

It can:

- 🧠 Understand genres, ratings, dates, language
- 🗂 Generate proper backend filters
- 🧬 Recommend similar movies using OpenAI
- 👁 React to the movies **currently visible** on screen
- 🔁 Remember context within your session

---

## 🎯 4. Manual Filtering (If You Want It)

Use dropdowns and sliders to fine-tune your search.

Filters include:

- 🎭 `genre_id`
- ⭐ `IMDb rating` (min–max)
- 🗳️ `IMDb vote count` minimum
- 📅 Release year (min–max)
- 🌍 Original language
- 🔀 Sort by: `popularity`, `vote_average`, `vote_count`

---

## 🎛️ 5. Rich Hybrid UX (Chat + Filters)

- 🔄 Chat and filter UI stay in **sync**
- 🗣 Chat updates the filters automatically
- 🖱 Filters reflect the current chat context
- 🧩 Both use the same backend logic: `recommend_movies()` or `recommend_similar_movies()`

Switch seamlessly between clicking and chatting.

---

## 🎬 6. Movie Cards with Quick Actions

Each result comes as an interactive movie card:

- 🎞️ Poster
- 📛 Release year
- ⭐ IMDb rating
- 🗳️ Vote count

Click to expand and get:

- 📝 Overview
- 🎭 Genre tags
- ⏱ Runtime
- ▶️ Embedded trailer
- 🔗 IMDb link

Quick actions:

- 👁 `Seen`
- ⏱ `Watch Later`
- ❌ `Not Interested`

These update instantly and affect future suggestions.

---

## 📁 7. User Movie Lists

You manage your own movie universe:

- ✅ **Seen**
- ⏱ **Watch Later**
- ❌ **Not Interested**

Every list:

- Is filterable by genre, year, rating
- Can be undone or adjusted
- Is used by the backend to personalize all recommendations

---

## 📊 8. Personal Stats

Keep track of your movie journey:

- 🎥 Total movies watched
- ⭐ Average IMDb rating
- 🎭 Top genres
- 📅 Most-watched years
- ⏱ Total hours watched
- 🔝 (Coming Soon) Top actor / director

---

## 🌍 9. Multilingual Support (EN/FR)

Everything is **localized**, both in UI and content.

- 🇬🇧 🇫🇷 Language toggle
- Movie metadata stored in:
  - `title_en`, `title_fr`
  - `overview_en`, `overview_fr`
  - `trailer_url_en`, `trailer_url_fr`
- Assistant replies in selected language

All results are shown in the correct language — always.

---

## 🚀 10. Powered by Real Tech

We’re not faking it with frontend-only gimmicks.

- ⚙️ Backend: `FastAPI`, `PostgreSQL`, `SQLAlchemy`
- 🧠 AI: `OpenAI GPT`, session-aware assistant
- 🎬 Movie data: `TMDB API`
- ⭐ IMDb data: `OMDB API`
- 🗂 Caching: Local DB with 7-day refresh logic
- 🔁 Parallel enrichment for fast response
- 🔒 User auth: JWT tokens

---

> 🚀 Ready to suggest **great movies you haven’t seen** — with logic, taste, and style.
