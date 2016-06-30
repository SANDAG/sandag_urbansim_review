from flask import render_template, request
from flask.ext.login import login_required
from flask import jsonify
from sqlalchemy import desc, func

from . import buildings
from ..models import Building, Parcel, Geographies, Job
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
    return jsonify(building.shape_geojson)


@buildings.route('/_data', methods=['POST'])
def buildings_page():
    total_records = db.session.query(func.count(Building.building_id)).scalar()
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
        'recordsTotal': total_records,
        'recordsFiltered': result.total,
        'data': bldgs
    }

    return jsonify(j)


@buildings.route('/_statistics/map/jobs')
def building_statistics_map_jobs():
    x_min = request.values.get('x_min', type=float)
    x_max = request.values.get('x_max', type=float)
    y_min = request.values.get('y_min', type=float)
    y_max = request.values.get('y_max', type=float)

    polygon = 'SRID=4326;POLYGON(({0:f} {1:f},{0:f} {3:f},{2:f} {3:f},{2:f} {1:f},{0:f} {1:f}))'.format(x_min, y_min,
                                                                                                        x_max, y_max)

    centroids = dict(db.session.query(Building.building_id, func.ST_AsGeoJson(Building.centroid)).filter(Building.centroid.ST_Intersects(polygon)).all())
    bldgs = dict(db.session.query(Building.building_id, func.count(Job.job_id)).join(Job).filter(Building.building_id.in_(centroids.keys())).group_by(Building.building_id).all())

    return_list = []

    for k, v in bldgs.iteritems():
        geojson = eval(centroids[k])
        return_list.append({
            "type": "Feature",
            "geometry": {
                "type": geojson['type'],
                "coordinates": geojson['coordinates']
            }, "properties": {
                "buildings": v
                , 'building_id': k
            }
        })

    return jsonify({"type": "FeatureCollection",
                    "features": return_list})


@buildings.route('/_statistics/map', methods=['POST'])
def buildings_statistics_map():
    zoom_level = request.values.get('zoom_level',type=int)
    x_min = request.values.get('x_min',type=float)
    x_max = request.values.get('x_max',type=float)
    y_min = request.values.get('y_min',type=float)
    y_max = request.values.get('y_max',type=float)

    if zoom_level < 12:
        geography_type = 'msa'
        print 'msa'
    elif zoom_level < 15:
        geography_type = 'luz'
        print 'luz'
    elif zoom_level < 20:
        geography_type = 'mgra'
        print 'mgra'
    else:
        geography_type = 'msa'
        print 'default'

    polygon = 'SRID=4326;POLYGON(({0:f} {1:f},{0:f} {3:f},{2:f} {3:f},{2:f} {1:f},{0:f} {1:f}))'.format(x_min, y_min, x_max, y_max)

    centroids = dict(db.session.query(Geographies.zone, func.ST_AsGeoJson(Geographies.centroid)).filter(
        Geographies.geography_type == geography_type[:5]).filter(Geographies.centroid.ST_Intersects(polygon)).all())

    id_column = getattr(Parcel, geography_type + "_id")
    bldgs = dict(db.session.query(id_column, func.count(Building.building_id)).join(Building).filter(
        id_column.isnot(None)).filter(id_column.in_(centroids.keys())).group_by(id_column).order_by(id_column).all())

    return_list = []

    for k, v in bldgs.iteritems():
        geojson = eval(centroids[k])
        return_list.append({
            "type": "Feature",
            "geometry": {
                "type": geojson['type'],
                "coordinates": geojson['coordinates']
            },"properties": {
                "buildings" : v
                ,geography_type: k
            }
        })

    return jsonify({"type": "FeatureCollection",
                    "features":return_list})
