"use model and other function tools to return data for routers"
import os,sys,json,StringIO
from datetime import date
from peewee import SqliteDatabase,fn
from model_tool import *
from models import *
from config import system as config
from util import guid, align_table_parser
sys.path.append('../python/share_app')

# link db
app_conf = config.mconfig['main']
db = SqliteDatabase(app_conf['app_db'])
db_proxy.initialize(db)

def stat():
	return {'ref_tab': ref_f(Ref.select().where(Ref.ac != None)).to_profile() }

def info(request):
	i_type = request.args.get('type','')
	if i_type == 'type_search':
		l_species, species2sero= {},{}
		# get species_sero map
		for i in Ncbispec.select().join(Ncbisero):
			l_species[i.id] = i.name
			species2sero[i.id] = dict([[x.id,x.name] for x in i.ncbisero if x.name])
		# get host
		l_host = dict([[x.id,x.name] for x in Host.select()])
		# get country
		l_continent, continent2country= {},{}
		for i in Continent.select().join(Country):
			l_continent[i.id] = i.name
			continent2country[i.id] = dict([[x.id,x.name] for x in i.countries])

		l_country = dict([[x.id,x.name] for x in Country.select()])
		# get year
		l_year = {}
		for i in Date.select().order_by(Date.date):
			t_year = i.date.strftime('%Y')
			l_year[t_year] = t_year

		return {'species':l_species,'species2sero':species2sero,'host':l_host,'country':l_country,'continent':l_continent,'continent2country':continent2country,
			'year':l_year
		};
	elif i_type == 'combine':
		l_species, spec2sero= {},{}
		for i in Species.select().join(Serotype):
			l_species[i.id] = i.name
			spec2sero[i.id] = dict([[x.id,x.name] for x in i.serotype if x.name[-2:] != 'NA'])
		return {'species':l_species,'spec2sero':spec2sero,'sero_num':Serotype.select().count()}
	elif i_type == 'stat':
		return region_f(Region.select()).to_profile()

def map_search(request):
	in_args = dict(((x,request.args.get(x,'')) for x in ['ntspec','ntsero','year1','year2','country']))
	t_sql = Nt.select()
	if in_args['ntspec']!='0':
		if in_args['ntsero']=='0':
			t_sql = t_sql.join(Ncbisero).join(Ncbispec).where(Ncbispec.id==in_args['ntspec'])
		else:
			t_sql = t_sql.join(Ncbisero).where(Ncbisero.id==in_args['ntsero'])
	# add time range
	dt_1 = date(int(in_args['year1']),1,1)
	dt_2 = date(int(in_args['year2']),12,31)
	t_sql = t_sql.join(Date,on=(Nt.date == Date.id)).where(Date.date>=dt_1,Date.date<=dt_2)
	tt_num = t_sql.count()
	# count country
	if in_args['country']:
		t_sql = t_sql.join(Country,on=(Nt.country == Country.id)).where(Country.name==in_args['country'])
		return nt_f(t_sql).to_profile()
	else:
		t_years = [x[0] for x in t_sql.select(Date.date.year).group_by(Date.date.year).tuples()]
		t_sql = t_sql.select(Country.name,Date.date.year,fn.COUNT(Country.id).alias('c_num')).join(Country,on=(Nt.country == Country.id)).group_by(Country.name,Date.date.year).tuples()
		c2c,un={},0
		for i in t_sql:
			if i[0] == 'unassigned':
				un += i[2]
			else:
				if i[0] not in c2c:
					c2c[i[0]] = [0]*len(t_years)
				y_ind = t_years.index(i[1])
				c2c[i[0]][y_ind] = i[2]
		return {'tt_num':tt_num,'years':t_years,'country2counts':c2c,'unassigned':un}

