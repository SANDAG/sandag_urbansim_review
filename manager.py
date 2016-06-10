import os

from app import create_app, db
from app.models import AllowedUse, Jurisdiction, Zoning, DevelopmentType, User, Building, Parcel
from flask.ext.script import Manager, Shell
from flask.ext.migrate import Migrate, MigrateCommand

app = create_app(os.getenv('FLASK_CONFIG') or 'default')
manager = Manager(app)
migrate = Migrate(app, db)


def make_shell_context():
    return dict(app=app, db=db, Jurisdiction=Jurisdiction, Zoning=Zoning,
                AllowedUse=AllowedUse, DevelopmentType=DevelopmentType,
                User=User, Building=Building, Parcel=Parcel)


manager.add_command('shell', Shell(make_context=make_shell_context))
manager.add_command('db', MigrateCommand)


@manager.command
def deploy():
    """Run deployment tasks."""
    from flask.ext.migrate import upgrade
    from app.models import Jurisdiction

    upgrade()

    Jurisdiction.insert_jurisdictions()

    Zoning.insert_zoning()

    AllowedUse.insert_allowed_use()

    DevelopmentType.insert_development_type()

if __name__ == '__main__':
    manager.run()
