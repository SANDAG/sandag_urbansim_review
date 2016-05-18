from flask import redirect, render_template, url_for

from . import zoning
from .forms import AddDevelopmentTypeForm
from .. import db
from ..models import Jurisdiction, Zoning, AllowedUse, DevelopmentType


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
