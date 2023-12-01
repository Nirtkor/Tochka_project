from flask import Flask, render_template, url_for, request, redirect, flash, get_flashed_messages, session, \
    make_response, Response, jsonify
from models import db, User, Roles, Reservation, Product
from flask_login import LoginManager, login_user, current_user, login_required, logout_user
from werkzeug.security import generate_password_hash, check_password_hash
import os
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_mail import Mail, Message
from datetime import datetime
from flask_admin import Admin
from adminview import MyAdminIndexView, ReservationView, MyModelView, ProductsView
from api_bp.api import api_bp
from sqlalchemy import or_
from email.mime.text import MIMEText
from email.header import Header
import smtplib

app = Flask(__name__)  # инициализируем экземпляр нашего приложения
app.secret_key = "123123412341234asdasd"  # задаем секретный ключ, нужен для сессий, логина и некоторых других модулей

# -----------------Прописываем конфигурацию нашего приложения(лучше это вынести в отдельный файл config) ---------------

# в конфиг приложения прописываем путь до базы данных в формате driver://username:password@adress:port(если нужен)/имяБД
app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql://admin:admin@localhost:5432/postgres"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # отключаем автоматическое отслеживание изменений в метаданных

app.config['MAIL_SERVER'] = "smtp.gmail.com"  # указываем адрес smtp сервера(берется из инструкции по настройке smtp например гугла или майла)
app.config['MAIL_PORT'] = 587  # указываем порт для smtp
app.config['MAIL_USE_TLS'] = True  # указываем что будем использовать TLS
app.config['SENDER_EMAIL'] = os.environ.get('creativespace.tochka@gmail.com')  # здесь прописываем логин от почты с которой будем отправлять письма
app.config['SENDER_PASSWORD'] = os.environ.get('hkgu aeaj fnzm jcnd')  # здесь прописываем токен который получаем при регистрации нашего приложения в почтовом клиенте
app.config['MAIL_DEFAULT_SENDER'] = os.environ.get('Test')  # устанавливаем отправителя по умолчанию == username

app.config['FLASK_ADMIN_SWATCH'] = 'Darkly'  # устанавливаем тему админки(можно выбрать тут https://bootswatch.com/3/)
# ----------------------------------------------------------------------------------------------------------------------

# ---------------------- создаем сущности для работы модулей(лучше вынести в отдельный файл __init__.py) ---------------
db.init_app(app)  # инициализируем приложение в бд

mail = Mail(app)  # создаем сущность для работы с почтой

login_manager = LoginManager()  # сущность для работы flask-login
login_manager.init_app(app)  # инициализируем приложение для flask-login

admin = Admin(app, index_view=MyAdminIndexView(url='/admin'), name='ExampleStore',
              template_mode='bootstrap3')  # сущность для работы админки
admin.add_view(MyModelView(User, db.session))  # добавляем ModelView для вкладки User в админке(Из файла adminview.py)
admin.add_view(ReservationView(Reservation, db.session))  # ModelView для вкладки Order(Из файла adminview.py)
admin.add_view(ProductsView(Product, db.session))  # ModelView для вкладки Order(Из файла adminview.py)

migrate = Migrate(app, db)

app.register_blueprint(api_bp, url_prefix="/api")# регистрируем blueprint api в нашем приложении


# ----------------------------------------------------------------------------------------------------------------------


@login_manager.user_loader
def load_user(user_id):
    """
    Callback-функция для возврата текущего пользователя
    Вызывается автоматически когда мы обращаемся к текущему пользователю
    Нужна для работа flask-login.

    :param user_id: id пользователя
    :return: Объект пользователя из бд с id == user_id
    """
    return User.query.filter(User.id == user_id).first()


# ----------------------------- Далее идут функции-представления для маршрутов приложения ------------------------------


@app.route('/home')
@app.route("/index/")
@app.route('/')
def index():
    """
    Функция-обработчик адресов домашней страницы

    :return: страницу index.html
    """
    session.modified = True
    return render_template('index.html')


