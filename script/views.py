"use models.py to return data for shopcart.py"
import sys
from datetime import date
from peewee import SqliteDatabase,fn
from prettytable import PrettyTable
import models as md
import discount

_fmtTime = '%Y%m%d%H%M'

conf = {}

def init(pathDB):
    md.db_proxy.initialize(SqliteDatabase(pathDB))
    conf['item2count'] = {}

def ckUser(nameUser):
    listUser = md.User.select().where(md.User.name == nameUser)
    if listUser:
        discount.init(md,listUser[0])
        return listUser[0]
    ## create user
    countLoop=0
    while countLoop<3:
        ck_create = input('create "{}" account?(y/n):'.format(nameUser))
        if ck_create=='n':
            return False
        elif ck_create=='y':
            user = md.User.create(name=nameUser)
            discount.init(md,user)
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
    itemSel,countCart = ckItemCart(item_id)
    if countCart:
        sys.stderr.write('[INFO] "{}" in Cart by {} number\n'.format(itemSel.name, conf['item2count'][itemSel.id][-1]))
    countLoop=0
    while countLoop<3:
        if not itemSel:
            return False
        strNum = input("input item number | back(b) | Quit(q): ")
        if strNum == 'q':
            leave()
        elif strNum == 'b':
            return False
        elif strNum.isdigit():
            eCart_editNumber(itemSel,int(strNum))
            return itemSel
        ## add into cart
        sys.stderr.write('[WARN] input correct number or operation code\n')
        countLoop += 1
    sys.stderr.write('[INFO] No add item\n')
    return False

def eCart_editNumber(objItem,countItem):
    if countItem < 1:
        sys.stderr.write('[WARN] Please input item number more than 0!\n')
        return False
    moneySum = objItem.price * countItem
    sys.stderr.write('[INFO] Select "{}" * {}, total: {}\n'.format(objItem.name, countItem, moneySum))
    countLoop=0
    while countLoop<3:
        strCk = input("Confirm put into Cart(y/n): ")
        if strCk=='n':
            return False
        elif strCk=='y':
            conf['item2count'].update({objItem.id:[objItem,countItem]})
            showCart()
            return True
        countLoop += 1
    sys.stderr.write('[INFO] No add item in Cart!\n')
    return False

def ckItemCart(idItem):
    "return objItem,countCart to get item info"
    listItem = md.Item.select().where(md.Item.id == idItem)
    if not listItem:
        sys.stderr.write('[WARN] no "{}" item id\n'.format(idItem))
        return None,None
    return listItem[0],conf['item2count'].get(idItem,[None,0])[-1]

def eCart_enter():
    if not conf['item2count']:
        sys.stderr.write('[INFO] No item in Cart!\n')
        return False
    showCart()
    countLoop=0
    while countLoop<3:
        strNum = input("input item id to edit | back(b) | Quit(q): ")
        if strNum == 'q':
            leave()
        elif strNum == 'b':
            return False
        elif strNum.isdigit():
            itemSel,countCart = ckItemCart(int(strNum))
            if not itemSel:
                countLoop += 1
                continue
            if not countCart:
                sys.stderr.write('[WARN] "{}" not in Cart\n'.format(itemSel.name))
                countLoop += 1
                continue
            cktmp = eCart_item(itemSel)
            if cktmp:
                sys.stderr.write('[INFO] Change Cart item Success!\n')
            continue
        countLoop += 1
    sys.stderr.write('[INFO] exit Cart!\n')
    return False

def eCart_item(itemSel):
    "change item count or remove it in cart"
    countLoop1=0
    while countLoop1<3:
        strNum = input("input item number | Remove all of this item(r) | back(b): ")
        if strNum == 'b':
            return False
        elif strNum.isdigit():
            return eCart_editNumber(itemSel, int(strNum))
        elif strNum == 'r':
            countLoop2=0
            while countLoop2<3:
                strCk = input('Confirm remove "{}" into Cart(y/n): '.format(itemSel.name))
                if strCk=='n':
                    return False
                elif strCk=='y':
                    del conf['item2count'][itemSel.id]
                    showCart()
                    return True
                countLoop2 += 1
            sys.stderr.write('[WARN] Do not remove "{}"!\n'.format(itemSel.name))
            return False
        sys.stderr.write('[WARN] Error Operation!\n')
        countLoop1 += 1
    return False

