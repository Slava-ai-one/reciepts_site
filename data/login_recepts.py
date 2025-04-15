from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired


class LoginForm(FlaskForm):
    name = StringField('Введите логин', validators=[DataRequired()])
    password = PasswordField('Введите пароль', validators=[DataRequired()])
    submit = SubmitField('Войти')