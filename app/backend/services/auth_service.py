from app.backend.models.user import User
from sqlalchemy import exists
from app.backend.core.security import hash_password


def register_user(user_data, database):

    # Check if email Already Exists in db
    email_already_exists = database.query(exists().where(User.email == user_data.email)).scalar()

    # if yes send error
    if email_already_exists :
        return False, "Email Already Exists"
    
    # Load the password code Hasher thing
    hashed_password = hash_password(user_data.password)

    # if all is good inject user into the database
    new_user = User(
        first_name= user_data.first_name,
        last_name= user_data.last_name,
        email= user_data.email,
        password_hash= hashed_password
    )

    database.add(new_user)
    database.commit()

    return True, "User Added Successfully"



def login_user(user_data, database):

    # Load the password Hashed thing 
    hashed_password = hash_password(user_data.password)

    # Search for user's credentials in the database ... 
    Credentials_valid = database.query(exists().where(User.email == user_data_))



    # If match then return a token 


    return "hi"