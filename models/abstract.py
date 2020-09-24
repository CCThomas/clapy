class AbstractModel:
    def __init__(self, model_tuple=None):
        schema = self.get_schema()
        tuple_index = 0
        for schema_key in schema:
            setattr(self, schema_key, None if model_tuple is None else model_tuple[tuple_index])
            tuple_index = tuple_index + 1

    def post_load(self):
        pass

    def pre_persist(self):
        pass

    @staticmethod
    def var_to_str(var):
        return str(var) if var is not None else "'None'"

    @staticmethod
    def get_schema():
        raise Exception("Not Implemented: get_schema")

    def __str__(self):
        schema = self.get_schema()
        variables = ''
        for schema_key in schema:
            variables = variables + schema_key + '=' + self.var_to_str(getattr(self, schema_key)) + ","
        return self.__class__.__name__ + '{' + variables[:-1] + '}'
