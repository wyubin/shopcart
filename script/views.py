"use model and other function tools to return data for routers"
import os,sys,json
from datetime import date
from peewee import SqliteDatabase,fn
from models import *

scriptDir = os.path.split(os.path.realpath(__file__))[0]
dirTool = os.path.join(scriptDir,'../')

class pkg():
    """shopcart.py: 
    interactive tools for shopcart
    """

    def __init__(self, args={}):
        "add all options var into self"
        self.args = {}
        self.args.update(args)
        self.vars = {}
        self.prepare()
    
    def prepare(self):
        pathConf = os.path.join(dirTool,'static','settings','config.json')
        self.config = json.load(open(pathConf))
        pathDB = os.path.join(dirTool,self.config['pathDB'])
        db_proxy.initialize(SqliteDatabase(pathDB))

    def main(self):
        return True

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description = pkg.__doc__, formatter_class = argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('-u','--user',help='input user name', required=True)
    args = parser.parse_args()

    a=pkg(vars(args))
    a.main()
