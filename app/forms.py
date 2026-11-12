from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, FloatField, SelectField
from wtforms.validators import DataRequired, Email, Length, EqualTo

# ------------------------------
# USER FORMS
# ------------------------------
class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=80)])
    email = StringField('Email', validators=[DataRequired(), Email(), Length(max=120)])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

#----------------------------------------
#LOGINFORM
#---------------------------------------
class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

#-----------------------------------------

# ------------------------------
# SHIPMENT FORM
# ------------------------------
class ShipmentForm(FlaskForm):
    sender_name = StringField('Sender Name', validators=[DataRequired(), Length(max=100)])
    receiver_name = StringField('Receiver Name', validators=[DataRequired(), Length(max=100)])
    origin = StringField('Origin', validators=[DataRequired(), Length(max=200)])
    destination = StringField('Destination', validators=[DataRequired(), Length(max=200)])
    submit = SubmitField('Create Shipment')


# ------------------------------
# TRACKING FORM (Admin Use)
# ------------------------------
class TrackingForm(FlaskForm):
    status = StringField('Status', validators=[DataRequired(), Length(max=100)])
    location = StringField('Location', validators=[Length(max=200)])
    submit = SubmitField('Update Tracking')


# ------------------------------
# PAYMENT FORM
# ------------------------------
class PaymentForm(FlaskForm):
    amount = FloatField('Amount', validators=[DataRequired()])
    method = SelectField('Payment Method', choices=[('card', 'Card'), ('paypal', 'PayPal')], validators=[DataRequired()])
    submit = SubmitField('Pay Now')
#-------------------------------------------
