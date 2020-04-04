#! /usr/bin/python3

import logging
import sys, os

logging.basicConfig(stream=sys.stderr)
sys.path.insert(0, '/var/www/Covid-19/')

os.chdir("/var/www/Covid-19/")

from site_covid import app as application
