from peewee import Model,CharField,TextField,ForeignKeyField,IntegerField,Proxy,DateTimeField,BooleanField
db_proxy = Proxy()

tables = ['Species','Serotype','Ref','Region','Source','Segment','Host','Continent','Country','Date','Ncbispec','Ncbisero','Nt']

class Base(Model):
	class Meta:
		database = db_proxy

class Species(Base):
	name = CharField(unique=True)

class Serotype(Base):
	name = CharField(unique=True)
	full_name = CharField(unique=True)
	species = ForeignKeyField(Species, related_name='serotypes')

class Ref(Base):
	ac = CharField(unique=True,null=True)
	seq = TextField(null=True)
	aa_seq = TextField(null=True)
	serotype = ForeignKeyField(Serotype, related_name='refs')

class Region(Base):
	name = CharField(unique=True)

class Source(Base):
	name = CharField(unique=True)

class Segment(Base):
	ref = ForeignKeyField(Ref, related_name='segments')
	region = ForeignKeyField(Region, related_name='segments')
	source = ForeignKeyField(Source, related_name='segments')
	start = IntegerField()
	end = IntegerField()
	aa_start = IntegerField(null=True)
	aa_end = IntegerField(null=True)

class Host(Base):
	name = CharField(unique=True)

class Continent(Base):
	name = CharField(unique=True)

class Country(Base):
	name = CharField(unique=True)
	continent = ForeignKeyField(Continent, related_name='countries')

class Date(Base):
	date = DateTimeField()

class Ncbispec(Base):
	name = CharField(unique=True)

class Ncbisero(Base):
	name = CharField()
	ncbispec = ForeignKeyField(Ncbispec, related_name='ncbiseros')

class Nt(Base):
	version = CharField(unique=True)
	seq = TextField()
	des = TextField()
	ex_ref = BooleanField()
	ref = ForeignKeyField(Ref, related_name='nts')
	host = ForeignKeyField(Host, related_name='nts')
	country = ForeignKeyField(Country, related_name='nts')
	date = ForeignKeyField(Date, related_name='nts', null=True)
	ncbisero = ForeignKeyField(Ncbisero, related_name='nts', null=True)
