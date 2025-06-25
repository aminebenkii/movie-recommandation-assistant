from fastapi import APIRouter

router = APIRouter()


@router.get("/seen")
def get_seen():
    return {"message" : "Seen Movies" }


@router.post("/seen")
def post_seen():
    return {"message" : "Already Seen movie"}