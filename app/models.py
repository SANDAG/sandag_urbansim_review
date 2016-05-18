from . import db, zoning_definitions, allowed_use_def, development_type_defs

class Jurisdiction(db.Model):
    __tablename__ = 'jurisdiction'
    __table_args__ = {'schema':'ref'}
    jurisdiction_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(32), unique=True)
    zones = db.relationship('Zoning', backref='jurisdiction', lazy='dynamic')

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


class Zoning(db.Model):
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

    @staticmethod
    def insert_zoning():
        for z in zoning_definitions:
            zoning = Zoning.query.filter_by(zoning_id=z).first()
            if zoning is None:
                zoning = Zoning(zoning_id=z)
            zoning.jurisdiction = Jurisdiction.query.filter_by(jurisdiction_id=zoning_definitions[z]['jurisdiction_id']).first()
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


class AllowedUse(db.Model):
    __tablename__ = 'zoning_allowed_use'
    __table_args__ = {'schema': 'urbansim'}
    zoning_allowed_use_id = db.Column(db.Integer, primary_key=True)
    zoning_id = db.Column(db.Integer, db.ForeignKey('urbansim.zoning.zoning_id'))
    development_type_id = db.Column(db.Integer, db.ForeignKey('ref.development_type.development_type_id'))

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


class DevelopmentType(db.Model):
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
        return '<AllowedUse %r-%r>' % (self.development_type_id, self.name)