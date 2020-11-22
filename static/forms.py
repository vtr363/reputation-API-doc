from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, FloatField, PasswordField, BooleanField
from wtforms.validators import DataRequired,Email,InputRequired,EqualTo

class email_confirmation(FlaskForm):
	user_email = StringField("email",validators=[InputRequired(),EqualTo("confirm_email"),Email()])
	confirm_email = StringField("Confirme o Email",validators=[InputRequired(),Email()])
	user_pswd = PasswordField("senha",validators=[InputRequired(),EqualTo("confirm_pswd")])
	confirm_pswd = PasswordField("senha",validators=[InputRequired()])
	submit = SubmitField("Submit")

class userSignUp(FlaskForm):

	name = StringField("name",validators=[DataRequired()])
	user_email = StringField("email",validators=[DataRequired(),Email()])
	user_pswd = PasswordField("senha",validators=[DataRequired()])
	submit = SubmitField("Submit")

class colaboratorSignUp(FlaskForm):

	name = StringField("name",validators=[DataRequired()])
	user_email = StringField("email",validators=[DataRequired(),Email()])
	user_pswd = PasswordField("senha",validators=[DataRequired()])
	submit = SubmitField("Submit")

class applicationSignUp(FlaskForm):

	name = StringField("name",validators=[DataRequired()])
	key = StringField("key",validators=[DataRequired()])
	key_status = BooleanField("key_status(test)")
	questions = StringField("Questions Labels Separeted by (,)",validators=[DataRequired()])
	submit = SubmitField("Submit")
