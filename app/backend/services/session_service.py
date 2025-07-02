from app.backend.models.chat_session import ChatSession
from sqlalchemy.orm import Session



def get_or_create_chat_session(user_id: int, session_id : str, database: Session) -> ChatSession:

    existing_session = database.query(ChatSession).filter(
        ChatSession.user_id == user_id,
        ChatSession.id == session_id 
    ).first()

    if existing_session:
        return existing_session
    
    else : 
        try :
            new_session = ChatSession(id=session_id, user_id=user_id, conversation=[])
            database.add(new_session) 
            database.commit()   
            return new_session
        
        except Exception as e:
            database.rollback()

