from app.backend.schemas.chat_schemas import ChatQuery, ChatResponse
from sqlalchemy.orm import Session
from app.backend.models.user_model import User

from app.backend.services.session_service import get_or_create_chat_session
from app.backend.services.llm_service import get_llm_response, parse_llm_response
from app.backend.services.movie_service import recommend_movies, recommend_similar_movies


def process_chat_query(payload: ChatQuery, user: User, database: Session, language:str) -> ChatResponse:
    # Get Chat Session from db:
    chat_session = get_or_create_chat_session(user.id, payload.session_id, database)

    # Append user's message to the chat_session:
    chat_session.conversation.append({"role": "user", "content": payload.query})

    print("user's message : ", payload.query)
    # get llm completion:
    llm_response = get_llm_response(chat_session.conversation)
    print("LLM's Answer : ", llm_response)

    # Scan llm completion for actionnable flags.
    cleaned_llm_completion, action, movie_name, filters = parse_llm_response(llm_response)
    print("Cleaned LLM Completion:", cleaned_llm_completion)
    print("Action:", action)
    print("Movie Name:", movie_name)
    print("Filters:", filters)

    # Append llm's Response to the chat_session:
    chat_session.conversation.append(
        {"role": "assistant", "content": cleaned_llm_completion}
    )
    # Commit BEFORE returning
    database.commit()

    if action == "filters":

        recommended_movies = recommend_movies(filters, user.id, database, language)
        return ChatResponse(
            message=cleaned_llm_completion,
            movies=recommended_movies,
            filters=filters)

    elif action == "similar_movie":

        similar_movies = recommend_similar_movies(movie_name, user.id, database, language)
        return ChatResponse(
            message=cleaned_llm_completion,
            movies=similar_movies,
            filters=filters)


    database.commit()
    return ChatResponse(
        message=cleaned_llm_completion,
        movies=None,
        filters=None)
