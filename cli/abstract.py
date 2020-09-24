class AbstractCLI:

    def __init__(self):
        self.message = None

    def execute(self):
        raise Exception('Not Implemented')

    @staticmethod
    def get_choice(header, options):
        """
        :param header:
        :param options: {
          'key' : 'display'
        }
        :return:
        """
        while True:
            print(header)
            for key in options:
                print(options[key])
            user_input = input('> ')
            if user_input in options:
                return user_input
