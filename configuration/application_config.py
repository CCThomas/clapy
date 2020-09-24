import logging


# Global Variables
app_name = None

# Globally Components
data_access = None


def execute_argv(argv):
    logging.debug('Executing arguments: starting')
    print('todo: execute_argv')
    print(argv)
    logging.debug('Executing arguments: finished')


def configure(app_name_prov='clapy', argv=None):
    # set app name
    global app_name
    app_name = app_name_prov

    # set logging
    from datetime import datetime
    log_name = app_name + str(datetime.now().time()) + '.log'
    logging.basicConfig(filename=log_name, level=logging.DEBUG)

    # set global data access
    from data_access.mysql_data_access import MySqlDataAccess
    config = {
        'host': 'localhost',
        'user': 'root',
        'password': 'password',
    }
    global data_access
    data_access = MySqlDataAccess(config)

    # execute args
    if argv is not None:
        execute_argv(argv)