def ncbi_search(request):
	in_args = dict(((x,(request.args or request.form).get(x,'')) for x in ['s_type','o_type','des','ntspec','ntsero','refsero','dbspec','dbsero' ,'host','continent','ids']))
	temp = [in_args.update({x:request.args.getlist('%s[]' % x)}) for x in ['country','year']]
	if in_args['s_type']=='des':
		nt_list = []
		# if des <= 10 , then scan locusid
		if len(in_args['des']) <= 10 :
			temp = [nt_list.append(x) for x in Nt.select().where(Nt.version.contains(in_args['des']))]
		# scan description all the time
		temp = [nt_list.append(x) for x in Nt.select().where(Nt.des.contains(in_args['des']))]

	elif in_args['s_type']=='type':
		nt_list = []
		filter_time = 0
		# filter Nt by ncbisero first
		if in_args['ntspec'] and in_args['ntspec']!='0':
			if in_args['ntsero']!='0':
				nt_list = Ncbisero.get(Ncbisero.id == in_args['ntsero']).nts
			else:
				temp = [nt_list.extend(x.nts) for x in Ncbispec.get(Ncbispec.id == in_args['ntspec']).ncbiseros]
			# another filter for ref serotype
			if in_args['refsero'] and in_args['refsero']!='0':
				t_ref_id = set([Serotype.get(Serotype.id == in_args['refsero']).refs[0].id])
				nt_list = [x for x in nt_list if x.ref.id in t_ref_id]
			filter_time+=1

		# filter by db spec and geno
		if in_args['dbspec'] and in_args['dbspec']!='0':
			# get ref ids first
			if in_args['dbsero']!='0':
				t_ref_id = set([Serotype.get(Serotype.id == in_args['dbsero']).refs[0].id])
			else:
				t_ref_id = set([x.ref[0].id for x in Species.get(Species.id == in_args['dbspec']).serotypes])
			# start get nt
			if filter_time:
				nt_list = [x for x in nt_list if x.ref.id in t_ref_id]
			else:
				nt_list = Nt.select().join(Ref).where(Ref.id.in_(*list(t_ref_id)))
			filter_time+=1

		# filter by host
		if in_args['host'] and in_args['host']!='0':
			t_host_id = int(in_args['host'])
			if filter_time: # after species and serotype filter
				nt_list = [x for x in nt_list if x.host.id == t_host_id]
			else: # no filter from species and serotype
				nt_list = Host.get(Host.id == t_host_id).nts
			filter_time+=1

		# filter by country, generate country list
		if in_args['continent'] and in_args['continent']!='0':
			if '0' in in_args['country']:
				t_country_id = set([x.id for x in Continent.get(Continent.id == in_args['continent']).countries])
			else:
				t_country_id = set(map(int,in_args['country']))
			# generate nt list from country list
			if filter_time: # after species and serotype filter
				nt_list = [x for x in nt_list if x.country.id in t_country_id]
			else: # no filter from species and serotype
				print(t_country_id)
				nt_list = Nt.select().join(Country).where(Country.id.in_(*list(t_country_id)))
			filter_time+=1

		# filter by year
		if in_args['year'] and '0' not in in_args['year']:
			t_date = set()
			temp = [[t_date.add(y.id) for y in Date.select().where(Date.date.between('%s-01-01' % x,'%s-12-31' % x)) ] for x in in_args['year']]
			if filter_time: # after species and serotype filter
				nt_list = [x for x in nt_list if x.date and x.date.id in t_date]
			else: # no filter from species and serotype
				nt_list = Nt.select().join(Date).where(Date.id.in_(*list(t_date)))
			filter_time+=1
	elif in_args['s_type']=='locusid':
		nt_list = Nt.select().where(Nt.version.in_(*in_args['ids'].split(',')))

	if in_args['o_type']=='search':
		return nt_f(nt_list).to_profile()
	elif in_args['o_type']=='geno_dist':
		return nt_f(nt_list).to_geno_dist('db' if in_args['ntspec'] else 'nt')
	elif in_args['o_type']=='fasta':
		return nt_f(nt_list).to_fasta()
	elif in_args['o_type']=='blastform':
		return nt_f(nt_list).to_blastform()

def seq_get(request):
	s_type=request.form.get('type','')
	ids = request.form.get('id').split(',')
	key = request.form.get('key')
	if s_type=='nt':
		sel_nt = Nt.select().where(getattr(Nt,key).in_(*ids))
		return nt_f(sel_nt).to_fasta()
	elif s_type=='ref':
		sel_nt = Ref.select().where(getattr(Ref,key).in_(*ids))
		return ref_f(sel_nt).to_fasta()
	elif s_type=='region':
		sel_nt = Region.select().where(getattr(Region,key).in_(*ids))
		return seg_f(sel_nt[0].segment).to_fasta()

def gt_scan(request):
	"scan genotype region and return object for response"
	args = {x:request.form[x] for x in ['fa','mode','e','ws','ms','gc']}
	temp = [args.update({x:args[x].split(',')}) for x in ['ms','gc'] if args[x]]
	t_guid = guid.id_get()
	t_path = path.join(config.temp_dir,t_guid)
	open('%s.fa' % t_path,'w').write(args['fa'])
	if args['mode'] == 'nucleotide':
		cmd_pre = 'blastn -task dc-megablast -db %s/seg.fna -reward %s -penalty %s' % (app_conf['blast_db_dir'],args['ms'][0],args['ms'][1])
	else:
		cmd_pre = 'blastp -comp_based_stats 0 -db %s/aa_seg.fna' % app_conf['blast_db_dir']
	os.system(cmd_pre + ' -query %s.fa -out %s.out \
		-num_threads 8 -evalue %s -word_size %s -gapopen %s -gapextend %s\
		-outfmt "6 std gaps score qcovhsp" -max_target_seqs 3000 -max_hsps 1' % \
		(t_path,t_path,args['e'],args['ws'],args['gc'][0],args['gc'][1]))

	res = open('%s.out' % t_path).read()
	os.system('rm %s.*' % t_path)
	return {'res':res}

def gt_map(request):
	"input megablast result to get map object"
	t_tab = StringIO.StringIO()
	t_tab.write(request.form['gt_blast'])
	t_tab.seek(0)
	blast_r = []
	temp = [blast_r.extend(x) for x in align_table_parser.parser(t_tab,'blast',{'gaps':12,'score':13,'qcovhsp':14})]
	blast_out = blast_f(blast_r).reg_scan(request.form['mode'])
	return {'gt_map':blast_out}

def gt2rec(request):
	"transfer genotype job info to recombination"
	guid = request.args['gt_guid']
	job_path = os.path.join(config._basedir,config.mconfig['jobs']['doc_path'],guid)
	j_conf = json.load(open(os.path.join(job_path,'args.json')))
	p_fas = os.path.join(job_path,'align_gt.fna' if j_conf['mode']=='nucleotide' else 'append_seq.fna')
	return {'fas':open(p_fas).read(),'ref_ids':j_conf['refs'],'gt_guid':guid}

def exam_update(request):
	"revise example id and return it"
	f_json = os.path.join(config.static_dir,'json','args.json')
	t_args = json.load(open(f_json))
	[t_args['example_job'].update({x:request.args[x]}) for x in ['blast','genotype_nucleotide','genotype_protein','combine'] if x in request.args]
	json.dump(t_args,open(f_json,'w'))
	return t_args['example_job']
