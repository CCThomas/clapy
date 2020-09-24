from clapy.cli.menu_cli import MenuCLI


def run():
    current_cli = MenuCLI()
    while True:
        message = current_cli.execute()
        if message == 'MenuCLI':
            current_cli = MenuCLI()
        else:
            print('message:', message)
