import wtforms
from wtforms import Form, TextField, HiddenField, TextAreaField, SubmitField, BooleanField, StringField, PasswordField, validators

class ContactForm(Form):
  name = TextField("Name")
  email = TextField("Email")
  subject = TextField("Subject")
  message = TextAreaField("Message")
  submit = SubmitField("Send")

class RegistrationForm(Form):
    username = StringField('Username', [validators.Length(min=4, max=25)])
    email = StringField('Email Address', [validators.Length(min=6, max=35)])
    password = PasswordField('New Password', [
        validators.DataRequired(),
        validators.EqualTo('confirm', message='Passwords must match')
    ])
    confirm = PasswordField('Repeat Password')
    accept_tos = BooleanField('I accept the TOS', [validators.DataRequired()])

class AddPage(Form):
  page_id = HiddenField("Page_id")
  new_page_name = TextField("Page Name")
  new_page_title = TextField("Page Title")
  submit = SubmitField("Save")

class DelPage(Form):
  page_id = HiddenField("Page_id")
  submit = SubmitField("Delete")

class UpdateContent(Form):
  page_id = HiddenField("Page_id")
  page_target = HiddenField("page_target")
  content_id = HiddenField("Content_id")
  database = HiddenField("database")
  content_md = TextField("Content Markdown")
  content_ht = TextField("Content HTML")
  submit = SubmitField("Save")

class ChooseDatabase(Form):
  database = TextField("database")
