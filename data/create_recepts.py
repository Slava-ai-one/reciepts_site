from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, IntegerField
from wtforms.validators import DataRequired


class CreationForm(FlaskForm):
    count = IntegerField(validators=[DataRequired()], default=1)
    submit = SubmitField('Установить')
