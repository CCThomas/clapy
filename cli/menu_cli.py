from clapy.cli.abstract import AbstractCLI


class MenuCLI(AbstractCLI):
    def execute(self):
        options = {
            'h': '(h)ello world',
            'q': '(q)uit',
        }

        from clapy.configuration.application_config import app_name
        choice_key = self.get_choice('Welcome to ' + str(app_name), options)

        if choice_key == 'h':
            print('Hello World!')
        elif choice_key == 'q':
            quit()
        return 'todo'
