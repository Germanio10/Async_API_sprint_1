from models.utils import BaseOrjsonModel


class User(BaseOrjsonModel):
    user_id: str | None = None
    role_id: int | str | None = None
