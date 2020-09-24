class AbstractDataAccess:
    def connect(self, database_name):
        """
        Connect to the Database.

        :param database_name: name of the database.
        """
        pass

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
        pass

    def get_database_names(self):
        """
        :return: database names this application manages.
        """
        pass

    def nuke(self):
        """
        Nuke all databases this application manages.
        """
        pass

    def nuke_database(self, database_name):
        """
        Nuke only the database for the given param.

        :param database_name: database name to nuke.
        """
        pass

    def save(self, instance, model=None):
        """
        Save the instance provided.

        :param instance: instance of object to save
        :param model: Specify what model/table to save to.
        :return: persisted instances will be returned. Although implementation may modify the original instance itself
        """
        pass
