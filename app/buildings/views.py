
from flask import render_template, request, url_for
from flask.ext.login import login_required, current_user
from flask import jsonify
from sqlalchemy import desc, func

from pysandag.gis import transform_wkt
from shapely.wkt import loads as wkt_loads
from shapely.geometry import mapping

from . import buildings
from ..models import Building
from .. import db


@buildings.route('/')
@login_required
def buildings_summary():
    bldg_summary = \
        db.session.query(
            func.count(Building.building_id).label('building_count'),
            func.sum(Building.residential_units).label('residential_units'),
            func.sum(Building.job_spaces).label('job_spaces')
        ).first()
    residential_units = db.session.query(func.sum(Building.residential_units)).scalar()

    return render_template('buildings/index.html',
                           building_summary=bldg_summary)


@buildings.route('/_geometry/<int:building_id>')
def buildings_geometry(building_id):
    building = Building.query.get(building_id)
    s = mapping(wkt_loads(transform_wkt(building.shape_wkt)[10:])) if building.shape_wkt is not None else None

    return jsonify(s)


@buildings.route('/_data', methods=['POST'])
def buildings_page():
    draw = request.values.get('draw',type=int)
    start = request.values.get('start', type=int)
    length = request.values.get('length', type=int)
    order_column_id = request.values.get('order[0][column]', type=int)
    order_direction = request.values.get('order[0][dir]', type=str)
    column_name = request.values.get('columns[%i][name]' % order_column_id, type=str)

    q = Building.query

    for i in xrange(0,11):
        search_term = request.values.get('columns[%i][search][value]' % i)
        if search_term:
            column = getattr(Building, request.values.get('columns[%i][name]' % i, type=str))
            q = q.filter(column == search_term)

    if order_direction == 'asc':
        col = getattr(Building, column_name)
    else:
        col = desc(getattr(Building, column_name))

    result = q.order_by(col).paginate((start / length) + 1, length, False)
    bldgs = [bldg.to_json for bldg in result.items]
    j = {
        'draw': draw,
        'recordsTotal': result.total,
        'recordsFiltered': result.total,
        'data': bldgs
    }

    return jsonify(j)