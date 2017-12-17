import cherrypy
import json
import random
import string
import config
import cherrypy_cors
from pymongo import MongoClient

def CORS():
	cherrypy.response.headers["Access-Control-Allow-Origin"] = "*"

class QuickFinStatsAPI(object):
	def __init__(self):
		self.country_to_geo=json.load(open(config.country_to_geo_file))
		self.country_to_econ=json.load(open(config.country_to_econ_file))

		client=MongoClient(config.mongo_client, config.mongo_port)

		self.db=client[config.mongo_dbname]
		self.erp={}
		cursor=self.db.equity_risk_premium.find()
		for entry in cursor:
			self.erp[entry['_id']]=entry
		self.countries=self.erp.keys()

		self.currency_ids=self.db.currencies.distinct('_id',{'risk_free_rate':{'$exists':True}})
		self.countries_yield=self.db.bond_yields.distinct('_id')
		self.regions=self.db.diversified_betas.distinct('region')
		self.sectors=self.db.diversified_betas.distinct('sector')

	@cherrypy.expose
	def allSectors(self):
		return json.dumps(self.sectors)

	@cherrypy.expose
	def allCurrencies(self):
		return json.dumps(self.currency_ids)

	@cherrypy.expose
	def allCountriesToEcon(self):
		return json.dumps(self.country_to_econ)

	@cherrypy.expose
	def allCountriesYields(self):
		return json.dumps(self.countries_yield)

	@cherrypy.expose
	def allRegions(self):
		return json.dumps(self.regions)

	@cherrypy.expose
	def equityRiskPremiums(self, country='all'):
		if country=='all':
			data=[]
			cursor=self.db.equity_risk_premium.find()
			for entry in cursor:
				data.append(entry)
			return json.dumps(data)
		elif country in self.countries:
			data=[]
			cursor=self.db.equity_risk_premium.find({'_id': country})
			for entry in cursor:
				data.append(entry)
			return json.dumps(data)
		else:
			raise cherrypy.HTTPError(500, 'Bad Request: Wrong Country')


	@cherrypy.expose
	def bondYields(self, country='all'):
		if country=='all':
			data=[]
			cursor=self.db.bond_yields.find()
			for entry in cursor:
				data.append(entry)
			return json.dumps(data)
		elif country in self.countries_yield:
			data=[]
			cursor=self.db.bond_yields.find({'_id': country})
			for entry in cursor:
				data.append(entry)
			return json.dumps(data)
		else:
			raise cherrypy.HTTPError(500, 'Bad Request: Wrong Country')

	@cherrypy.expose
	def sp500(self):
		data=self.db.sp_500.find_one()
		return json.dumps(data)


	@cherrypy.expose
	def currencyRates(self, currency='all', country=''):
		if currency=='all':
			data=[]	
			if country in self.countries:
				cursor=self.db.currencies.find({'countries':{'$in':[country]}, 'risk_free_rate':{'$exists':True}})
				min_rate=1000
				for entry in cursor:
					if entry['risk_free_rate']<min_rate:
						min_rate=entry['risk_free_rate']
						entry['country']=country
						data=[entry]
				return json.dumps(data)

			elif country=='all':
				for country in self.countries:
					cursor=self.db.currencies.find({'countries':{'$in':[country]}, 'risk_free_rate':{'$exists':True}})
					min_rate=1000
					for entry in cursor:
						if entry['risk_free_rate']<min_rate:
							min_rate=entry['risk_free_rate']
							entry['country']=country
							del entry['countries']
							data.append(entry)
				return json.dumps(data)

			else:					
				cursor=self.db.currencies.find({'risk_free_rate':{'$exists':True}})
				for entry in cursor:
					data.append(entry)
				return json.dumps(data)

		elif currency in self.currency_ids:
			data=[]
			cursor=self.db.currencies.find({'$or':[{'_id': currency}, {'name': currency}]})
			for entry in cursor:
				data.append(entry)
			return json.dumps(data)
		else:
			raise cherrypy.HTTPError(500, 'Bad Request: Wrong Currency')

	@cherrypy.expose
	def riskByIndustryPublic(self, region='all', sector='all', country='all', byCountry='no'):
		data=[]
		if country!='all':
			try:
				region = self.country_to_econ[country]
			except KeyError:
				raise cherrypy.HTTPError(500, 'Bad Request: Wrong country')
		if region=='all':
			if sector=='all':
				cursor=self.db.diversified_betas.find()
				for entry in cursor:
					data.append(entry)
				return json.dumps(data)
			elif sector in self.sectors:
				cursor=self.db.diversified_betas.find({'sector':sector})
				for entry in cursor:
					if byCountry=='yes':
						for country_, region_ in self.country_to_econ.iteritems():
							if entry['region'] == region_:
								entry=entry.copy()
								entry['country']=country_
								data.append(entry)
					else:
						data.append(entry)
				return json.dumps(data)
			else:
				raise cherrypy.HTTPError(500, 'Bad Request: Wrong Sector')
		elif region in self.regions:
			if sector=='all':
				cursor=self.db.diversified_betas.find({'region':region})
				for entry in cursor:
					data.append(entry)
				return json.dumps(data)
			elif sector in self.sectors:
				cursor=self.db.diversified_betas.find({'region':region, 'sector':sector})
				for entry in cursor:
					if byCountry=='yes':
						for country_, region_ in self.country_to_econ.iteritems():
							if entry['region'] == region_:
								entry=entry.copy()
								entry['country']=country_
								data.append(entry)
					else:
						data.append(entry)
				return json.dumps(data)

			else:
				raise cherrypy.HTTPError(500, 'Bad Request: Wrong Sector')
		else:

			raise cherrypy.HTTPError(500, 'Bad Request: Wrong Region '+region)

	@cherrypy.expose
	def riskByIndustryPrivate(self, region='all', sector='all', country='all', byCountry='no'):
		data=[]
		if country!='all':
			try:
				region = self.country_to_econ[country]
			except KeyError:
				raise cherrypy.HTTPError(500, 'Bad Request: Wrong country')
		if region=='all':
			if sector=='all':
				cursor=self.db.undiversified_betas.find()
				for entry in cursor:
					data.append(entry)
				return json.dumps(data)
			elif sector in self.sectors:
				cursor=self.db.undiversified_betas.find({'sector':sector})
				for entry in cursor:
					if byCountry=='yes':
						for country_, region_ in self.country_to_econ.iteritems():
							if entry['region'] == region_:
								entry=entry.copy()
								entry['country']=country_
								data.append(entry)
					else:
						data.append(entry)
				return json.dumps(data)
			else:
				raise cherrypy.HTTPError(500, 'Bad Request: Wrong Sector')
		elif region in self.regions:
			if sector=='all':
				cursor=self.db.undiversified_betas.find({'region':region})
				for entry in cursor:
					data.append(entry)
				return json.dumps(data)
			elif sector in self.sectors:
				cursor=self.db.undiversified_betas.find({'region':region, 'sector':sector})
				for entry in cursor:
					if byCountry=='yes':
						for country_, region_ in self.country_to_econ.iteritems():
							if entry['region'] == region_:
								entry=entry.copy()
								entry['country']=country_
								data.append(entry)
					else:
						data.append(entry)
				return json.dumps(data)

			else:
				raise cherrypy.HTTPError(500, 'Bad Request: Wrong Sector')
		else:

			raise cherrypy.HTTPError(500, 'Bad Request: Wrong Region '+region)

def load_http_server():
	# extra server instance to dispatch HTTP
	server = cherrypy._cpserver.Server()
	server.socket_host = config.api_host
	server.socket_port = 80
	server.subscribe()

def force_tls():
	if cherrypy.request.scheme == "http":
		# see https://support.google.com/webmasters/answer/6073543?hl=en
		raise cherrypy.HTTPRedirect(cherrypy.url().replace("http:", "https:"),
									status=301)

cherrypy.tools.force_tls = cherrypy.Tool("before_handler", force_tls)
	
if __name__ == '__main__':
	cherrypy.tools.CORS = cherrypy.Tool('before_finalize', CORS)
	cherrypy.config.update({'server.socket_host':config.api_host,'server.socket_port': config.api_port})
	#Change this option if you want SSL and HTTP to HTTPS redirects
	if config.use_ssl:
		cherrypy.config.update({'tools.force_tls.on': True, 'server.ssl_module':'pyopenssl','server.ssl_certificate':config.ssl_certificate, 'server.ssl_private_key':config.private_key,})
		load_http_server()
	cherrypy.config.update({'environment' : 'production'})
	cherrypy.quickstart(QuickFinStatsAPI(), config={'/': {'tools.CORS.on': True}})

	