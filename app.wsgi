#!/var/www/html/fronty/venv/bin/python3.5
activate_this = '/home/ubuntu/pyflaskpro/venv/bin/activate_this.py'
with open(activate_this) as file_:
	exec(file_.read(), dict(__file__=activate_this))

import sys
import logging

logging.basicConfig(stream=sys.stderr)
sys.path.insert(0,"/var/www/html/pyflaskpro/")

from app import app as application
