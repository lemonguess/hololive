from config import app_config


from models.base import Base
from sqlalchemy import create_engine
from model import BaseSupplierModel, UsersModel, UserSupplierModel, LLMModel, AgentConfigModel, TTSConfigModel

db_config = app_config['database']
def create_tables():
    db_type = db_config.get('type', 'sqlite')
    if db_type == 'sqlite':
        database = db_config.get('database', 'hololive.db')
        engine_url = f"sqlite:///{database}"
    elif db_type == 'mysql':
        user = db_config.get('user', '')
        password = db_config.get('password', '')
        host = db_config.get('host', 'localhost')
        port = db_config.get('port', '3306')
        database = db_config.get('database', 'hololive')
        engine_url = f"mysql+pymysql://{user}:{password}@{host}:{port}/{database}"
    elif db_type == 'pgsql':
        user = db_config.get('user', '')
        password = db_config.get('password', '')
        host = db_config.get('host', 'localhost')
        port = db_config.get('port', '5432')
        database = db_config.get('database', 'hololive')
        engine_url = f"postgresql+psycopg2://{user}:{password}@{host}:{port}/{database}"
    else:
        raise ValueError("Unsupported database type")
    
    engine = create_engine(engine_url)
    Base.metadata.create_all(engine)


create_tables()