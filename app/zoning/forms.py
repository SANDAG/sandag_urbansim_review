from flask.ext.wtf import Form
from wtforms import HiddenField, SubmitField, StringField, TextAreaField, IntegerField, FloatField
from wtforms.validators import InputRequired, NumberRange


class EditZoningForm(Form):

    jurisdiction_id = HiddenField('jurisdiction_id', validators=[InputRequired()])
    zoning_id = HiddenField('zoning_id', validators=[InputRequired()])

    min_far = FloatField('Minimum FAR', validators=[NumberRange(-1,10)])
    max_far = FloatField('Maximum FAR', validators=[NumberRange(-1,10)])
    min_front_setback = FloatField('Minimum Front Setback', validators=[NumberRange(-1,100)])
    max_front_setback = FloatField('Maximum Front Setback', validators=[NumberRange(-1,100)])
    rear_setback = FloatField('Rear Setback', validators=[NumberRange(-1,100)])
    side_setback = FloatField('Side Setback', validators=[NumberRange(-1,100)])
    min_lot_size = FloatField('Minimum Lot Size', validators=[NumberRange(-1,435600)])
    min_dua = FloatField('Minimum Dwelling Units per Acre', validators=[NumberRange(-1,100)])
    max_dua = FloatField('Maximum Dwelling Units per Acre', validators=[NumberRange(-1,500)])
    max_res_units = IntegerField('Maximum Residential Units per Lot', validators=[NumberRange(-1,500)])
    max_building_height = IntegerField('Maximum Building Height', validators=[NumberRange(-1,750)])
    zone_code_link = StringField('Link to Zoning Ordinance')
    notes = TextAreaField('Notes')
    submit = SubmitField('Submit')