def showCart():
    if not conf['item2count']:
        sys.stderr.write('[INFO] Cart is empty!\n')
        return False
    ## show content
    sys.stdout.write('Menu:\n')
    x = PrettyTable()
    x.field_names = ["id","name","supplier","price",'count','summary']
    for itemTmp,countItem in conf['item2count'].values():
        sumTmp = itemTmp.price*countItem
        x.add_row([itemTmp.id,itemTmp.name,itemTmp.supplier.name,itemTmp.price,countItem,sumTmp])
    print(x.get_string())
    listDiscount,moneyFinal = discount.count(conf['item2count'])
    showDiscount(listDiscount,moneyFinal)
    return listDiscount

def showDiscount(listDiscount,moneyFinal):
    sys.stdout.write('[INFO] Apply {} discount: {}\n'.format(len(listDiscount), ' ,'.join(['{}({})'.format(x[0].name,x[-1]) for x in listDiscount])))
    sys.stdout.write('[INFO] Checkout amount: {}\n'.format(moneyFinal))

def checkout():
    ckCart = showCart()
    if ckCart == False:
        return False
    countLoop=0
    while countLoop<3:
        strCk = input("Confirm check out the Cart(y/n): ")
        if strCk=='n':
            return False
        elif strCk=='y':
            sn_checkout = discount.checkout(conf['item2count'],ckCart)
            if type(sn_checkout) == str:
                sys.stderr.write('[INFO] Keep our serial number:{}\n'.format(sn_checkout))
                ## clean 
                conf['item2count'] = {}
                return True
            else:
                ckCart = sn_checkout[0]
                sys.stderr.write('[WARN] Discount changed, please check again!\n')
                showDiscount(*sn_checkout)
                continue
        sys.stderr.write('[WARN] Error Operation!\n')
        countLoop += 1
    sys.stderr.write('[INFO] Do not check out the Cart!\n')
    return False

def showOrders(user=None):
    countLoop=0
    queryTmp = md.Order_info.select()
    if user:
       queryTmp = queryTmp.where(user==user)
    lenOrder = queryTmp.count()
    if not lenOrder:
        sys.stderr.write('[WARN] no associated sn!\n')
    while countLoop<3:
        showOrderInfos(queryTmp)
        strID = input("Input rawID that you want to check: ")
        if strID.isdigit() and int(strID)<= lenOrder:
            showOrderSN(queryTmp[int(strID)-1])
            return True
        countLoop +=1
    sys.stderr.write('[INFO] Back to homepage!\n')
    return False

def showOrderInfos(qOrderInfo):
    x = PrettyTable()
    x.field_names = ["rawID","User","date","checkout money","sn"]
    countTmp = 0
    for fetchTmp in qOrderInfo:
        countTmp += 1
        x.add_row([countTmp,fetchTmp.user.name, fetchTmp.date.strftime(_fmtTime),fetchTmp.final_money, fetchTmp.sn])
    print(x.get_string())

def showOrderSN(objOrder):
    sys.stderr.write('[INFO] Order on {} by {} money.\n'.format(objOrder.date.strftime(_fmtTime), objOrder.final_money))
    sys.stdout.write('Items:\n')
    x = PrettyTable()
    x.field_names = ["name","supplier","price",'count','summary']
    for itemTmp in objOrder.items:
        objItem = itemTmp.item
        x.add_row([objItem.name, objItem.supplier, objItem.price, itemTmp.item_count, objItem.price*itemTmp.item_count])
    print(x.get_string())

    sys.stdout.write('Discounts:\n')
    x = PrettyTable()
    x.field_names = ["name","discount_amount"]
    for bonusTmp in objOrder.sets_bonus:
        objItem = itemTmp.item
        x.add_row([bonusTmp.bonus.name, bonusTmp.discount_amount])
    print(x.get_string())
