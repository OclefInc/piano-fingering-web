from flask_wtf import FlaskForm
from wtforms import FileField, SelectField, SubmitField
from wtforms.validators import DataRequired

class UploadForm(FlaskForm):
    file = FileField('Upload File', validators=[DataRequired()])
    hand_size = SelectField('Select Hand Size', choices=[
        ('XXS', 'XXS'),
        ('XS', 'XS'),
        ('S', 'S'),
        ('M', 'M'),
        ('L', 'L'),
        ('XL', 'XL'),
        ('XXL', 'XXL')
    ], validators=[DataRequired()])
    submit = SubmitField('Submit')