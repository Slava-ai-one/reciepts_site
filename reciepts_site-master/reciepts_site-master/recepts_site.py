from flask import Flask, url_for, request, render_template, redirect, url_for, flash
from random import randint
import os
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
app.config["Upload_folder"] = "static/img"


@app.route('/')
def main():
    res = []
    if len(db_recepts_session.create_session().query(recept_table.Recepts.id).all()) != 0:
        for _ in range(3):
            x = randint(1, len(db_recepts_session.create_session().query(recept_table.Recepts.id).all()))
            ans = db_recepts_session.create_session().query(recept_table.Recepts).filter(recept_table.Recepts.id == x).first()
            with open(f"{ans.content}", mode='r') as f:
                b = f.readlines()
                ans.content = ''.join(b)
            res.append(ans)
        print(res)
        return render_template('main_page.html', title='Главная страница', rec=res)
    else:
        return render_template('main_page.html', title='Главная страница')

@app.route('/recept_page/<data>')
def recept_page(data):
    ans = db_recepts_session.create_session().query(recept_table.Recepts).filter(recept_table.Recepts.id == data).first()
    with open(f"{ans.content}", mode='r') as f:
        b = f.readlines()
        ans.content = ''.join(b)
    return render_template('recept_page.html', title=ans.title, rec=ans)


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
    count = len(db_recepts_session.create_session().query(recept_table.Recepts.id).all()) + 1
    if request.method == 'GET':
        return render_template('create_recept_page.html', title='Создание рецепта', count=count)
    elif request.method == 'POST':
        rec = [request.form.get(f"name_recept{count}"), request.form.get(f"description_recept{count}"),
               request.form.get(f"recept{count}"), request.form.get(f"categories{count}")]
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        # If the user does not select a file, the browser submits an
        # empty file without a filename.
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file:
            filename = f"hero_file{count}.png"
            file.save(os.path.join(app.config['Upload_folder'], filename))
        print(rec)
        recept = recept_table.Recepts()
        recept.title = rec[0]
        recept.discription = rec[1]
        recept.way_to_image = f"/static/img/hero_file{count}.png"
        recept.category_tags = rec[3]
        recept.user_id = db_recepts_session.create_session().query(users_table_recepts.User.id).filter(
            users_table_recepts.User.name == data).first()[0]
        with open(f'static/text_files/text_recept_{count}', mode='w') as f:
            f.write('\n'.join(rec[2].split('\r\n')))
        recept.content = f'static/text_files/text_recept_{count}'

        db_sess = db_recepts_session.create_session()
        db_sess.add(recept)
        db_sess.commit()
        return redirect(location=f"/autorizated_main_page/{data}")


@app.route('/autorizated_main_page/<data>')
def main_autorized(data):
    res = []
    if len(db_recepts_session.create_session().query(recept_table.Recepts.id).all()) != 0:
        for _ in range(3):
            x = randint(1, len(db_recepts_session.create_session().query(recept_table.Recepts.id).all()))
            ans = db_recepts_session.create_session().query(recept_table.Recepts).filter(
                recept_table.Recepts.id == x).first()
            with open(f"{ans.content}", mode='r') as f:
                b = f.readlines()
                ans.content = ''.join(b)
            res.append(ans)
        user = db_recepts_session.create_session().query(users_table_recepts.User).filter(
            users_table_recepts.User.name == data).first()
        name = '%20'.join(user.name.split())
        return render_template('main_page_autorization.html', title='Главная страница', name=user.name,
                           email=user.email, acc=f"/account/{name}", cre=f"/create_recept/{name}", rec=res)
    else:
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
