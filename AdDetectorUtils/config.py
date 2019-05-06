from os import getenv
from configparser import ConfigParser


config = ConfigParser()
config.read(getenv('CONFIG_PATH') or 'config.ini', encoding='utf-8')

