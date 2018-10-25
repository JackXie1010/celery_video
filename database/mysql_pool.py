# coding:utf8

from db_pool import db
import ConfigParser
import os


conf_path = os.path.dirname(os.path.dirname(__file__))
config = ConfigParser.ConfigParser()
config_file = 'dbconfig.ini'
config.read(conf_path + '/config/' + config_file)
async_db = db.DB(host=config.get('database1', 'host'), port=config.get('database1', 'port'), database=config.get('database1', 'db'), user=config.get('database1', 'user'),
                 password=config.get('database1', 'passwd'),
                 init_command="set names utf8")

if __name__ == '__main__':
    print(os.path.dirname(conf_path))
    print(conf_path)
