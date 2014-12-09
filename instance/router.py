
from .conf import DEFAULT_DB_CONNECTION

def connection_for_model(model):
    if model._meta.app_label == 'instance':
        return DEFAULT_DB_CONNECTION
    return None

class DefaultInstanceRouter(object):
    def db_for_read(self, model, **hints):
        return connection_for_model(model)

    def db_for_write(self, model, **hints):
        return connection_for_model(model)

    def allow_relation(self, obj1, obj2, **hints):
        return any([
            obj1._meta.app_label == 'instance',
            obj2._meta.app_label == 'instance',
        ]) or None

    def allow_migrate(self, db, model):
        if db == DEFAULT_DB_CONNECTION:
            return model._meta.app_label == 'instance'
        elif model._meta.app_label == 'instance':
            return False
        return None
