import datetime

from flask import redirect, render_template, url_for, flash, jsonify, request
from flask.ext.login import login_required, current_user

from sqlalchemy import func, asc

from . import zoning
from .forms import EditZoningForm
from .. import db
from ..models import Capacity, Jurisdiction, Zoning, AllowedUse, DevelopmentType

import json

def zoning_summary():
    total = dict(db.session.query(Zoning.jurisdiction_id, func.count(Zoning.jurisdiction_id)).group_by(
        Zoning.jurisdiction_id).all())

    reviewed = dict(db.session.query(Zoning.jurisdiction_id, func.count(Zoning.jurisdiction_id)).filter(
        Zoning.review_by != None).group_by(Zoning.jurisdiction_id).all())

    return dict(
        (k, {'total': total.get(k), 'reviewed': reviewed.get(k) if reviewed.get(k) is not None else 0}) for k in set(total.keys() + reviewed.keys()))


@zoning.route('/')
def index():
    jurisdictions = Jurisdiction.query.all()
    return render_template('zoning/index.html',
                           title='Jurisdictions',
                           jurisdictions=jurisdictions,
                           summary=zoning_summary())

@zoning.route('/<jurisdiction_name>')
def jurisdiction_overview(jurisdiction_name):
    j = Jurisdiction.query.\
        filter_by(name=jurisdiction_name).first()
    return render_template('zoning/jurisdiction_overview.html',
                           title=j.name,
                           jurisdiction=j,
                           zoning=j.zones)


@zoning.route('/_capacity/<jurisdiction_name>')
def jurisdiction_capacity(jurisdiction_name):
    include_zones = request.values.get('include_zones', type=str)
    j = Jurisdiction.query.filter_by(name=jurisdiction_name).first()

    qry = db.session.query(Capacity.jurisdiction_id, func.sum(Capacity.parcel_capacity)).filter(Capacity.jurisdiction_id == j.jurisdiction_id).group_by(Capacity.jurisdiction_id)
    columns = ['jurisdiction', 'residential_units']

    if include_zones and include_zones.lower() == 'yes':
        qry = qry.add_columns(Capacity.zoning_id)\
            .group_by(Capacity.zoning_id)\
            .order_by(Capacity.zoning_id)
        columns.append('zoning_id')



    capacity = qry.all()
    return_list = []
    for c in capacity:
        results = [jurisdiction_name, int(c[1])]
        if include_zones and include_zones.lower() == 'yes':
            results.append(c[2])
        return_list.append(dict(zip(columns, results)))

    print return_list

    return jsonify({'capacity': return_list})


@zoning.route('/<jurisdiction_name>/<zone_code>')
def zoning_overview(jurisdiction_name, zone_code):
    j = Jurisdiction.query.\
        filter_by(name=jurisdiction_name).first()
    z = Zoning.query.filter_by(jurisdiction_id=j.jurisdiction_id, zone_code=zone_code).first()
    d = DevelopmentType.query.order_by(DevelopmentType.development_type_id).all()

    return render_template('zoning/zoning_overivew.html',
                           title='%s - %s' % (j.name, z.zone_code),
                           jurisdiction=j,
                           zoning=z,
                           development_types=d,
                           geom=z.shape_geojson)


@zoning.route('/<jurisdiction_name>/<zone_code>/edit', methods=['GET', 'POST'])
@login_required
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
        z.review_date = datetime.datetime.utcnow()
        z.review_by = current_user.email
        db.session.add(z)
        db.session.commit()
        flash('The zone has been updated by %s.' % current_user.email)

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

    return render_template('zoning/edit_zoning.html', form=form, zoning=z)

@zoning.route('/add/<jurisdiction_name>/<zone_code>/<development_type_id>')
@login_required
def add_zoning_allowed_use(jurisdiction_name, zone_code, development_type_id):
    j = Jurisdiction.query.filter_by(name=jurisdiction_name).first()
    z = Zoning.query.filter_by(jurisdiction_id=j.jurisdiction_id, zone_code=zone_code).first()
    a = AllowedUse(zoning_id=z.zoning_id, development_type_id=development_type_id)
    db.session.add(a)
    db.session.commit()

    return redirect(url_for('.zoning_overview', jurisdiction_name=j.name, zone_code=z.zone_code))


@zoning.route('/_add/<jurisdiction_name>/<zone_code>/<development_type_id>')
@login_required
def add_zoning_allowed_use_ajax(jurisdiction_name, zone_code, development_type_id):
    print jurisdiction_name
    print zone_code
    print development_type_id
    j = Jurisdiction.query.filter_by(name=jurisdiction_name).first()
    z = Zoning.query.filter_by(jurisdiction_id=j.jurisdiction_id, zone_code=zone_code).first()
    a = AllowedUse(zoning_id=z.zoning_id, development_type_id=development_type_id)
    db.session.add(a)
    db.session.commit()

    return jsonify(result=[a.to_json for a in z.allowed_uses.order_by(asc(AllowedUse.development_type_id))])


@zoning.route('/allowed_use/delete/<allowed_use_id>')
@login_required
def delete_zoning_allowed_use(allowed_use_id):
    a = AllowedUse.query.get(allowed_use_id)
    jurisdiction_name = a.zoning.jurisdiction.name
    zone_code = a.zoning.zone_code
    db.session.delete(a)
    db.session.commit()
    return redirect(url_for('.zoning_overview', jurisdiction_name=jurisdiction_name, zone_code=zone_code))

@zoning.route('/allowed_use/_delete/<allowed_use_id>')
@login_required
def delete_zoning_allowed_use_ajax(allowed_use_id):
    a = AllowedUse.query.get(allowed_use_id)
    z = a.zoning
    db.session.delete(a)
    db.session.commit()

    return jsonify(result=[a.to_json for a in z.allowed_uses.order_by(asc(AllowedUse.development_type_id))])