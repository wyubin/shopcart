"calculate discount and save order"
import sys
import datetime
from uuid import uuid4

conf = {}

def id_get(ex_set=set()):
    id = uuid4().hex
    if id in ex_set:
        return id_get(ex_set)
    else:
        return id

def init(md,user):
    "hook md and user in conf"
    conf['md'] = md
    conf['user'] = user

def ckLimit(rule,moneyDiscount):
    if not rule.sets_limit:
        return True
    now = datetime.datetime.now()
    for rule_limit in rule.sets_limit:
        queryTmp = rule.bonus.sets_order.select().join(conf['md'].Order_info)
        limitTmp = rule_limit.limit
        if limitTmp.by_user:
            queryTmp = queryTmp.where(conf['md'].Order_info.user == conf['user'])
        if limitTmp.by_month:
            queryTmp = queryTmp.where(conf['md'].Order_info.date.month == now.month)
        discountDB,timeDB = sum([x.discount_amount for x in queryTmp]), len(queryTmp)
        #sys.stderr.write('[INFO] Limit:"{}", discountDB: {}({}), timeDB: {}({})\n'.format(limitTmp.name,+moneyDiscount,limitTmp.max_money,timeDB+1,limitTmp.max_time))
        ## return False if one ck
        if limitTmp.max_money and discountDB+moneyDiscount >  limitTmp.max_money:
            sys.stderr.write('[INFO] Discount({}) exceed max_money({}), "{}" discount can not apply!\n'.format(discountDB+moneyDiscount,limitTmp.max_money,rule.name))
            return False
        if limitTmp.max_time and timeDB+1 > limitTmp.max_time:
            sys.stderr.write('[INFO] Discount time({}) exceed max_time({}), "{}" discount can not apply!\n'.format(timeDB+1, limitTmp.max_time,rule.name))
            return False
    return True

def calDiscount(moneyTmp,bonus):
    "calculate money will be discount based on bonus"
    moneyDiscount = 0
    if bonus.discount_money:
        moneyDiscount += bonus.discount_money
    elif bonus.discount_percent:
        moneyDiscount += moneyTmp*bonus.discount_percent/100
    
    return moneyDiscount

def getDiscount(item2count):
    now = datetime.datetime.now()
    md_rule = conf['md'].Discount_rule
    rules = md_rule.select().where((md_rule.date_start <= now) & (md_rule.date_end > now)).order_by(md_rule.priority.asc())
    listDiscount = []
    itemCounts = item2count.values()
    moneycurr = sum([x[0].price*x[-1] for x in itemCounts])
    countTotal = sum([x[-1] for x in itemCounts])
    for rule in rules:
        itemCountsTmp = itemCounts
        moneyTmp = moneycurr
        countTmp = countTotal
        ckSelitem = False
        if rule.sel_supplier:
            itemCountsTmp = [x for x in itemCountsTmp if x[0].supplier.id == rule.sel_supplier.id]
            ckSelitem = True
        if rule.sel_item:
            itemCountsTmp = [x for x in itemCountsTmp if x[0].id == rule.sel_item.id]
            ckSelitem = True
        if ckSelitem:
            moneyTmp = sum([x[0].price*x[-1] for x in itemCountsTmp])
            countTmp = sum([x[-1] for x in itemCountsTmp])
        if rule.min_count and countTmp < rule.min_count:
            continue
        if rule.min_money and moneyTmp < rule.min_money:
            continue
        moneyDiscount = calDiscount(moneyTmp,rule.bonus)
        if not ckLimit(rule,moneyDiscount):
            continue
        moneycurr -= moneyDiscount
        listDiscount.append([rule,moneyDiscount])
    
    return listDiscount,moneycurr

def count(item2count):
    "return discount"
    listDiscount,moneycurr = getDiscount(item2count)
    return listDiscount,moneycurr

def checkout(item2count,listDiscount):
    ## calculate again
    discountNew,moneyNew = getDiscount(item2count)
    if discountNew!=listDiscount:
        return discountNew,moneyNew
    ## generate sn
    ex_set = set([x.sn for x in conf['md'].Order_info.select()])
    idCheckout = id_get(ex_set)
    ## save Order_info
    orderInfo = conf['md'].Order_info.create(
        sn=idCheckout,date=datetime.datetime.now(),user=conf['user'],final_money=moneyNew
    )
    ## save Order_item
    for itemTmp, countTmp in item2count.values():
        conf['md'].Order_item.create(
            order=orderInfo,item=itemTmp,item_count=countTmp
        )
    ## save Order_bonus
    for ruleTmp, discountTmp in discountNew:
        conf['md'].Order_bonus.create(
            order=orderInfo,bonus=ruleTmp.bonus,discount_amount=discountTmp
        )
    return idCheckout
