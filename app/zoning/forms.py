from flask.ext.wtf import Form
from wtforms import SelectField, SubmitField, HiddenField
from wtforms.validators import  DataRequired, Length

from ..models import DevelopmentType


class AddDevelopmentTypeForm(Form):
    development_type_id = SelectField('Development Type', coerce=int, validators=[DataRequired()])
    jurisdiction_name = HiddenField('Jurisdiction', validators=[DataRequired(), Length(0,32)])
    zone_code = HiddenField('Zone Code', validators=[DataRequired(), Length(22)])
    submit = SubmitField('Submit')

    def __init__(self, *args, **kwargs):
        super(AddDevelopmentTypeForm, self).__init__(*args, **kwargs)
        self.development_type_id.choices = [(development.development_type_id, development.name)
                                         for development in DevelopmentType.query.order_by(DevelopmentType.name).all()]
