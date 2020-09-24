# clapy
Command Line Application - python

# Usage
```python
from clapy.configuration import application_config
from clapy.server.cli_server import run
import sys

# Get Arguments
argv = sys.argv

# Configure Application
application_config.configure('CLAPY!', argv)

# Run application
run()
```
