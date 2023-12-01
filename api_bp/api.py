from flask import Blueprint, jsonify, current_app, request, abort, make_response
from models import User, Product
import jwt
from datetime import datetime, timedelta, timezone
from .decorator import token_required
from flask_login import login_required
import json
api_bp = Blueprint("api", __name__, template_folder="templates", static_folder="static")  # создаем объект Blueprint


@api_bp.route('/')
def api_index():
    """
    Функция обработчик адреса /api/
    """
    return jsonify({"status": 200})


@api_bp.route('/get_products')
@login_required
def get_products():
    """
    Функция обработчик адреса /api/get_products
    Нужна авторизация по токену
    :return: словарь товаров из бд в формате json
    """
    products = Product.query.all()  # получаем список товаров из бд
    result = {}  # создаем пустой словарь result
    for product in products:  # заполняем словарь result
        result[product.id] = {"name": product.name,
                              "price": product.price}
    
    json_result = {"products": result}
    response = jsonify(json_result)

    # Используйте json.dumps с ensure_ascii=False
    response.data = json.dumps(response.json, ensure_ascii=False)

    response.headers['Content-Type'] = 'application/json; charset=utf-8'
    return response


@api_bp.route('/get_user', methods=["GET", "POST"])
@login_required
def get_user():
    """
        Функция обработчик адреса /api/get_users
        Нужна авторизация по токену
        Принимает id пользователя из тела запроса в формате json,
        TODO: проверка админской роли или чтобы пользователь мог получить только данные о себе

        :return: данные о пользователе
        """
    if request.method == "POST":  # проверяем метод
        user_id = request.json.get("id")  # получаем id пользователя из json
        user = User.query.filter(User.id == user_id).first()  # получаем пользователя с таким id из бд
        result = {
            user.id: {
                "name": user.name,
                "email": user.email,
                "role": user.role,
                "orders": [order.id for order in user.orders]
            }
        }  # формируем ответ в виде словаря
        return jsonify(result)
    return abort(405)


@api_bp.route('/auth', methods=["GET", "POST"])
def auth():
    """
    Функция-обработчик адреса /api/auth
    Принимает от клиента email и password из json
    :return: json с токеном или 405 статус код если обратились по методу GET
    """
    if request.method == "POST":
        email = request.json.get("email")  # получаем email пользователя из json
        password = request.json.get("password")  # получаем password пользователя из json
        exp = datetime.now(tz=timezone.utc) + timedelta(hours=1)  # устанавливаем срок окончания токена 1 час
        token = jwt.encode(dict(email=email, password=password, exp=exp), current_app.secret_key, algorithm="HS256")  # генерируем токен, передаем нагрузку, секретный ключ и метод
        return {"status": "token generated successfully", "token": token}
    return abort(405)
