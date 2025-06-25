from fastapi import APIRouter


router = APIRouter(prefix="/auth")


@router.post("/register")
def register():
    return {"message" : "register"}


@router.post("/login")
def login():
    return {"message" : "Login"}
