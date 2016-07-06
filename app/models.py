"""  Module for holding together ORM Mappings """

from flask.ext.login import UserMixin
from geoalchemy2.shape import to_shape
from geoalchemy2.types import Geography
from shapely.geometry import mapping as geojson_mapping
from werkzeug.security import generate_password_hash, check_password_hash

from . import db, zoning_definitions, allowed_use_def, development_type_defs, model_structure_def, login_manager


class AllowedUse(db.Model):
    """ SQL Alchemy Class that maps to urbansim.zoning_allowed_use """

    __tablename__ = 'zoning_allowed_use'
    __table_args__ = {'schema': 'urbansim'}
    zoning_allowed_use_id = db.Column(db.Integer, primary_key=True)
    zoning_id = db.Column(db.Integer, db.ForeignKey('urbansim.zoning.zoning_id'))
    development_type_id = db.Column(db.Integer, db.ForeignKey('ref.development_type.development_type_id'))

    @property
    def to_json(self):
        return {
            'zoning_allowed_use_id': self.zoning_allowed_use_id,
            'zoning_id': self.zoning_id,
            'zone_code': self.zoning.zone_code,
            'development_type_id': self.development_type_id,
            'development_type': self.development_type.name
        }

    @staticmethod
    def insert_allowed_use():
        for a in allowed_use_def:
            allowed_use = AllowedUse.query.filter_by(zoning_allowed_use_id=a).first()
            if allowed_use is None:
                allowed_use = AllowedUse(zoning_allowed_use_id=a)
            allowed_use.zoning = Zoning.query.filter_by(zoning_id=allowed_use_def[a]['zoning_id']).first()
            allowed_use.development_type_id = allowed_use_def[a]['development_type_id']
            db.session.add(allowed_use)
        db.session.commit()

    def __repr__(self):
        return '<AllowedUse %r-%r>' % (self.zoning_id, self.development_type_id)


class Building(db.Model):
    """ SQL Alchemy Class that maps to urbansim.buildings """

    __tablename__ = 'buildings'
    __table_args__ = {'schema': 'urbansim'}
    column_default_sort = 'building_id'
    building_id = db.Column(db.Integer, primary_key=True)
    development_type_id = db.Column(db.Integer, nullable=False)
    parcel_id = db.Column(db.Integer, db.ForeignKey('urbansim.parcels.parcel_id'))
    improvement_value = db.Column(db.Float)
    residential_units = db.Column(db.SmallInteger)
    residential_sqft = db.Column(db.Integer)
    non_residential_sqft = db.Column(db.Integer)
    job_spaces = db.Column(db.SmallInteger)
    jobs = db.relationship('Job', backref='building', lazy='dynamic')
    non_residential_rent_per_sqft = db.Column(db.Float)
    residential_rent_per_sqft = db.Column(db.Float, name='price_per_sqft')
    stories = db.Column(db.Integer)
    year_built = db.Column(db.SmallInteger)
    shape = db.Column(Geography(geometry_type='GEOMETRY', srid=4236))
    centroid = db.Column(Geography(geometry_type='POINT', srid=4326))

    @property
    def shape_geojson(self):
        return geojson_mapping(to_shape(self.shape)) if self.shape is not None else None

    @property
    def centroid_geojson(self):
        return geojson_mapping(to_shape(self.centroid)) if self.shape is not None else None

    @property
    def to_json(self):
        return {
            'building_id': self.building_id,
            'parcel_id': self.parcel_id,
            'development_type_id': self.development_type_id,
            'improvement_value': '{:,}'.format(
                int(self.improvement_value)) if self.improvement_value is not None else '',
            'residential_units': '{:,}'.format(self.residential_units) if self.residential_units is not None else '',
            'residential_sqft': '{:,}'.format(self.residential_sqft) if self.residential_sqft is not None else '',
            'non_residential_sqft': '{:,}'.format(
                self.non_residential_sqft) if self.non_residential_sqft is not None else '',
            'job_spaces': '{:,}'.format(self.job_spaces) if self.job_spaces is not None else '',
            'non_residential_rent_per_sqft': '{:,}'.format(
                self.non_residential_rent_per_sqft) if self.non_residential_rent_per_sqft is not None else '',
            'residential_rent_per_sqft': '{:,}'.format(
                self.residential_rent_per_sqft) if self.non_residential_rent_per_sqft is not None else '',
            'stories': '{:,}'.format(self.stories) if self.job_spaces is not self.stories else '',
            'year_built': self.year_built,
            'DT_RowId': 'row_%i' % self.building_id
        }

    def __repr__(self):
        return '<Building %r>' % self.building_id


