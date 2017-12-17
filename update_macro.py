import requests
import json
import ast
import math
from pymongo import MongoClient
from sympy.solvers import solve
from sympy import Symbol

import config
import parameters

def update_bond_yields(text, db):

	start = text.find('(function($) {')
	end = text.find('// Initiate the chart')
	end=end-11
	start+=31

	text=text[start:end]

	lines=[]
	for line in text.split('\n'):
		desc=line[4:6]
		if desc=='de' or desc=='co' or desc=='fl':
			continue
		else:
			lines.append(line)

	text='\n'.join(lines)
	text=text.replace('value', 'yield').replace('name','_id').replace('\n','')

	data=ast.literal_eval(text)

	for document in data:
		document['yield']=document['yield']/100
		db.bond_yields.replace_one({'_id':document['_id']},document,upsert=True)

def update_risk_free_rates(db):

	currencies=db.currencies.find()
	for currency in currencies:
		min_rate=-100
		countries=currency['countries']

		for country in countries:
			cursor=db.bond_yields.find({'_id': country})
			rate=-100
			for val in cursor:
				rate=val['yield']
				cursor=db.equity_risk_premium.find({'_id': country})
				for val in cursor:
					rate-=val['default_spread']

				if rate>min_rate:
					min_rate=rate

		if min_rate!=-100:
			currency['risk_free_rate']=min_rate
			db.currencies.replace_one({'_id':currency['_id']},currency,upsert=True)

def update_sp500_erp(sp500, db):

	document={}
	document['price']=sp500
	r = Symbol('r', real=True)
	payout_delta=(parameters.sp500_payout-parameters.sp500_target_payout)/6
	payout=parameters.sp500_payout
	document['payout']=payout
	earnings=parameters.sp500_earnings
	document['earnings']=earnings
	document['growth']=parameters.sp500_growth_estimate

	rf_usd=db.currencies.find({'_id':'USD'})[0]['risk_free_rate']

	fcf=[]
	for i in range(1,7):
		payout-=payout_delta
		earnings=earnings*(1+parameters.sp500_growth_estimate)
		fcf.append(earnings*payout)
	spy=fcf[0]/(1+r)+fcf[1]/((1+r)**2)+fcf[2]/((1+r)**3)+fcf[3]/((1+r)**4)+fcf[4]/((1+r)**5)+fcf[5]/((r-rf_usd)*((1+r)**5))
	erp_list=solve(spy-sp500,r)
	
	for erp_candidate in erp_list:
		if erp_candidate>0:
			erp=float('{0:.5f}'.format(erp_candidate-rf_usd))
			document['equity_risk_premium']=erp
			db.sp_500.replace_one({'_id':'sp500'},document,upsert=True)

def update_erps(db):

	erp=db.sp_500.find_one()['equity_risk_premium']
	cursor=db.equity_risk_premium.find()
	for document in cursor:
		document['equity_risk_premium']=erp+document['country_risk_premium']
		db.equity_risk_premium.replace_one({'_id':document['_id']},document,upsert=True)

def get_sp500(api_key):
	try:
		response=requests.get(config.stock_price_url, params={'function':'TIME_SERIES_DAILY', 'apikey':api_key, 'symbol':'SPY'}).json()	
		price=sorted(response['Time Series (Daily)'].items())[-1][1]['4. close']
		return float(price)*10

	except ValueError:
		print('Decoding JSON has failed. Check your request parameters.')	
		quit()

def main():

	#Load API key and create default_params dictionary
	api_key=open(config.api_key_file,'r').readlines()[0]
	default_params={'api_key':api_key}

	client=MongoClient(config.mongo_client, config.mongo_port)
	db=client[config.mongo_dbname]

	#Update yields
	print('Updating bond yields...')
	r = requests.get(config.gov_yields_url)
	text = r.text
	update_bond_yields(text, db)

	#Update risk-free rates
	print('Updating risk-free rates...')
	update_risk_free_rates(db)

	#Update SP500 and implied Equity Risk Premium
	print('Updating SP500...')
	sp500=get_sp500(api_key)
	update_sp500_erp(sp500, db)

	print('Updating Risk Premia...')
	#Update Equity Risk Premia
	update_erps(db)
	print('Done')


if __name__ == '__main__':
	
	main()