#!/usr/bin/python3
# coding=utf-8
import os,sys,json
from datetime import datetime
from peewee import SqliteDatabase
import models as md

scriptDir = os.path.split(os.path.realpath(__file__))[0]
dirTool = os.path.join(scriptDir,'../')

_fmtTime = '%Y%m%d%H%M'
_fmtDate = '%Y%m%d'

def cleanDB(pathDB):
    if os.path.exists(pathDB):
        sys.stderr.write('[INFO] re-create DB\n')
        os.unlink(pathDB)
    md.db_proxy.create_tables([getattr(md,x) for x in md.tablesDB])

def table2list(pathTable):
    fileTable = open(pathTable)
    colnames = fileTable.readline().strip(' \n\r').split('\t')
    aData = []
    for tline in fileTable:
        trow = tline.strip(' \n\r').split('\t')
        aData.append(dict(zip(colnames,trow)))
    return aData

def init_orderInfo(pathTable):
    aData = table2list(pathTable)
    tCount = 0
    for dataTmp in aData:
        user,_ = md.User.get_or_create(name=dataTmp['user'])
        dt = datetime.strptime(dataTmp['date'],_fmtTime)
        md.Order_info.insert(
            user=user,
            date=dt,
            final_money = int(dataTmp['final_money']),
            sn=dataTmp['sn']
        ).execute()
        tCount += 1
    sys.stderr.write('[INFO] Insert {} records in Order_info\n'.format(tCount))

def init_item(pathTable):
    aData = table2list(pathTable)
    tCount = 0
    for dataTmp in aData:
        supplier,_ = md.Supplier.get_or_create(name=dataTmp['supplier'])
        md.Item.insert(
            name=dataTmp['name'],
            price=int(dataTmp['price']),
            supplier=supplier,
        ).execute()
        tCount += 1
    sys.stderr.write('[INFO] Insert {} records in Item\n'.format(tCount))

def init_order_item(pathTable):
    aData = table2list(pathTable)
    tCount = 0
    for dataTmp in aData:
        order = md.Order_info.select().where(md.Order_info.sn == dataTmp['order'])[0]
        item = md.Item.select().where(md.Item.name == dataTmp['item'])
        md.Order_item.insert(
            order=order,
            item=item,
            item_count=int(dataTmp['item_count']),
        ).execute()
        tCount += 1
    sys.stderr.write('[INFO] Insert {} records in order_item\n'.format(tCount))

def init_bonus(pathTable):
    aData = table2list(pathTable)
    tCount = 0
    for dataTmp in aData:
        listItem = md.Item.select().where(md.Item.name == dataTmp['free_item'])
        free_item = listItem[0] if listItem else None
        md.Bonus.insert(
            name=dataTmp['name'],
            discount_money=int(dataTmp['discount_money']),
            discount_percent=int(dataTmp['discount_percent']),
            free_item=free_item,
            free_shipping=bool(int(dataTmp['free_shipping'])),
        ).execute()
        tCount += 1
    sys.stderr.write('[INFO] Insert {} records in Bonus\n'.format(tCount))

def init_order_bonus(pathTable):
    aData = table2list(pathTable)
    tCount = 0
    for dataTmp in aData:
        order = md.Order_info.select().where(md.Order_info.sn == dataTmp['order'])[0]
        bonus = md.Bonus.select().where(md.Bonus.name == dataTmp['bonus'])
        md.Order_bonus.insert(
            order=order,
            bonus=bonus,
            discount_amount = int(dataTmp['discount_amount']),
        ).execute()
        tCount += 1
    sys.stderr.write('[INFO] Insert {} records in Order_bonus\n'.format(tCount))

def init_discount_rule(pathTable):
    aData = table2list(pathTable)
    tCount = 0
    for dataTmp in aData:
        listItem = md.Item.select().where(md.Item.name == dataTmp['sel_item'])
        sel_item = listItem[0] if listItem else None
        listSupplier = md.Supplier.select().where(md.Supplier.name == dataTmp['sel_supplier'])
        sel_supplier = listSupplier[0] if listSupplier else None
        listBonus = md.Bonus.select().where(md.Bonus.name == dataTmp['bonus'])
        bonus = listBonus[0] if listBonus else None
        md.Discount_rule.insert(
            name=dataTmp['name'],
            min_count=int(dataTmp['min_count']) if dataTmp['min_count'] else None,
            min_money=int(dataTmp['min_money']) if dataTmp['min_money'] else None,
            sel_item=sel_item,
            sel_supplier=sel_supplier,
            bonus=bonus,
            date_start=datetime.strptime(dataTmp['date_start'],_fmtDate) if dataTmp['date_start'] else None,
            date_end=datetime.strptime(dataTmp['date_end'],_fmtDate) if dataTmp['date_end'] else None,
            priority=int(dataTmp['priority']),
        ).execute()
        tCount += 1
    sys.stderr.write('[INFO] Insert {} records in Discount_rule\n'.format(tCount))

def init_discount_limit(pathTable):
    aData = table2list(pathTable)
    tCount = 0
    for dataTmp in aData:
        md.Discount_limit.insert(
            name=dataTmp['name'],
            max_money=int(dataTmp['max_money']) if dataTmp['max_money'] else None,
            max_time=int(dataTmp['max_time']) if dataTmp['max_time'] else None,
            by_user=bool(int(dataTmp['by_user'])),
            by_month=bool(int(dataTmp['by_month'])),
        ).execute()
        tCount += 1
    sys.stderr.write('[INFO] Insert {} records in Discount_limit\n'.format(tCount))

def init_rule_limits(pathTable):
    aData = table2list(pathTable)
    tCount = 0
    for dataTmp in aData:
        rule = md.Discount_rule.select().where(md.Discount_rule.name == dataTmp['rule'])[0]
        limit = md.Discount_limit.select().where(md.Discount_limit.name == dataTmp['limit'])
        md.Rule_limits.insert(
            rule=rule,
            limit=limit,
        ).execute()
        tCount += 1
    sys.stderr.write('[INFO] Insert {} records in rule_limits\n'.format(tCount))

def init(pathDB):
    md.db_proxy.initialize(SqliteDatabase(pathDB))
    cleanDB(pathDB)
    dirDB = os.path.join(dirTool,'static','db')
    pathTmp = os.path.join(dirDB,'orderInfo.tsv')
    if os.path.exists(pathTmp):
        init_orderInfo(pathTmp)
    pathTmp = os.path.join(dirDB,'item.tsv')
    if os.path.exists(pathTmp):
        init_item(pathTmp)
    pathTmp = os.path.join(dirDB,'order_item.tsv')
    if os.path.exists(pathTmp):
        init_order_item(pathTmp)
    pathTmp = os.path.join(dirDB,'bonus.tsv')
    if os.path.exists(pathTmp):
        init_bonus(pathTmp)
    pathTmp = os.path.join(dirDB,'order_bonus.tsv')
    if os.path.exists(pathTmp):
        init_order_bonus(pathTmp)
    pathTmp = os.path.join(dirDB,'discount_rule.tsv')
    if os.path.exists(pathTmp):
        init_discount_rule(pathTmp)
    pathTmp = os.path.join(dirDB,'discount_limit.tsv')
    if os.path.exists(pathTmp):
        init_discount_limit(pathTmp)
    pathTmp = os.path.join(dirDB,'rule_limits.tsv')
    if os.path.exists(pathTmp):
        init_rule_limits(pathTmp)

    md.db_proxy.close()
    sys.stderr.write('[INFO] Database initiation complete\n')