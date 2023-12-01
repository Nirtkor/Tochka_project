import flask_admin as fladmin
import flask_login as login
from flask import redirect, url_for
from flask_admin import helpers, expose
from models import User, Reservation
from flask_admin.contrib.sqla import ModelView


class MyAdminIndexView(fladmin.AdminIndexView):
    """
    Overriding of Admin index view
    """

    @expose('/')
    def index(self):
        """
        Authorization for '/admin' panel
        :return: redirect to '/login' if user not logged in or his role not Admin
        """
        if not login.current_user.is_authenticated:  # если пользователь не авторизован то сразу переадресовываем на логин
            return redirect(url_for('login'))
        else:
            admin = User.query.filter(User.id == login.current_user.get_id()).first()
            if admin.role_id == 1:  # проверяем роль текущего пользователя, если она админ отдаем страницу
                return super(MyAdminIndexView, self).index()
            return redirect(url_for('login'))


class MyModelView(ModelView):
    """
    Overriding of base ModelView to add authentication for other admin paths
    """
    column_hide_backrefs = False

    def is_accessible(self):
        """
        This method used to check if the current user is authenticated and their role is Admin
        :return: True if accessible, otherwise False
        """
        if not login.current_user.is_authenticated:
            return False
        
        # Предполагаем, что роль администратора имеет id = 1
        return login.current_user.role_id == 1

class UserView(MyModelView):

    
    column_list = ["id", "name", "email", "role", "reservations"]  # Обновлено для соответствия модели User
    column_searchable_list = ["name", "email"]  # Делаем колонки name и email доступными для поиска
    column_sortable_list = ["name", "email"]  # Делаем колонки name и email сортируемыми

class ReservationView(MyModelView):
    """
    View for '/admin/reservation'
    """

    column_list = ["id", "user_id", "date", "status", "total"]  # Обновлено для соответствия модели Reservation
    column_searchable_list = ["date"]  # делаем колонку date доступной для поиска
    column_sortable_list = ["date"]  # делаем колонку date сортируемой


class ProductsView(MyModelView):
    """
    View for '/admin/products'
    """

    column_list = ["id", "name", "description", "price"]  # Обновлено для соответствия модели Product
    column_searchable_list = ["name", "price"]  # делаем колонки name и price доступными для поиска
    column_sortable_list = ["name", "price"]  # делаем колонки name и price сортируемыми

