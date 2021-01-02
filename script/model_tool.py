import json
from config import system as config
from os import path
from app.main.models import *

class ref_f():
	"parse ref list to format that assigned"
	def __init__(self,model_l):
		self.model_l = model_l

	def to_profile(self):
		"json for table view"
		t_title = ['Accession no.','Sepecies','Genotype','Acronym','Length','Region','Segment number']
		t_data = []
		for i in self.model_l:
			t_data.append([i.ac,i.serotype.species.name,i.serotype.full_name,i.serotype.name,len(i.seq),i.region,len(i.segment)])

		return dict(colnames=t_title ,data=t_data)

	def to_fasta(self):
		name, seq = [],[]
		for i in self.model_l:
			sero = i.serotype
			name.append('ac|%s sp|%s ge|%s' % (i.ac,sero.species.name,sero.name))
			seq.append(i.seq)
		return dict(name=name ,seq=seq)

class nt_f():
	"parse ref list to format that assigned"
	def __init__(self,model_l):
		self.model_l = model_l

	def to_profile(self):
		t_title = ['LOCUS','Species','GenBank Genotype','Re-classified Genotype(based on ICTV)','Host','Country','Description','Date','Gi','id']
		t_data = []
		for i in self.model_l:
			if i.date:
				i_date = i.date.date.strftime('%Y') if (i.date.date.day==1 and i.date.date.month==1) else i.date.date.strftime('%Y-%b-%d')
			else:
				i_date='unknown'
			t_data.append([i.version,i.ncbisero.ncbispec.name,i.ncbisero.name, '/'.join([i.ref.serotype.species.name,i.ref.serotype.full_name]),i.host.name, i.country.name ,i.des, i_date, i.version,i.id])

		return dict(colnames=t_title ,data=t_data)

	def to_blastform(self):
		t_key,t_value = [],[]
		for i in self.model_l:
			t_key.append(i.version)
			t_value.append(['/'.join([i.ref.serotype.species.name,i.ref.serotype.full_name]),i.des,i.version,i.country.name,i.id])

		return dict(loc_key=t_key ,loc_value=t_value)

	def to_fasta(self):
		name, seq = [],[]
		for i in self.model_l:
			sero = i.ref.serotype
			name.append('version|%s ac|%s sp|%s ge|%s' % (i.version,i.version,sero.species.name,sero.name))
			seq.append(i.seq)
		return dict(name=name ,seq=seq)

	def to_geno_dist(self,source):
		geno2c,geno2n,spec2geno,spec2n = {},{},{},{}
		spec_i2n,geno_i2n = [],[]
		for i in self.model_l:
			t_geno = i.ncbisero if source=='nt' else i.ref.serotype
			if t_geno.id not in geno2c:
				geno2c[t_geno.id]=0
				t_name = t_geno.name if source=='nt' else t_geno.full_name
				geno2n[t_geno.id] = t_name if t_name else 'unclassified'
				t_spec = t_geno.ncbispec if source=='nt' else t_geno.species
				if t_spec.id not in spec2geno:
					spec2n[t_spec.id] = t_spec.name
				spec2geno.setdefault(t_spec.id,[]).append(t_geno.id)
			geno2c[t_geno.id] += 1

		for i,j in sorted(spec2n.items(),key=lambda x:x[1]):
			t_c = sum([geno2c[x] for x in spec2geno[i]])
			spec_i2n.append([i,j,t_c])
			geno_i2n.append([[x,geno2n[x],geno2c[x]] for x in sorted(spec2geno[i],key=lambda x:geno2n[x])])
		return dict(spec_i2n=spec_i2n ,geno_i2n=geno_i2n)

class seg_f():
	"parse ref list to format that assigned"
	def __init__(self,model_l):
		self.model_l = model_l

	def to_fasta(self):
		name, seq = [],[]
		for i in self.model_l:
			name.append('ref|%s|serotype|%s|domain|%s' % (i.ref.ac,i.ref.serotype.name,i.region.name))
			seq.append(i.ref.seq[(i.start-1):i.end])
		return dict(name=name ,seq=seq)

class region_f():
	"parse ref list to format that assigned"
	def __init__(self,model_l):
		self.model_l = model_l

	def to_profile(self):
		t_title = ['id','Name', 'Average length','Max length','Min length', 'ref number']
		t_data = []
		for i in self.model_l:
			ref_c = len(i.segment)
			len_list = [x.end-x.start+1 for x in i.segment]
			t_data.append([i.id, i.name, sum(len_list)/ref_c, max(len_list), min(len_list), ref_c])

		return dict(colnames=t_title ,data=t_data)

class blast_f():
	def __init__(self,model_l):
		self.model_l = model_l

	def reg_scan(self,mode):
		json_loaded = json.load(open(path.join(config.static_dir,'json/gt_scan_json.json')))
		reg2ref2blast = dict([[x,{}] for x in json_loaded['reg_idname']])
		blast_colnames = ['Coverage(hsp)','Identity','Score','Alignment length','Region length','Identical length','Ref. Start','Ref. End','Query Start','Query End']
		len_ind = 3 if mode=='protein' else 2
		for i in self.model_l:
			t_seginfo = json_loaded['seg2info'][i.t_id]
			#t_conv = i.a_l*100/t_seginfo[2]
			reg2ref2blast[str(t_seginfo[0])].setdefault(t_seginfo[1] ,[i.qcovhsp,i.ident,int(i.score),i.a_l,t_seginfo[len_ind],(i.a_l-i.mismatch-int(i.gaps)),i.t_s,i.t_e,i.q_s,i.q_e])
		json_loaded.update({'blast_colnames':blast_colnames,'reg2ref2blast':reg2ref2blast,'mode':mode})
		del json_loaded['seg2info']

		return json_loaded
