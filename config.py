import os
basedir = os.path.abspath(os.path.dirname(__file__))
POSTS_PER_PAGE = 10

class Config:
    SECRET_KEY = '074hN0u4Ex'
    SSL_DISABLE = False
    SQLALCHEMY_COMMIT_ON_TEARDOWN = True
    SQLALCHEMY_RECORD_QUERIES = True

    @staticmethod
    def init_app(app):
        pass

class DevelopmentConfig(Config):
    DATABASE_TYPE = 'SQLITE'
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('DEV_DATABASE_URL') or \
                              'sqlite:///' + os.path.join(basedir, 'data-dev.sqlite')

class SqlSvrConfig(Config):
    DATABASE_TYPE = 'MSSQL'
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'mssql+pyodbc://sql2014a8/spacecore?driver=SQL+Server+Native+Client+11.0'


config = {
    'development': DevelopmentConfig,
    'sqlsvr': SqlSvrConfig,
    'default': DevelopmentConfig
}