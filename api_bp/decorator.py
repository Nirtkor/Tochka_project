import jwt
from flask import request, abort, current_app
from models import User
from werkzeug.security import check_password_hash
from functools import wraps


def token_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        """
        Декоратор для авторизации пользователя по токену.
        Проверяет:
        Есть ли заголовок "Authorization";
        Существует ли токен;
        Валидный ли токен;
        Дату окончания срока токена;
        Есть ли пользователь;
        Совпадает ли пароль;
        """
        if "Authorization" in request.headers:  # Есть ли заголовок "Authorization"
            token = request.headers.get("Authorization")  # получаем токен из заголовков запроса
            if token:  # существует ли токен
                try:
                    data = jwt.decode(token, current_app.secret_key, algorithms=["HS256"])  # декодируем токен
                    user = User.query.filter(
                        User.email == data["email"]).first()  # получаем пользователя с email из токена
                    if not user:  # если пользователя не нашло
                        return {"message": "user not found"}, 401
                    if not check_password_hash(user.password, data["password"]):  # если пароль не совпадает
                        return {"message": "password invalid"}, 401

                except Exception as e:  # срабатывает если токен не валидный или время срока действия токена истекло
                    return {"message": "Invalid token", "error": str(e)}, 401
            else:  # срабатывает если токена нет
                return {"message": "Authentication token required"}, 401
        else:  # срабатывает если нет заголовка авторизации
            return {"message": "Authorization required"}, 401

        return func(*args, **kwargs)  # вызываем нашу оборачиваемую функцию

    return wrapper  # возвращаем объект обертки(если не понимаете зачем почитайте как работают декораторы)
