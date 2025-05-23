from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired


class RegistrationForm(FlaskForm):
    email = StringField('Введите адресс электронной почты', validators=[DataRequired()])
    login = StringField('Введите логин', validators=[DataRequired()])
    password = PasswordField('Введите пароль', validators=[DataRequired()])
    password_repeat = PasswordField('Повторите пароль', validators=[DataRequired()])
    submit = SubmitField('Зарегистрироваться')