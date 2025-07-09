from fastapi import APIRouter, status, Depends
from app.backend.schemas.chat import ChatRequest, ChatResponse
from sqlalchemy.orm import Session
from app.backend.core.database import get_db
from app.backend.models.user import User
from app.backend.core.dependancies import get_current_user
from app.backend.services.session_service import get_or_create_chat_session
from app.backend.services.llm_service import prune_conversation_for_llm, get_llm_response, parse_llm_response, movies_to_overviews_text
from app.backend.services.movie_service import recommend_movies


router = APIRouter()

@router.post("/chat", response_model= ChatResponse)
def chat(payload: ChatRequest, user : User = Depends(get_current_user), database: Session = Depends(get_db)):

    # Get Chat Session from db:
    chat_session = get_or_create_chat_session(user.id, payload.session_id, database)

    # Append user's message to the chat_session:
    chat_session.conversation.append({"role" : "user", "content" : payload.message})

    # Prune messages up to remove previous movies list :
    pruned_conversation = prune_conversation_for_llm(chat_session.conversation)

    # get llm completion:
    llm_response = get_llm_response(pruned_conversation)

    # Scan llm completion for actionnable flags.
    action, filters, cleaned_llm_completion = parse_llm_response(llm_response)

    # Append llm's Response to the chat_session:
    chat_session.conversation.append({"role" : "assistant", "content" : cleaned_llm_completion})

    update_movie_panel = False
    recommended_movies = []
    
    
    if action == "filters_requested":

        # set update_movie_panel to True
        update_movie_panel = True

        # Fetch Recommended Movie Based on user's filters
        recommended_movies = recommend_movies(filters, user.id, database)

        # Append invisible [movie_context] assistant message
        movie_context_msg = movies_to_overviews_text(recommended_movies)
        chat_session.conversation.append({"role": "assistant", "content": movie_context_msg})


    return ChatResponse(
        response=cleaned_llm_completion,
        update_movie_panel=update_movie_panel , 
        recommended_movies=recommended_movies)







    