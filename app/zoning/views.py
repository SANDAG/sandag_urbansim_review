import datetime

from flask import redirect, render_template, url_for, flash

from . import zoning
from .forms import EditZoningForm
from .. import db
from ..models import Jurisdiction, Zoning, AllowedUse, DevelopmentType
from wtforms_sqlalchemy.orm import model_form



@zoning.route('/')
def index():
    jurisdictions = Jurisdiction.query.all()
    return render_template('index.html',
                           title='Jurisdictions',
                           jurisdictions=jurisdictions)

@zoning.route('/<jurisdiction_name>')
def jurisdiction_overview(jurisdiction_name):
    j = Jurisdiction.query.\
        filter_by(name=jurisdiction_name).first()
    return render_template('jurisdiction_overview.html',
                           title=j.name,
                           jurisdiction=j,
                           zoning=j.zones)


@zoning.route('/<jurisdiction_name>/<zone_code>')
def zoning_overview(jurisdiction_name, zone_code):
    j = Jurisdiction.query.\
        filter_by(name=jurisdiction_name).first()
    z = Zoning.query.filter_by(jurisdiction_id=j.jurisdiction_id, zone_code=zone_code).first()
    d = DevelopmentType.query.order_by(DevelopmentType.name).all()

    return render_template('zoning_overivew.html',
                           title='%s - %s' % (j.name, z.zone_code),
                           jurisdiction=j,
                           zoning=z,
                           development_types=d)


@zoning.route('/<jurisdiction_name>/<zone_code>/edit', methods=['GET', 'POST'])
def edit_zoning(jurisdiction_name, zone_code):
    form = EditZoningForm()
    j = Jurisdiction.query. \
        filter_by(name=jurisdiction_name).first()
    z = Zoning.query.filter_by(jurisdiction_id=j.jurisdiction_id, zone_code=zone_code).first()

    if form.validate_on_submit():
        z.min_far = form.min_far.data
        z.max_far = form.max_far.data
        z.min_front_setback = form.min_front_setback.data
        z.max_front_setback = form.max_front_setback.data
        z.rear_setback = form.rear_setback.data
        z.side_setback = form.side_setback.data
        z.min_lot_size = form.min_lot_size.data
        z.min_dua =  form.min_dua.data
        z.max_dua = form.max_dua.data
        z.max_res_units = form.max_res_units.data
        z.max_building_height = form.max_building_height.data
        z.zone_code_link = form.zone_code_link.data
        z.notes =  form.notes.data
        z.review_date = datetime.datetime.now()
        z.review_by = form.review_by.data
        db.session.add(z)
        db.session.commit()
        flash('The zone has been updated.')

    form.jurisdiction_id.data = j.jurisdiction_id
    form.zoning_id.data = z.zoning_id
    form.min_far.data = z.min_far
    form.max_far.data = z.max_far
    form.min_front_setback.data = z.min_front_setback
    form.max_front_setback.data = z.max_front_setback
    form.rear_setback.data = z.rear_setback
    form.side_setback.data = z.side_setback
    form.min_lot_size.data = z.min_lot_size
    form.min_dua.data = z.min_dua
    form.max_dua.data = z.max_dua
    form.max_res_units.data = z.max_res_units
    form.max_building_height.data = z.max_building_height
    form.zone_code_link.data = z.zone_code_link
    form.notes.data = z.notes
    form.review_by.data = z.review_by
    return render_template('edit_zoning.html', form=form, zoning=z)

@zoning.route('/add/<jurisdiction_name>/<zone_code>/<development_type_id>')
def add_zoning_allowed_use(jurisdiction_name, zone_code, development_type_id):
    j = Jurisdiction.query.filter_by(name=jurisdiction_name).first()
    z = Zoning.query.filter_by(jurisdiction_id=j.jurisdiction_id, zone_code=zone_code).first()
    a = AllowedUse(zoning_id=z.zoning_id, development_type_id=development_type_id)
    db.session.add(a)
    db.session.commit()

    return redirect(url_for('.zoning_overview', jurisdiction_name=j.name, zone_code=z.zone_code))


@zoning.route('/allowed_use/delete/<allowed_use_id>')
def delete_zoning_allowed_use(allowed_use_id):
    a = AllowedUse.query.get(allowed_use_id)
    jurisdiction_name = a.zoning.jurisdiction.name
    zone_code = a.zoning.zone_code
    db.session.delete(a)
    db.session.commit()
    return redirect(url_for('.zoning_overview', jurisdiction_name=jurisdiction_name, zone_code=zone_code))

ZoneForm = model_form(Zoning,exclude=['allowed_uses','jurisdiction'])


@zoning.route('/<jurisdiction_name>/<zone_code>/edit', methods=['GET', 'POST'])
def edit_zoning_from_model(jurisdiction_name, zone_code):
    success = False
    j = Jurisdiction.query.\
        filter_by(name=jurisdiction_name).first()
    z = Zoning.query.filter_by(jurisdiction_id=j.jurisdiction_id, zone_code=zone_code).first()
    if request.method == 'POST':
        form = ZoneForm(request.form,obj=z)
     #   if form.validate():
        form.populate_obj(z)
        db.session.add(z)
        db.session.commit()
        success = True
    else:
        form = ZoneForm(obj=z)

    return render_template('edit_zoning_from_model.html', form=form, success=success, j_name=j.name, z_code = zone_code)