class Capacity(db.Model):
    """ SQL Alchemy Class that maps to a view urbansim.vi_parcel_res_capacity """

    __tablename__ = 'vi_parcel_res_capacity'
    __table_args__ = {'schema': 'urbansim'}
    jurisdiction_id = db.Column(db.Integer, db.ForeignKey('ref.jurisdiction.jurisdiction_id'))
    zoning_id = db.Column(db.String(35), nullable=False)
    parcel_id = db.Column(db.Integer, db.ForeignKey('urbansim.parcels.parcel_id') ,primary_key=True)
    parcel_capacity = db.Column(db.Integer, nullable=False)


class DevelopmentType(db.Model):
    """ SQL Alchemy Class that maps to a lookup table ref.development_type """

    __tablename__ = 'development_type'
    __table_args__ = {'schema': 'ref'}
    development_type_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(35), unique=True, nullable=False)
    allowed_uses = db.relationship('AllowedUse', backref='development_type', lazy='dynamic')

    @staticmethod
    def insert_development_type():
        for d in development_type_defs:
            development_type = DevelopmentType.query.get(d)
            if development_type is None:
                development_type = DevelopmentType(development_type_id=d)
            development_type.name = development_type_defs[d]
            db.session.add(development_type)
        db.session.commit()

    def __repr__(self):
        return '<DevelopmentType %r-%r>' % (self.development_type_id, self.name)


class Geographies(db.Model):
    """ SQL Alchemy Class that maps to the common geography shape table ref.geography_zone """

    __tablename__ = 'geography_zone'
    __table_args__ = {'schema': 'ref'}
    geography_zone_id = db.Column(db.Integer, primary_key=True)
    geography_type = db.Column(db.String(8), nullable=False)
    zone = db.Column(db.Integer, nullable=False)
    shape = db.Column(Geography(geometry_type='MULTIPOLYGON', srid=4326), nullable=False)
    centroid = db.Column(Geography(geometry_type='POINT', srid=4326), nullable=False)


class Job(db.Model):
    """ SQL Alchemy Class that maps to urbansim.jobs """

    __tablename__ = 'jobs'
    __table_args__ = {'schema': 'urbansim'}
    job_id = db.Column(db.Integer, primary_key=True)
    sector_id = db.Column(db.Integer, nullable=False)
    building_id = db.Column(db.Integer, db.ForeignKey('urbansim.buildings.building_id'))


class Jurisdiction(db.Model):
    """ SQL Alchemy Class that maps to ref.jurisdiction """

    __tablename__ = 'jurisdiction'
    __table_args__ = {'schema': 'ref'}
    jurisdiction_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(32), unique=True)
    zones = db.relationship('Zoning', backref='jurisdiction', lazy='dynamic')
    capacity = db.relationship('Capacity', backref='jurisdiction', lazy='dynamic')

    @staticmethod
    def insert_jurisdictions():
        jurisdictions = {
            1: 'Carlsbad',
            2: 'Chula Vista',
            3: 'Coronado',
            4: 'Del Mar'
        }
        for j in jurisdictions:
            jurisdiction = Jurisdiction.query.filter_by(jurisdiction_id=j).first()
            if jurisdiction is None:
                jurisdiction = Jurisdiction(jurisdiction_id=j)
            jurisdiction.name = jurisdictions[j]
            db.session.add(jurisdiction)
        db.session.commit()

    def __repr__(self):
        return '<Jurisdiction %r>' % self.name


class ModelStructure(db.Model):
    """ SQL Alchemy Class that maps to ref.model """

    __tablename__ = 'model'
    __table_args__ = {'schema': 'ref'}
    model_id = db.Column(db.SmallInteger, primary_key=True)
    name = db.Column(db.String(64), unique=True, nullable=False)
    display_name = db.Column(db.String(64), unique=True, nullable=False)
    overview = db.Column(db.String())
    active = db.Column(db.Boolean(), nullable=False, default=False)

    @staticmethod
    def insert_model_structure():
        for m in model_structure_def:
            model_structure = ModelStructure.query.get(m)
            if model_structure is None:
                model_structure = ModelStructure(model_id=m)
            model_structure.name = m.name
            model_structure.display_name = m.display_name
            model_structure.overview = m.overview
            model_structure.active = m.active
            db.session.add(model_structure)
        db.session.commit()

    def __repr__(self):
        return '<ModelStructure %r-%r>' % (self.model_id, self.name)