@login_required
@app.route('/about')
def about():
    """
    Функция-обработчик адреса страницы about.
    Для демонстрации декоратора @login_required выдается только после авторизации

    :return: страницу about.html
    """
    return render_template('about.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    """
    Функция-обработчик адреса авторизации

    :return: Если обратились по методу GET отдаем страницу sign_in.html, если по методу POST:
    перенаправляет на себя же в случае не успешной авторизации,
    перенаправляет на index в случае успешной авторизации,
    перенаправляет на admin в случае входа под админом
    """
    if request.method == 'POST':  # проверяем метод по которому запрашивается страница
        email = request.form.get('email')  # берем данные из поля email формы
        password = request.form.get('password')  # берем данные из поля password формы
        try:
            # обращаемся в бд, получаем пользователя по id, если к бд не подключает или пользователя с таким email нет, срабатывает except
            user = User.query.filter(User.email == email).one()
        except:
            # если сработал, выдаем flash-сообщение и переадресовываем на себя же
            flash("Пользователь с указанным логин/паролем не найден")
            return redirect("/login")
        if check_password_hash(user.password, password):
            # если пользователя нашли, проверяем совпадают ли хеш пароля из бд с хешом пароля из поля формы
            if user.role_id == 3 or 2:
                # если роль пользователя просто user(id == 2), то авторизовываем во flask-login и переадресовываем на /
                login_user(user)
                return render_template('catalog.html')
            else:
                # если роль пользователя admin(id == 1), то авторизовываем во flask-login и переадресовываем на /admin
                login_user(user)
                return redirect('/admin')
        else:
            # если хэши паролей не совпали, выдаем flash-сообщение и переадресовываем на себя же
            flash("Пользователь с указанным логин/паролем не найден")
            return redirect('/login')
    return render_template('sign_in.html')  # Если пользователь обратился по методу GET рисуем страницу sign_in




@app.route("/logout")
@login_required
def logout():
    """
    Функция-обработчик адреса logout
    завершает сессию пользователя

    :return:  перенаправляет на index
    """
    logout_user()  # вызываем функцию из flask-login
    return redirect("/index")  # переадресовываем на индекс


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    """
    Функция-обработчик адреса регистрации

    :return: signup.html если обратились по методу GET,если обратились по методу POST:
    перенаправляет на login в случае успешной регистрации,
    в случае не успешной регистрации выводит надпись "Добавление не удалось"
    """
    if request.method == 'POST':  # проверяем метод по которому запрашивается страница
        name = request.form.get("name")  # берем данные из поля name формы
        email = request.form.get("email")  # берем данные из поля email формы
        password = request.form.get("password")  # берем данные из поля password формы
        password = generate_password_hash(password)  # генерируем хэш пароля
        new_user = User(name=name, email=email, password=password, role_id = 3)  # создаем новый объект пользователя
        try:
            db.session.add(new_user)  # добавляем пользователя в метаданные
            db.session.commit()  # выполняем коммит в базу
            return redirect("/login")  # если код выше сработал перенаправляем на логин
        except:
            # если сработал выводим надпись что добавление не удалось
            return "Добавление не удалось"
    else:  # если метод GET рисуем страницу signup
        return render_template('signup.html')

@app.route('/contact', methods=['POST'])
def contact():
        name = request.form.get('name')
        email = request.form.get('email')
        message = request.form.get('message')

        if name is None or email is None:
            return jsonify({'success': False, 'error': 'Missing required parameters'}), 400

        sender_email = 'creativespace.tochka@gmail.com'
        sender_password = 'hkgu aeaj fnzm jcnd'
        admin_email = 'creativespace.tochka@gmail.com'

        message_to_admin = f"Новый клиент\nИмя - {name}\nEmail - {email}\n Сообщение - {message}"
        message_to_client = f"Уважаемый, {name} мы совсем скоро с вами свяжемся."

        mime_client = MIMEText(message_to_client, 'plain', 'utf-8')
        mime_admin = MIMEText(message_to_admin, 'plain', 'utf-8')
        mime_admin['Subject'] = Header("Новый клиент", 'utf-8')
        mime_client['Subject'] = Header("Ваше обращение зарегистрировано", 'utf-8')
    
        try:
            with smtplib.SMTP('smtp.gmail.com', 587) as smtp:
                smtp.starttls()
                smtp.login(sender_email, sender_password)
                smtp.sendmail(sender_email, admin_email, mime_admin.as_string().encode('utf-8'))
                smtp.sendmail(sender_email, email, mime_client.as_string().encode('utf-8'))
                flash('Ваше обращение принято в работу!', 'success')
                return redirect(url_for('index'))
            
        except Exception as e:
            print(f'Произошла ошибка при отправке почты: {str(e)}')
            return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/catalog')
def catalog():
    """
    Функция-обработчик адреса /catalog
    Выводит товары на страницу catalog.html

    :return: страницу catalog.html со списком товаров
    """
    products = Product.query.all()  # Получаем все товары из бд(соответствует select * from products)
    return render_template('catalog.html',
                           products=products)  # отдаем страницу catalog.html, товары лежат в списке products

@app.route('/filter_and_search', methods=['GET'])
def filter_and_search():
    query = request.args.get('query', '')
    sort_option = request.args.get('sort', 'asc')
    products = Product.query.filter(or_(Product.name.ilike(f'%{query}%'), Product.description.ilike(f'%{query}%')))

    if sort_option == 'asc':
        products = products.order_by(Product.price.asc())
    elif sort_option == 'desc':
        products = products.order_by(Product.price.desc())
    elif sort_option == 'area':
        products = products.order_by(Product.area.asc())
    elif sort_option == 'capacity':
        products = products.order_by(Product.capacity.asc())

    products = products.all()

    return render_template('catalog.html', products=products)

@app.route('/item/<int:product_id>', methods=['GET', 'POST'])
def show_item(product_id: int):
    """
    Функция-обработчик страницы конкретного товара

    :param product_id: id продукта страницу которого необходимо вывести
    :return: Страницу конкретного товара с темплейтом item.html
    или 404 код в случае если пользователь перешел не с каталога
    """
    if request.method == 'POST':  # если обратились по POST запросу значит запрос шел с кнопки на странице каталога
        item = Product.query.filter(Product.id == product_id).first()  # получаем продукт по id
        return render_template('item.html', item=item)  # отдаем страницу item.html с продуктом в переменной item
    return Response("Данную страницу можно посетить только после посещения каталога",
                    404)  # в случае обращения по методу GET отдаем 404 статус код с сообщением


# @app.route("/make_order")
# def make_order():
#     """
#     Функция для создания заказа в базе данных.
#     Перед отправкой заказа пользователю необходимо авторизоваться
#     Создает запись в БД в таблице Orders
#     :return: Оставляет запись в таблице Orders и переадресовывает на индекс если успешно,
#     либо переадресовывает на login если пользователь не авторизовался
#     """
#     if "Cart" in session and session["Cart"]["total"] != 0:  # проверяем что корзина есть и она не пустая
#         if current_user.is_authenticated:  # проверяем авторизовался ли пользователь
#             new_order = Order(user_id=current_user.get_id(),
#                               date=datetime.now(),
#                               total=session["Cart"]["total"])  # создаем объект заказа с текущей датой и стоимостью из сессии
#             for product_id in session["Cart"]["items"]:  # проходимся по id продуктов в сессии
#                 for i in range(session["Cart"]["items"][product_id]["qty"]):  # формируем range(количество товара в корзине) чтобы добавить несколько одинаковых товаров в заказ
#                     product = Products.query.filter(Products.id == product_id).first()  # получаем объект товара из бд
#                     new_order.cart.append(product)  # добавляем в список cart модели Order объект товара
#             db.session.add(new_order)  # добавляем заказ в метаданные
#             db.session.commit()  # выполняем коммит в базу данных
#             return redirect('/')  # переадресовываем на индекс
#         else:
#             return redirect("/login")  # если пользователь не прошел авторизацию переадресовываем на login

@app.route('/booking', methods=['GET', 'POST'])
def booking():
    if current_user.is_authenticated:
        if request.method == 'GET':
            products = Product.query.all()
            return render_template('booking.html', products=products)
        elif request.method == 'POST':
            try:
                product_id = request.form.get('product_id')
                date = request.form.get('date')
                status = 'created'
                booking_hours = int(request.form.get('booking_hours'))
                
                product = Product.query.filter_by(id=product_id).first()
                price = product.price
                selected_date = datetime.strptime(date, "%Y-%m-%dT%H:%M")

                # Проверка, что выбранное время находится в будущем
                if selected_date < datetime.now():
                    flash('Так нельзя, сначала нужно изобрести машину времени', 'error')
                    return redirect(url_for('booking'))

                total = booking_hours * price

                reservation = Reservation(
                    user_id=current_user.id,
                    product_id=product_id,
                    date=date,
                    status=status,
                    total=total
                )

                db.session.add(reservation)
                db.session.commit()

                flash('Бронирование успешно завершено!', 'success')
            except Exception as e:
                print(f'Произошла ошибка при бронировании: {str(e)}')

            return redirect(url_for('booking'))
    else:
        flash('Вы должны войти в систему, чтобы забронировать продукт.', 'error')
        return redirect(url_for('login'))

@app.route('/moderating', methods=['GET', 'POST'])
@login_required
def moderating():
    if current_user.is_authenticated and current_user.role_id == 2 or 1:
        if request.method == 'GET':
            bookings = Reservation.query.all()
            return render_template('moderating.html', bookings=bookings)
        if request.method == 'POST':
            for booking in Reservation.query.all():
                new_status = request.form.get(f'status_{booking.id}')
                if new_status in ['created', 'confirmed', 'completed']:
                    booking.status = new_status

                if f'delete_{booking.id}' in request.form:
                    db.session.delete(booking)

            db.session.commit()  # Сохраняем изменения в базе данных
            flash('Статусы успешно обновлены', 'success')
            return redirect(url_for('moderating'))

    flash('У вас нет прав доступа к этой странице', 'error')
    return redirect(url_for('index'))

@app.route('/list_reserv', methods=['GET', 'POST'])
@login_required
def list_reserv():
    user_id = current_user.id
    user = User.query.get(user_id)

    if user:
        reservations = user.reservations
        products = [Product.query.get(reservation.product_id) for reservation in reservations]
        reservations_and_products = zip(reservations, products)

        if request.method == 'POST':
            booking_id_to_delete = request.form.get('delete_booking_id')
            
            if booking_id_to_delete:
                booking_to_delete = Reservation.query.get(booking_id_to_delete)
                
                if booking_to_delete:
                    db.session.delete(booking_to_delete)
                    db.session.commit()  # Сохраняем изменения в базе данных
                    flash('Бронирование успешно удалено', 'success')
                    return redirect(url_for('list_reserv'))

        return render_template('list_reserv.html', reservations_and_products=reservations_and_products)

    return render_template('error.html', error_message="Пользователь не найден")

@app.route('/cookies')
def cookies():
    """
    Функция для создания куки
    :return: ответ с кукой
    """
    res = make_response("Лови печеньку")  # отправляем ответ что создадим тебе куку
    res.set_cookie("Name", "Misato", max_age=60 * 60 * 24 * 365)  # добавляем куку с временем жизни 1 год
    return res


@app.route('/show_cookies')
def show():
    """
    Функция для отображения куки
    :return:
    """
    if request.cookies.get("Name"):  # проверяем есть ли кука Name
        return "Hello" + request.cookies.get("Name")
    else:
        return "Кук нет"


@app.route('/delete_cookies')
def delete_cookies():
    """
    Функция удаления куки
    :return:
    """
    res = make_response("Мы тебе удаляем куку")
    res.set_cookie("Name", "asdas", max_age=0)  # пересоздаем существующую куку с временем жизни 0
    return res

@app.route('/delete_user/<int:user_id>', methods=['POST'])
def delete_user(user_id):
    user = User.query.get(user_id)

    if user:
        db.session.delete(user)
        db.session.commit()
        return jsonify({'message': 'User successfully deleted'})
    else:
        return jsonify({'message': 'User not found'}), 404

if __name__ == "__main__":
    # with app.app_context():
    #     db.create_all()
    app.run(debug=True)  # Запускаем приложение
