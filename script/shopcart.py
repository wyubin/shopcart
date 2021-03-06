#!/usr/bin/python3
# coding=utf-8
import os,sys,json
import db_init
import views

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
        self.vars['pathDB'] = os.path.join(dirTool,self.config['pathDB'])

    def main(self):
        if self.args.get('init') or not os.path.exists(self.vars['pathDB']):
            db_init.init(self.vars['pathDB'])
        
        if not self.args.get('user'):
            sys.stderr.write('[WARN] Please input user name\n')
            sys.exit(0)
        views.init(self.vars['pathDB'])
        ## check user
        user = views.ckUser(self.args['user'])
        if not user:
            views.leave()
        #views.conf['user'] = user
        ## start
        countLoop=0
        while countLoop<3:
            views.showItem()
            strFunc = input("input item id | Edit ShopCart(s) | Checkout(c) | checkOrders(l) | Quit(q): ")
            if strFunc == 'q':
                views.leave()
            elif strFunc == 's':
                views.eCart_enter()
                countLoop=0
            elif strFunc == 'c':
                views.checkout()
                countLoop=0
            elif strFunc == 'l':
                views.showOrders(user)
                countLoop=0
            elif strFunc.isdigit():
                views.addItem(int(strFunc))
                countLoop=0
            else:
                countLoop += 1
        sys.stderr.write('[WARN] Error Operation more than 3 times!!\n')
        views.leave()


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description = pkg.__doc__, formatter_class = argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('-u','--user',help='input user name')
    parser.add_argument('--init',help='initial db', action='store_true')
    args = parser.parse_args()

    a=pkg(vars(args))
    a.main()
