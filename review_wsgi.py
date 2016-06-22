import sys

sys.path.insert(0, 'E:/Apps/urbansim/review_prod')

from app import create_app

application = create_app('pgsql')