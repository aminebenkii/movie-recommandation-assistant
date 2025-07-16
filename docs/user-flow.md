# 👤 User Flow — MoviesYouDidntWatch.com

This document defines the complete **front-to-back UX journey** for the platform. It outlines how users interact with the app, from the hero landing page to personal stats and chatbot-based discovery.

---

## 🚪 1. Hero Page (Landing)

- Background image/artwork (subtle, cinematic)
- Center:
  - **Register** button
  - **Login** button
- Top-right:
  - **Language toggle** 🇫🇷 / 🇬🇧
    - Updates all visible UI text instantly

---

## 📝 2. Authentication

### Register Page

User enters:

- First Name
- Email
- Password

Below the form:
> “Already have an account? [Login instead]”

### Login Page

User enters:

- Email
- Password

Below the form:
> “Don’t have an account yet? [Register here]”

✅ Upon successful login/registration, the user is redirected to the **Main App Page**.

---

## 🏠 3. Main App Page Layout

### 3.1 Header

- **Left**: Clickable logo → returns to hero page
- **Right**:
  - `Hello, Amine` (clickable → opens User Panel)
  - `Logout` button

### 3.2 Filters Bar

- Genre dropdown
- IMDb rating slider (e.g., 6.0–10.0)
- Minimum vote count input/slider
- Release year range slider
- Language filter (optional)
- Sort by dropdown (rating, popularity, etc.)

### 3.3 Chat Button

- Fixed position button
- Opens **Chat Window** (slide-in/modal)
- Supports natural language like:

```
"Show me dark comedies like The Lobster"
"Sci-fi from the 90s with great ratings"
```

✅ When submitted:
- Chat parses query
- Filters update accordingly
- Movie grid refreshes

---

## 🎞️ 4. Movie Grid

- Displays up to 25 movie cards
- Each card shows:
  - Poster
  - Title
  - IMDb Rating (e.g., ★ 8.4)
  - Vote Count (e.g., 120k votes)
  - Buttons:
    - 👁 Seen
    - ❌ Not Interested
    - ⏱ Watch Later

### On Click (Card Expand):

- Description
- Genre tags
- Runtime
- Release year
- Embedded **YouTube trailer**
- IMDb link

✅ Buttons (Seen, Later, Not Interested) also work in expanded view.

---

## 👤 5. User Panel

Click `Hello, Amine` → navigates to the **User Panel**.

Tabs:

- ✅ **Seen Movies**
  - List of all marked as seen
  - Filterable by genre, rating, etc.

- ⏱ **Watch Later**
  - Saved for later viewing
  - Can remove or mark as seen

- ❌ **Not Interested**
  - Hidden movies
  - Can undo if needed

---

## 📊 6. Personal Stats (Optional)

Includes:

- Total movies seen
- Average IMDb rating
- Top watched genres
- Most watched years
- Total hours watched
- Favorite actor/director (future)

---

## 🧠 Smart Features Overview

- **Movies marked as Seen / Later / Not Interested** are excluded from future suggestions
- **Chat and manual filters** work together:
  - Changing one updates the other
- **Multilingual**:
  - UI + content adapt to selected language (FR/EN)
- **Strict filtering rules**:
  - Only shows high-rated, well-voted, genre-relevant movies

---

✅ This file documents:

- The complete UX journey
- Authentication logic
- Layout and filtering behavior
- Interaction with the chat
- Movie actions and profile management
