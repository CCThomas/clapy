# author: Christopher Thomas ~ github.com/CCThomas
# created: Sept 24th 2020
# version: 0.1.0


from configuration import application_config
from server.cli_server import run
import sys

if sys.version_info < (3, 0):
    print('Python version 3+ required')
    print('Download Python 3 here:\nhttps://www.python.org/downloads/')
    sys.exit(0)

# Get Arguments
argv = sys.argv

# Configure Application
application_config.configure('CLAPY!', argv)

# Run application
run()
