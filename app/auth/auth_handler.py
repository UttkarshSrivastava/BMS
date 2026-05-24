from datetime import datetime, timedelta
import jwt

from app.config.setting import SECRET_KEY, ALGORITHM


def create_token(data: dict):

    payload = data.copy()

    payload["exp"] = datetime.utcnow() + timedelta(hours=10)

    token = jwt.encode(
        payload,
        SECRET_KEY,
        algorithm=ALGORITHM
    )

    return token


def verify_token(token: str):

    try:

        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM]
        )

        return payload

    except jwt.ExpiredSignatureError:

        raise Exception("Token expired")

    except jwt.InvalidTokenError:

        raise Exception("Invalid token")