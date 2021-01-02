from peewee import Model,CharField,TextField,ForeignKeyField,IntegerField,DatabaseProxy,DateTimeField,BooleanField
db_proxy = DatabaseProxy()

tables = ['User','Order_info','Supplier','Item','Order_item','Bonus','Discount_rule','Discount_limit'],

class Base(Model):
    class Meta:
        database = db_proxy

class User(Base):
    name = CharField(unique=True)

class Order_info(Base):
    sn = TextField(unique=True)
    date = DateTimeField()
    user = ForeignKeyField(User, backref='orders')
    discount_ck = BooleanField()
    discount_amount = IntegerField()
    final_money = IntegerField()

class Supplier(Base):
    name = CharField(unique=True)

class Item(Base):
    name = CharField(unique=True)
    supplier = ForeignKeyField(Supplier, backref='items')
    price = IntegerField()

class Order_item(Base):
    order = ForeignKeyField(Order_info, backref='items')
    item = ForeignKeyField(Item, backref='orders')
    item_count = IntegerField()

class Bonus(Base):
    discount_money = IntegerField(null=True)
    discount_percent = IntegerField(null=True)
    free_item = ForeignKeyField(Item, backref='ref_bonus')
    free_shipping = BooleanField()

class Discount_rule(Base):
    min_count = IntegerField(null=True)
    min_money = IntegerField(null=True)
    sel_item = ForeignKeyField(Item, backref='ref_disc_rules', null=True)
    sel_supplier = ForeignKeyField(Supplier, backref='ref_disc_rules', null=True)
    bouns = ForeignKeyField(Bonus, backref='ref_disc_rules')
    active = BooleanField()

class Discount_limit(Base):
    max_money = IntegerField(null=True)
    max_time = IntegerField(null=True)
    by_user = BooleanField()
    by_month = BooleanField()
    date_start = DateTimeField(null=True)
    date_end = DateTimeField(null=True)