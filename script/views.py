"use models.py to return data for shopcart.py"
import os,sys
from datetime import date
from peewee import SqliteDatabase,fn
from prettytable import PrettyTable
import models as md

conf = {}

def init(pathDB):
    md.db_proxy.initialize(SqliteDatabase(pathDB))
    conf['item2count'] = {}

def ckUser(nameUser):
    listUser = md.User.select().where(md.User.name == nameUser)
    if listUser:
        return listUser[0]
    ## create user
    countLoop=0
    while countLoop<3:
        ck_create = input('create "{}" account?(y/n):'.format(nameUser))
        if ck_create=='n':
            return False
        elif ck_create=='y':
            user = md.User.create(name=nameUser)
            return user
        countLoop += 1
    return False

def leave():
    sys.stderr.write('[WARN] Leave system, bye~~\n')
    sys.exit(0)

def showItem():
    if conf.get('str_items'):
        print(conf['str_items'])
        return True
    ## collect item
    x = PrettyTable()
    x.field_names = ["id","name","supplier","price"]
    for sItem in md.Item.select():
        x.add_row([sItem.id,sItem.name,sItem.supplier.name,sItem.price])
    
    conf['str_items'] = x.get_string()
    print(conf['str_items'])

def addItem(item_id):
    listItem = md.Item.select().where(md.Item.id == item_id)
    countLoop=0
    while countLoop<3:
        if not listItem.count():
            sys.stderr.write('[WARN] no "{}" item id\n'.format(item_id))
            return False
        strNum = input("input item number | back(b) | Quit(q): ")
        if strNum == 'q':
            leave()
        elif strNum == 'b':
            return False
        elif strNum.isdigit():
            eCart_item(listItem[0],int(strNum))
            return listItem[0]
        ## add into cart
        sys.stderr.write('[WARN] input correct number or operation code\n')
        countLoop += 1
    sys.stderr.write('[INFO] No add item\n')
    return False

def eCart_item(objItem,countItem):
    moneySum = objItem.price * countItem
    sys.stderr.write('[INFO] Select "{}" * {}, total: {}\n'.format(objItem.name, countItem, moneySum))
    countLoop=0
    while countLoop<3:
        strCk = input("Confirm put into Cart(y/n): ")
        if strCk=='n':
            return False
        elif strCk=='y':
            conf['item2count'].setdefault(objItem.id,countItem)
            showCart()
            return True
        countLoop += 1
    return False

def showCart():
    return True