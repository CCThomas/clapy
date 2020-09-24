from clapy.data_access.abstract import AbstractDataAccess
from clapy.models.abstract import AbstractModel
import logging
import mysql.connector


class MySqlDataAccess(AbstractDataAccess):
    def __init__(self, config):
        self.current_database_name = None
        self.host = config['host']
        self.user = config['user']
        self.password = config['password']

    def connect(self, database_name):
        """
        Connect to the Database.

        :param database_name: name of the database.
        """
        self._load_database_name(database_name)
        if not self._exists(self._get_databases(), self.current_database_name):
            logging.debug('Creating Database')
            my_cursor = self._get_cursor()
            sql = "CREATE DATABASE " + self.current_database_name
            logging.debug('executing sql=%s', sql)
            my_cursor.execute(sql)
            logging.debug('committing to my_database')
            self.my_database.commit()
        self._load_my_database(with_db_connection=True)

    def find_by(self, model, query, instance=None):
        """
        Find and Return list of instances for desired model for query.

        :param model: Model you are wanting returned.
        :param query: Dict config of the desired query to execute.
        {
            'where_x': [value_1, value_..., value_n],
            'and_y': [value_a],
            'or_z': [value_!]
        }
        :param instance: Specify what instance the values from the rows return should be saved to. (provided primarily
        for the use of recursive calls to find parent class data)
        :return: list if instances, for all the rows returned for the provided query.
        """
        logging.debug("Find %s by query=%s", model.__name__, query)
        if model is AbstractModel:
            logging.debug('Base Find by')
            return
        if getattr(model, 'get_schema', None) is None:
            print('Not Acceptable instance')
            return
        self._load_table_of_not_exists(model)

        sql = 'SELECT * FROM ' + model.__name__

        def _build_in_statement(items):
            stmt = ''
            for item in items:
                stmt = stmt + str(item) + ","
            return stmt[:-1]

        for query_key in query:
            sql = sql + ' ' + query_key.replace('_', ' ') + " in (" + _build_in_statement(query[query_key]) + ")"
        logging.debug('executing sql=%s', sql)

        my_cursor = self._get_cursor()
        my_cursor.execute(sql)
        instance_tuples = my_cursor.fetchall()
        logging.debug('sql executed and found=%s', instance_tuples)
        instances = []

        for instance_tuple in instance_tuples:
            i = 0
            schema = model.get_schema()
            instance = model() if instance is None else instance
            for key in schema:
                setattr(instance, key, instance_tuple[i])
                i = i + 1
            instance.post_load()
            query = {
                'where_id': [instance.id]
            }
            self.find_by(model.__base__, query, instance=instance)
            instances.append(instance)

        logging.debug("returning instances=%s", instances)
        return instances

    def get_database_names(self):
        """
        :return: database names this application manages.
        """
        names = []
        from configuration.application_config import app_name
        for n in self._get_databases():
            if app_name in n[0]:
                names.append(n[0].replace(app_name + '_', ''))
        return names

    def nuke(self):
        """
        Nuke all databases this application manages.
        """
        logging.debug('Nuke Databases')
        for name in self.get_database_names():
            self.nuke_database(name)

    def nuke_database(self, database_name):
        """
        Nuke only the database for the given param.

        :param database_name: database name to nuke.
        """
        logging.debug('Nuke Database %s', database_name)
        self._load_database_name(database_name)
        self._load_my_database()
        my_cursor = self._get_cursor()
        sql = "DROP DATABASE " + self.current_database_name
        logging.debug('executing sql=%s', sql)
        my_cursor.execute(sql)
        logging.debug('committing to my_database')
        self.my_database.commit()

    def save(self, instance, model=None):
        """
        Save the instance provided.

        :param instance: instance of object to save
        :param model: Specify what model/table to save to.
        :return: persisted instances will be returned. Although implementation may modify the original instance itself
        """
        logging.debug('saving instance=%s with model=%s', instance, model)
        if model is None:
            model = instance.__class__
        if model is AbstractModel:
            logging.debug('Base Model hit for save')
            return None
        if getattr(model, 'get_schema', None) is None:
            print(instance, 'is missing static method="get_schema"')
            return None

        self._load_table_of_not_exists(instance.__class__)

        self.save(instance, model.__base__)

        sql = None
        schema = instance.get_schema()
        query = {
            'where_id': [instance.id]
        }

        instance.pre_persist()

        if instance.id is not None and len(self.find_by(instance.__class__, query)) != 0:
            columns_and_values = ''
            for column_key in schema:
                columns_and_values = columns_and_values + column_key + ' = ' + '%(' + column_key + ")s,"
            columns_and_values = columns_and_values[:-1]
            sql = 'UPDATE ' + instance.__class__.__name__ + " SET " + columns_and_values + ' WHERE id = %(id)s'
        else:
            columns = "INTO " + instance.__class__.__name__ + "("
            values = "VALUES ("
            for column_key in schema:
                if column_key == 'id' and instance.id is None:
                    continue
                columns = columns + column_key + ","
                values = values + '%(' + column_key + ")s,"
            columns = columns[:-1] + ") "
            values = values[:-1] + ")"
            sql = 'INSERT ' + columns + values

        logging.debug('executing sql=%s with values=%s', sql, instance.__dict__)
        my_cursor = self._get_cursor()
        my_cursor.execute(sql, instance.__dict__)

        if my_cursor.rowcount == 1:
            logging.debug('saved class=%s with id=%s', instance, my_cursor.lastrowid)
            if instance.id is None:
                instance.id = my_cursor.lastrowid
        else:
            logging.debug('Failing to insert clazz=%s', instance)
            print('Failed to insert!')

        logging.debug('committing to my_database')
        self.my_database.commit()

        logging.debug('Returning clazz=%s', instance)
        return instance

    def _get_cursor(self):
        return self.my_database.cursor(buffered=True)

    def _get_databases(self):
        self._load_my_database()
        my_cursor = self._get_cursor()
        sql = 'SHOW DATABASES'
        logging.debug('executing sql=%s', sql)
        my_cursor.execute(sql)
        return my_cursor

    def _load_database_name(self, database_name):
        from configuration.application_config import app_name
        self.current_database_name = app_name + '_' + database_name

    def _load_my_database(self, with_db_connection=None):
        logging.debug('load db with_db_connection=%s', with_db_connection)
        if with_db_connection is not None:
            logging.debug('loading my_database with host=%s, user=%s, password=<redacted>, and database=%s', self.host,
                          self.user, self.current_database_name)
            self.my_database = mysql.connector.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                database=self.current_database_name
            )
        else:
            logging.debug('loading my_database with host=%s, user=%s, and password=<redacted>', self.host, self.user)
            self.my_database = mysql.connector.connect(
                host=self.host,
                user=self.user,
                password=self.password
            )

    def _load_table_of_not_exists(self, model):
        logging.debug('does database exists with name=%s', model.__name__)
        my_cursor = self._get_cursor()
        sql = 'SHOW TABLES'
        logging.debug('executing sql=%s', sql)
        my_cursor.execute(sql)
        if not self._exists(my_cursor, model.__name__):
            logging.debug('Creating table for class=%s', model.__name__)
            my_cursor = self._get_cursor()

            sql = 'CREATE TABLE ' + model.__name__ + ' ('
            schema = model.get_schema()
            for column_key in schema:
                sql = sql + column_key + " " + schema[column_key] + ","
            sql = sql[:-1] + ")"

            logging.debug('executing sql=%s', sql)
            my_cursor.execute(sql)
            logging.debug('committing to mydb')
            self.my_database.commit()

    @staticmethod
    def _exists_in_cursor(my_cursor, name):
        logging.debug('does name=%s exist in my_cursor=%s', name, my_cursor)
        found = False
        for x in my_cursor:
            logging.debug('checking name=%s with x=%s', name, x)
            if x[0] == name:
                logging.debug('Found match!')
                found = True
                break
        logging.debug('does exits returning=%s', found)
        return found

