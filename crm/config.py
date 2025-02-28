import os
from configparser import ConfigParser


DB = 'DB'
HOST = 'HOST'
NAME = 'NAME'
USER = 'USER'
PORT = 'PORT'
PASSWORD = 'PASSWORD'


class Config:
    _instance = None

    @staticmethod
    def get_instance():
        if not Config._instance:
            Config._instance = Config()
        return Config._instance

    def __init__(self):
        self.config = ConfigParser()
        self.config.read('config.ini')

    def get_property(self, section, item):
        env_variable = "{}_{}".format(section, item)
        value = os.environ.get(env_variable)
        if not value:
            value = self.config.get(section, item)
        if value == 'None':
            return None
        return value


    
    @property
    def db_host(self):
        return self.get_property(DB, HOST )
    
    @property
    def db_name(self):
        return self.get_property(DB, NAME )
    
    @property
    def db_user(self):
        return self.get_property(DB, USER )
    @property
    def db_port(self):
        return self.get_property(DB, PORT)

    @property
    def db_password(self):
        return self.get_property(DB, PASSWORD )


if __name__ == '__main__':
    config = Config.get_instance()
    
    
