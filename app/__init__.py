from flask import Flask
from flask.ext.bootstrap import Bootstrap
from flask.ext.login import LoginManager
from flask.ext.sqlalchemy import SQLAlchemy

from config import config, Config
from sample_data_structure import zoning_definitions, model_structure_def, allowed_use_def, development_type_defs
from .moment import momentjs

bootstrap = Bootstrap()
db = SQLAlchemy()

login_manager = LoginManager()
login_manager.session_protection = 'strong'
login_manager.login_view = 'auth.login'

def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)

    bootstrap.init_app(app)
    db.init_app(app)
    login_manager.init_app(app)
    app.jinja_env.globals['momentjs'] = momentjs

    from .auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint, url_prefix='/auth')

    from .scenario import scenario as scenario_blueprint
    app.register_blueprint(scenario_blueprint, url_prefix='/scenario')

    from .zoning import zoning as zoning_blueprint
    app.register_blueprint(zoning_blueprint, url_prefix='/zoning')

    return app
