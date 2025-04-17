from flask import Flask, url_for, request, render_template, redirect
from random import randint
import json
from data.login_recepts import LoginForm
from data.registration_recepts import RegistrationForm
from data import db_recepts_session
from data import users_table_recepts
from data import create_recepts
from data import recept_table

db_recepts_session.global_init("db/blogs.db")
app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'


@app.route('/')
def main():
    return render_template('main_page.html', title='Главная страница')


@app.route('/account/<data>')
def account(data):
    try:
        user = db_recepts_session.create_session().query(users_table_recepts.User).filter(
            users_table_recepts.User.name == data).first()
        if not user:
            raise SyntaxError
        return render_template('account_page.html', title='Аккаунт')
    except Exception:
        return render_template('main_page.html', title='Главная страница',
                               message=f'Кажется, вы не в аккаунте.')


#@app.route('/chose_count/<data>', methods=['POST', 'GET'])
#def chose_count(data):
#    form = create_recepts.CreationForm()
#    key = ['q', 'w', 'e', 'r', 't', 'y', 'u', 'i', 'o', 'p', 'a', 's', 'd', 'f', 'g', 'h', 'j', 'k', 'l', 'z', 'x', 'c',
#           'v', 'b', 'n', 'm', ',', '.', ';', '[', ']', '{', '}']
#    if form.validate_on_submit():
#        count = []
#        for _ in range(int(form.count.data)):
#            count.append(key[randint(0, len(key))])
#        return redirect(f'/create_recept/{''.join(count)}')
#    return render_template('chose_count.html', title='Выбор количества шагов', form=form)


@app.route('/create_recept/<data>', methods=['POST', 'GET'])
def create_recept(data):
    count = len(db_recepts_session.create_session().query(recept_table.Recepts.id).all())
    if request.method == 'GET':
        return render_template('create_recept_page.html', title='Создание рецепта', count=count)
    elif request.method == 'POST':
        rec = request.form.get('asd')
        print(rec)


@app.route('/autorizated_main_page/<data>')
def main_autorized(data):
    user = db_recepts_session.create_session().query(users_table_recepts.User).filter(
        users_table_recepts.User.name == data).first()
    name = '%20'.join(user.name.split())
    return render_template('main_page_autorization.html', title='Главная страница', name=user.name,
                           email=user.email, acc=f"/account/{name}", cre=f"/create_recept/{name}")


@app.route('/login', methods=['GET', 'POST'])
def pain():
    form = LoginForm()
    if form.validate_on_submit():
        if (form.name.data,) not in db_recepts_session.create_session().query(users_table_recepts.User.name).all():
            return render_template('login_recepts.html', form=form, title='Вход в аккаунт',
                                   message='Такого пользователя не существует')
        elif not db_recepts_session.create_session().query(users_table_recepts.User).filter(
                users_table_recepts.User.name == form.name.data).first().check_password(form.password.data):
            return render_template('login_recepts.html', form=form, title='Вход в аккаунт',
                                   message='Неверный пароль или логин')
        elif db_recepts_session.create_session().query(users_table_recepts.User).filter(
                users_table_recepts.User.name == form.name.data).first().check_password(form.password.data):
            user = db_recepts_session.create_session().query(users_table_recepts.User).filter(
                users_table_recepts.User.name == form.name.data).first()
            # return render_template('main_page_autorization.html', title='Главная страница', name=user.name,
            #                       email=user.email)
            return redirect(location=f"/autorizated_main_page/{user.name}")
    return render_template('login_recepts.html', form=form, title='Вход в аккаунт')


@app.route('/registration', methods=['GET', 'POST'])
def sain():
    user = users_table_recepts.User()
    form = RegistrationForm()
    if form.validate_on_submit():
        if form.password_repeat.data != form.password.data:
            return render_template('registration_recepts.html', form=form, title='Регистрация',
                                   message='Пароли не совпадают')
        elif (form.login.data,) in db_recepts_session.create_session().query(users_table_recepts.User.name).all():
            return render_template('registration_recepts.html', form=form, title='Регистрация',
                                   message='Такой пользователь уже существует')
        elif (form.email.data,) in db_recepts_session.create_session().query(users_table_recepts.User.email).all():
            return render_template('registration_recepts.html', form=form, title='Регистрация',
                                   message='Такой адресс почты уже используется')
        else:
            print()
            user.name = form.login.data
            user.email = form.email.data
            user.set_password(form.password.data)
            user.is_admin = False
            db_sess = db_recepts_session.create_session()
            db_sess.add(user)
            db_sess.commit()
            return redirect(location=f"/autorizated_main_page/{user.name}")
    return render_template('registration_recepts.html', form=form, title='Регистрация')


@app.route('/registration/3224252', methods=['GET', 'POST'])
def adain():
    user = users_table_recepts.User()
    form = RegistrationForm()
    if form.validate_on_submit():
        if form.password_repeat.data != form.password.data:
            return render_template('registration_recepts.html', form=form, title='Регистрация',
                                   message='Пароли не совпадают')
        elif (form.login.data,) in db_recepts_session.create_session().query(users_table_recepts.User.name).all():
            return render_template('registration_recepts.html', form=form, title='Регистрация',
                                   message='Такой пользователь уже существует')
        elif (form.email.data,) in db_recepts_session.create_session().query(users_table_recepts.User.email).all():
            return render_template('registration_recepts.html', form=form, title='Регистрация',
                                   message='Такой адресс почты уже используется')
        else:
            print()
            user.name = form.login.data
            user.email = form.email.data
            user.set_password(form.password.data)
            user.is_admin = True
            db_sess = db_recepts_session.create_session()
            db_sess.add(user)
            db_sess.commit()
            return redirect(location=f"/autorizated_main_page/{user.name}")
    return render_template('registration_recepts.html', form=form, title='Регистрация')


if __name__ == '__main__':
    app.run(port=8080, host='127.0.0.1')
