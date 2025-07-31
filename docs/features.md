# 🌟 Core Features — MoviesYouDidntWatch.com

A smart discovery app for movies **and TV shows** that actually gets your taste.  
No more endless scrolling. No more repeated suggestions.  
Just **great content**, powered by **IMDb ratings**, your **watch history**, and a clever chat assistant.

---

## 📑 Table of Contents

1. [🎬 Intelligent Discovery (IMDb + AI)](#-1-intelligent-discovery-imdb--ai)
2. [🧠 Personalized & User-Aware](#-2-personalized--user-aware)
3. [💬 Smart Assistant = Your Content Concierge](#-3-smart-assistant--your-content-concierge)
4. [🎯 Manual Filtering (If You Want It)](#-4-manual-filtering-if-you-want-it)
5. [🎛️ Rich Hybrid UX (Chat + Filters)](#-5-rich-hybrid-ux-chat--filters)
6. [🎬 Cards with Quick Actions (Movies & Shows)](#-6-cards-with-quick-actions-movies--shows)
7. [📁 User Lists](#-7-user-lists)
8. [📊 Personal Stats](#-8-personal-stats)
9. [🌍 Multilingual Support (EN/FR)](#-9-multilingual-support-enfr)
10. [🚀 Powered by Real Tech](#-10-powered-by-real-tech)

---

## 🎬 1. Intelligent Discovery (IMDb + AI)

We don’t suggest random blockbusters.  
We **enrich every title** — movie or show — with real-world quality data:

- ✅ **IMDb ratings** and **vote counts** from OMDB
- 🎯 Only show titles with:
  - High rating (e.g. 7.0+)
  - Enough votes to be reliable
  - Genre in top 2 TMDB tags
- 🧠 Results are **reranked** based on your sort preference (rating, votes, popularity)

---

## 🧠 2. Personalized & User-Aware

Your taste matters. Your history is remembered.

Every user has their own:

- ✅ `Seen` titles
- ⏱ `Watch Later` list
- ❌ `Not Interested` titles

These are:

- 🔒 **Always excluded** from future suggestions
- 🎯 Used behind the scenes to **tailor every result**
- 📊 Available for filtering, tracking, and stats

No duplicates. No spam. Just content you haven’t seen.

---

## 💬 3. Smart Assistant = Your Content Concierge

Talk to your assistant like a friend.  
Let it **filter**, **search**, and **recommend** for you.

Ask for:

- _“Underrated 90s sci-fi series with deep themes”_
- _“More shows like Dark”_
- _“Should I watch this or that?”_

It can:

- 🧠 Understand genres, ratings, dates, language, type (movie/show)
- 🗂 Generate proper backend filters
- 🧬 Recommend similar content using OpenAI
- 👁 React to the titles **currently visible** on screen
- 🔁 Remember context within your session

---

## 🎯 4. Manual Filtering (If You Want It)

Use dropdowns and sliders to fine-tune your search.

Filters include:

- 📺 `type`: `movie` or `tv`
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

## 🎬 6. Cards with Quick Actions (Movies & Shows)

Each result comes as an interactive card:

- 🎞️ Poster
- 📛 Release year
- ⭐ IMDb rating
- 🗳️ Vote count

Click to expand and get:

- 📝 Overview
- 🎭 Genre tags
- ⏱ Runtime or episode count
- ▶️ Embedded trailer
- 🔗 IMDb link

Quick actions:

- 👁 `Seen`
- ⏱ `Watch Later`
- ❌ `Not Interested`

These update instantly and affect future suggestions.

---

## 📁 7. User Lists

You manage your own content universe:

- ✅ **Seen**
- ⏱ **Watch Later**
- ❌ **Not Interested**

Every list:

- Is filterable by genre, year, rating, and type (`movie` or `tv`)
- Can be undone or adjusted
- Is used by the backend to personalize all recommendations

---

## 📊 8. Personal Stats

Keep track of your discovery journey:

- 🎥 Total movies & shows watched
- ⭐ Average IMDb rating
- 🎭 Top genres
- 📅 Most-watched years
- ⏱ Total hours watched
- 🔝 (Coming Soon) Top actor / director

---

## 🌍 9. Multilingual Support (EN/FR)

Everything is **localized**, both in UI and content.

- 🇬🇧 🇫🇷 Language toggle
- Metadata stored in:
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
- 🎬 Content data: `TMDB API`
- ⭐ IMDb data: `OMDB API`
- 🗂 Caching: Local DB with 7-day refresh logic
- 🔁 Parallel enrichment for fast response
- 🔒 User auth: JWT tokens

---

> 🚀 Ready to suggest **great movies and shows you haven’t seen** — with logic, taste, and style.
