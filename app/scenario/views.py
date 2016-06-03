import datetime

from flask import redirect, render_template, url_for, flash
from flask.ext.login import login_required, current_user

from sqlalchemy import func

from . import scenario
from ..models import ModelStructure
from .. import db


@scenario.route('/')
@login_required
def run_scenario():
    models = ModelStructure.query.all()
    return render_template('scenario/run.html',
                           models=models)