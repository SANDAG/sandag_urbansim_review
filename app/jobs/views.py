from flask import render_template, request
from flask.ext.login import login_required
from flask import jsonify
from sqlalchemy import desc, func

from . import jobs
from ..models import Building, Parcel, Geographies, Job
from .. import db


@jobs.route('/')
@login_required
def jobs_summary():
    return render_template('jobs/index.html')


@jobs.route('/_statistics/map/jobs')
def job_statistics_map_jobs():
    zoom_level = request.values.get('zoom_level', type=int)
    x_min = request.values.get('x_min', type=float)
    x_max = request.values.get('x_max', type=float)
    y_min = request.values.get('y_min', type=float)
    y_max = request.values.get('y_max', type=float)

    polygon = 'SRID=4326;POLYGON(({0:f} {1:f},{0:f} {3:f},{2:f} {3:f},{2:f} {1:f},{0:f} {1:f}))'.format(x_min, y_min,
                                                                                                        x_max, y_max)


    if zoom_level >= 16:
        id_column = Building.building_id
        spatial_results = dict(db.session.query(id_column, func.ST_AsGeoJson(Building.centroid)).filter(Building.centroid.ST_Intersects(polygon)).all())
        non_spatial_results = dict(db.session.query(id_column, func.count(Job.job_id)).join(Job).filter(id_column.in_(spatial_results.keys())).group_by(id_column).all())
    else:
        print "Zoom: " + str(zoom_level)
        if zoom_level >= 15:
            column = 'mgra'
        elif zoom_level >= 12:
            column = 'luz'

        id_column = getattr(Parcel, column + "_id")
        spatial_results = dict(db.session.query(Geographies.zone, func.ST_AsGeoJson(Geographies.shape)).filter(
            Geographies.geography_type == column).filter(Geographies.centroid.ST_Intersects(polygon)).all())

        non_spatial_results = dict(db.session.query(id_column, func.count(Job.job_id)).join(Building).join(Job)
                                   .filter(id_column.in_(spatial_results.keys())).group_by(id_column)
                                   .order_by(id_column).all())

    return_list = []

    for k, v in non_spatial_results.iteritems():
        geojson = eval(spatial_results[k])
        return_list.append({
            "type": "Feature",
            "geometry": {
                "type": geojson['type'],
                "coordinates": geojson['coordinates']
            }, "properties": {
                "jobs": v
                , id_column.name: k
            }
        })

    return jsonify({"type": "FeatureCollection",
                    "features": return_list})
