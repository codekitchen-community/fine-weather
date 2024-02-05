from flask_wtf import FlaskForm
from flask_wtf.file import FileRequired
from wtforms.fields.simple import StringField, FileField
from wtforms.validators import InputRequired, Length

ALLOWED_IMAGE_TYPES = ["jpeg", "gif", "png"]


class UploadImageForm(FlaskForm):
    image = FileField(
        "Image",
        render_kw={
            "accept": f'{",".join(["image/"+t for t in ALLOWED_IMAGE_TYPES])}',
        },
        validators=[FileRequired()],
    )
    title = StringField(
        "Title",
        validators=[InputRequired(), Length(1, 100)],
    )
    position = StringField("Position")
    description = StringField("Description")
    time = StringField("Time")


class EditImageForm(FlaskForm):
    title = StringField(
        "Title",
        validators=[InputRequired(), Length(1, 100)],
    )
    position = StringField("Position")
    description = StringField("Description")
    time = StringField("Time")
