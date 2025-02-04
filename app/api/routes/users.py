# from fastapi import APIRouter
# from app.schemas.user import UserCreate, UserRead
# # from app.services.user_service import create_user, get_users

# router = APIRouter()

# @router.post("/", response_model=UserRead)
# def create_user_route(user: UserCreate):
#     return create_user(user)

# @router.get("/", response_model=list[UserRead])
# def get_users_route():
#     return get_users()
