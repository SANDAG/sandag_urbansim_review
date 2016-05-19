import sys

sys.path.insert(0, 'E:/Apps/urbansim/review')

from app import create_app

application = create_app('sqlsvr')