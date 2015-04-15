def is_api_model(model):
    return model.__module__ == 'api.models'


class APIRouter(object):
    """
    A router to ensure that all requests for RedirectArchive objects
    go to the "archive" database defined in settings.DATABASES.

    """
    def db_for_read(self, model, **hints):
        """
        Attempts to read from RedirectArchive go to "archive".

        """
        if is_api_model(model):
            return 'api'
        return None

    def db_for_write(self, model, **hints):
        """
        Attempts to write to RedirectArchive go to "archive".

        """
        if is_api_model(model):
            return 'api'
        return None

    def allow_relation(self, obj1, obj2, **hints):
        """
        Prevent relations to the RedirectArchive table, since it should
        be on it's own database. This may need to be changed if we
        ever decide to host other tables on the same database as
        RedirectArchive.

        """
        if is_api_model(type(obj1)) or is_api_model(type(obj2)):
            return False
        return None

    def allow_migrate(self, db, model):
        """
        Make sure the RedirectArchive model only appears in the "archive"
        database.

        """
        print db
        print model
        if db == "api":
            return is_api_model(model)
        elif is_api_model(model):
            return False
        return None