class Parcel(db.Model):
    """ SQL Alchemy Class that maps to urbansim.parcels """

    __tablename__ = 'parcels'
    __table_args__ = {'schema': 'urbansim'}
    parcel_id = db.Column(db.Integer, primary_key=True)
    msa_id = db.Column(db.Integer)
    luz_id = db.Column(db.Integer)
    mgra_id = db.Column(db.Integer)
    buildings = db.relationship('Building', backref='parcel', lazy='dynamic')
    capacity = db.relationship('Capacity', backref='parcel', uselist=False)

    def __repr__(self):
        return '<Parcel %r>' % self.parcel_id


class User(UserMixin, db.Model):
    """ SQL Alchemy Class that maps to ref.users """

    __tablename__ = 'users'
    __table_args__ = {'schema': 'ref'}
    id = db.Column(db.Integer, primary_key=True, name='users_id')
    email = db.Column(db.String(64), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(128))
    first_name = db.Column(db.String(32), nullable=False)
    last_name = db.Column(db.String(32), nullable=False)

    @property
    def password(self):
        raise AttributeError('Password is not a readable property.')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    @property
    def full_name(self):
        return self.first_name + ' ' + self.last_name

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    @staticmethod
    def insert_users():
        users = {
            1: {'email': 'clint.daniels@sandag.org',
                'password': 'sandag',
                'first_name': 'Clint',
                'last_name': 'Daniels'},
            2: {'email': 'elias.sanz@sandag.org',
                'password': 'sandag',
                'first_name': 'Elias',
                'last_name': 'Sanz'},
        }

        for u in users:
            user = User.query.filter_by(id=u).first()
            if user is None:
                user = User(id=u)
            user.email = users[u]['email']
            user.password = users[u]['password']
            user.first_name = users[u]['first_name']
            user.last_name = users[u]['last_name']
            db.session.add(user)
        db.session.commit()

    def __repr__(self):
        return '<User %r-%r>' % (self.id, self.email)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class Zoning(db.Model):
    """ SQL Alchemy Class that maps to urbansim.zoning """

    __tablename__ = 'zoning'
    __table_args__ = {'schema': 'urbansim'}

    zoning_id = db.Column(db.String(35), primary_key=True)
    jurisdiction_id = db.Column(db.Integer, db.ForeignKey('ref.jurisdiction.jurisdiction_id'))
    allowed_uses = db.relationship('AllowedUse', backref='zoning', lazy='dynamic')
    zone_code = db.Column(db.String(22), nullable=False)
    region_id = db.Column(db.Integer, nullable=False, default=1)
    min_far = db.Column(db.Float, nullable=False, default=0)
    max_far = db.Column(db.Float, nullable=False, default=0)
    min_front_setback = db.Column(db.Float, nullable=False, default=0)
    max_front_setback = db.Column(db.Float, nullable=False, default=0)
    rear_setback = db.Column(db.Float, nullable=False, default=0)
    side_setback = db.Column(db.Float, nullable=False, default=0)
    min_lot_size = db.Column(db.Integer)
    min_dua = db.Column(db.Float, nullable=False, default=0)
    max_dua = db.Column(db.Float, nullable=False, default=0)
    max_res_units = db.Column(db.Integer)
    max_building_height = db.Column(db.Integer, nullable=False, default=0)
    zone_code_link = db.Column(db.String())
    notes = db.Column(db.Text())
    review_date = db.Column(db.DateTime)
    review_by = db.Column(db.String(25))
    shape = db.Column(Geography(geometry_type='Geometry', srid=4326))

    @property
    def shape_geojson(self):
        return geojson_mapping(to_shape(self.shape)) if self.shape is not None else None

    @staticmethod
    def insert_zoning():
        for z in zoning_definitions:
            zoning = Zoning.query.filter_by(zoning_id=z).first()
            if zoning is None:
                zoning = Zoning(zoning_id=z)
            zoning.jurisdiction = Jurisdiction.query.filter_by(
                jurisdiction_id=zoning_definitions[z]['jurisdiction_id']).first()
            zoning.zone_code = zoning_definitions[z]['zone_code']
            zoning.region_id = zoning_definitions[z]['region_id']
            zoning.min_far = zoning_definitions[z]['min_far']
            zoning.max_far = zoning_definitions[z]['max_far']
            zoning.min_front_setback = zoning_definitions[z]['min_front_setback']
            zoning.max_front_setback = zoning_definitions[z]['max_front_setback']
            zoning.rear_setback = zoning_definitions[z]['rear_setback']
            zoning.side_setback = zoning_definitions[z]['side_setback']
            zoning.min_dua = zoning_definitions[z]['min_dua']
            zoning.max_dua = zoning_definitions[z]['max_dua']
            zoning.max_building_height = zoning_definitions[z]['max_building_height']
            db.session.add(zoning)
        db.session.commit()

    def __repr__(self):
        return '<Zoning %r>' % self.zoning_id
