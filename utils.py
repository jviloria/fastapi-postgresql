from passlib.context import CryptContext
import json

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def model2Dict(obj):
    res_dict = {}
    for f in obj.__table__.columns.keys():
        res_dict[f] = getattr(obj, f)
    return res_dict


def failedMessage(msg):
    if not isinstance(msg, str): msg = '%s'%msg
    return {'Result': 'Failed', 'Message': msg}

def successMessage(msg: str = None):
    if msg: return {'Result': 'Success', 'Message': msg} 
    return {'Result': 'Success'}

def encryptPassword(password):
    return pwd_context.hash(password)

def loadConfig(key=None):
    with open('config.cfg', 'r') as f:
        try:
            config_file = json.load(f)
            if key: config_file = config_file[key]
        except Exception as e:
            print('Error cargando archivo de configuracion: %s'%e)
            return False
    return config_file