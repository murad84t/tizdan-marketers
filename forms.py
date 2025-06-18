from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, DecimalField, SelectField
from wtforms.validators import DataRequired, NumberRange

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])

class TransactionForm(FlaskForm):
    marketer = SelectField('Marketer', coerce=int)
    amount   = DecimalField('Amount (£)', validators=[DataRequired(), NumberRange(min=0.01)])
