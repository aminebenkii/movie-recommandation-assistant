## 🧑‍💻 Full User Story – Amine Uses MoviesYouDidntWatch.com

---

### 🧩 Scene 1 – Arrival: Hero Page

Amine opens `MoviesYouDidntWatch.com` on his browser.

- The **Hero page** loads instantly.
- It welcomes him in English by default.
- At the center: he sees two big buttons → `Login` and `Register`.
- At the top-right corner, he notices a language switch: `Français 🇫🇷 / English 🇬🇧`.
- He clicks `Français` — the whole UI switches to French.
- He clicks `Register`.

---

### 🧩 Scene 2 – Registering an Account

- The `Register` page opens.
- Fields: Name, Email, Password.
- Amine enters:
  - Name: `Amine`
  - Email: `amine@gmail.com`
  - Password: `12345678`
- He clicks `Submit`.
- Request is sent to `POST /auth/register`.
- ✅ Backend hashes the password, stores the user.
- 🎉 He sees: "Account created! Please log in."

---

### 🧩 Scene 3 – Logging In

- He’s redirected to `Login` page.
- Enters:
  - Email: `amine@gmail.com`
  - Password: `12345678`
- Clicks `Login`.
- Request sent to `POST /auth/login`.
- ✅ JWT is returned.
- 🧠 Frontend stores JWT in memory (or localStorage).
- User is redirected to: `/app`

---

### 🧩 Scene 4 – Main App (`/app`)

- The screen is split:
  - **Left side** → A welcome message from the chatbot:
    > "🎬 Welcome, Amine! Looking for your next movie?"
  - **Right side** → Empty movie grid (waiting for a query).

- He types into the Chat:
  > “Show me a sci-fi movie with good reviews”

---

### 🧩 Scene 5 – Backend Processing Begins

**Request goes to:** `POST /chat`  
Payload:
```json
{
  "session_id": "12ae3f1b-89f2-4c6e-bb1e-b8f6f4a231bd",
  "message": "Show me a sci-fi movie with good reviews"
}
```
Auth: JWT token attached

---



#### 🔧 Backend flow (inside `/chat`):

1. ✅ **JWT is decoded**, and `user_id` is extracted.

2. ✅ **Session check**:
   - If `session_id` exists → retrieve it (used for multi-turn context).
   - If it doesn’t exist or is invalid → raise an error or create a new session.

---

3. 🧠 **LLM is called** using the user’s message.  
Function: `get_llm_completion(message: str) → str`  
The prompt uses a predefined template, like:

```
You are a movie assistant. Ask the user what kind of movie they'd like to watch. You can suggest genres, ratings, release dates, or any preferences.

When the user provides filters, you MUST append a new line to your message starting with:

[filters_requested] genre: ..., min_release_date: ..., min_imdb_rating: ..., language: ...

Only use this format if you're confident the user provided filters.
```

---
4. 🧾 **LLM response is parsed**:
   - We split the response by lines and check if **the last line** starts with `[filters_requested]`.
   - ✅ If the flag exists:
     - The rest of the line is parsed into a `MovieSearchFilter` object.
     - The movies are fetched via `get_filtered_movies()`.
     - A `[movie_context]` assistant message is created *silently*, containing:
       ```
       [movie_context]
       1. Interstellar – IMDb 8.6 – A team of explorers travels through a wormhole...
       2. Arrival – IMDb 7.9 – A linguist helps humans communicate with aliens...
       ```
     - This message is **injected into the conversation**, but **not returned to the frontend** (it’s backend-only memory).
     - The **chat response includes**:
       - `llm_response` (the message before the `[filters_requested]` line)
       - `movies` (filtered list)
       - `update_movies = True`
   - ❌ If no `[filters_requested]` flag is present:
     - We only return the `llm_response` (entire message)
     - Set `movies = []`
     - Set `update_movies = False`



5. ✂️ **Conversation Pruning – Send Only Relevant Context to the LLM**

To prevent the LLM from being overwhelmed by long history or outdated movie suggestions, we apply **context pruning** *only when preparing the messages sent to the LLM*.  
**Important**: We never delete messages from the database — only from the current payload.

---

### 🧠 Strategy:

- When a new `[filters_requested]` flag is detected:
  1. Fetch a new movie list.
  2. Inject a `[movie_context]` assistant message (containing movie summaries).
  3. **Before sending to the LLM**:
     - Look for the **last `[movie_context]`** message in the `messages` list.
     - **Only include messages from after that point onward** (i.e., drop earlier turns from the LLM payload).
     - Append the new `[movie_context]` at the end of this filtered list.
  4. This trimmed list is what gets sent to `get_llm_completion()`.

---

6. 🔁 **Return `ChatResponse`** to frontend:
```json
{
  "message": "Sure! Would you like something more action-packed or romantic?",
  "movies": [],
  "update_movies": false
}
```
or:
```json
{
  "message": "How about a great comedy? Here's what I found for you:",
  "movies": [ ...MovieCard list... ],
  "update_movies": true
}
```