import sys
import csv
import xlrd
from pymongo import MongoClient
from os import listdir
from os.path import isfile, join

import config

def populate_currencies(db):

	sheet = xlrd.open_workbook(config.currency_file).sheet_by_index(0)
	currency={}
	currency['countries']=[sheet.cell(4,0).value]
	currency['name']=sheet.cell(4,1).value
	currency['_id']=sheet.cell(4,2).value
	currency_code=currency['_id']

	for i in range(5,300):
		try:
			if currency_code!=sheet.cell(i,2).value:
				db.currencies.replace_one({'_id':currency['_id']},currency,upsert=True)
				currency['countries']=[sheet.cell(i,0).value]
				currency['name']=sheet.cell(i,1).value
				currency['_id']=sheet.cell(i,2).value
				currency_code=currency['_id']
			else:
				currency['countries'].append(sheet.cell(i,0).value)

		except IndexError:
			db.currencies.replace_one({'_id':currency['_id']},currency,upsert=True)
			break

def populate_tax_rates(db):

	tax_files=[f for f in listdir(config.effective_tax_path) if isfile(join(config.effective_tax_path, f))]

	for file in tax_files:
		region=file.split('_')[1].replace('.xls','')
		document={}
		document['_id']=region
		document['rates_by_sector']={}
		sheet = xlrd.open_workbook(config.effective_tax_path + file).sheet_by_index(0)
		for i in range(8, 200):
			try:
				sector=sheet.cell(i,0).value.replace('.','')
				document['rates_by_sector'][sector]={}
				document['rates_by_sector'][sector]['money_making']=sheet.cell(i,2).value
				document['rates_by_sector'][sector]['money_losing']=sheet.cell(i,3).value
				document['rates_by_sector'][sector]['all']=sheet.cell(i,4).value
			except IndexError:
				break

		db.effective_tax.replace_one({'_id':region},document,upsert=True)

def populate_diversified_betas(db):

	beta_files=[f for f in listdir(config.diversified_betas_path) if isfile(join(config.diversified_betas_path, f))]

	for file in beta_files:
		region=file.split('_')[1].replace('.xls','')
		sheet = xlrd.open_workbook(config.diversified_betas_path + file).sheet_by_index(0)
		for i in range(8, 200):
			try:
				sector=sheet.cell(i,0).value.replace('.','')
				document={}
				document['_id']=region+sector
				document['region']=region
				document['sector']=sector				
				document['market_beta']=sheet.cell(i,2).value
				document['debt_equity']=sheet.cell(i,3).value
				document['tax_rate']=sheet.cell(i,4).value
				document['unlevered_beta']=sheet.cell(i,5).value
				document['cash_firm']=sheet.cell(i,6).value
				document['unlevered_beta_cash_corrected']=sheet.cell(i,7).value
				document['sigma_price']=sheet.cell(i,8).value
				document['sigma_ebit']=sheet.cell(i,9).value

				db.diversified_betas.replace_one({'_id':document['_id']},document,upsert=True)
	
			except IndexError:
				break		

def populate_undiversified_betas(db):

	beta_files=[f for f in listdir(config.undiversified_betas_path) if isfile(join(config.undiversified_betas_path, f))]
	
	for file in beta_files:
		region=file.split('_')[1].replace('.xls','')
		sheet = xlrd.open_workbook(config.undiversified_betas_path + file).sheet_by_index(0)
		for i in range(8, 200):
			try:
				sector=sheet.cell(i,0).value.replace('.','')
				document={}
				document['_id']=region+sector
				document['region']=region
				document['sector']=sector	
				document['unlevered_beta_partial']=sheet.cell(i,2).value
				document['levered_beta_partial']=sheet.cell(i,3).value
				document['market_correlation']=sheet.cell(i,4).value
				document['unlevered_beta']=sheet.cell(i,5).value
				document['levered_beta']=sheet.cell(i,6).value

				db.undiversified_betas.replace_one({'_id':document['_id']},document,upsert=True)				
	
			except IndexError:
				break


def populate_erps(db):

	sheet = xlrd.open_workbook(config.erp_file).sheet_by_index(5)
	us_spread=0.0038
	for i in range(1, 156):
		#try:
		document = {}
		country=sheet.cell(i,0).value
		document['rating']=sheet.cell(i,2).value
		document['default_spread']=sheet.cell(i,3).value
		document['default_spread']=float(document['default_spread'])+us_spread
		document['country_risk_premium']=sheet.cell(i,5).value
		document['equity_risk_premium']=sheet.cell(i,4).value
		document['marginal_tax']=sheet.cell(i,6).value

		#Get currency
		cursor=db.currencies.find({'countries': country})
		for entry in cursor:
			document['currency']=entry['name']
			document['currency_id']=entry['_id']

		db.equity_risk_premium.replace_one({'_id':country},document,upsert=True)

	sheet = xlrd.open_workbook(config.erp_file).sheet_by_index(2)
	for i in range(7, 153):
		country=sheet.cell(i,0).value
		document=db.equity_risk_premium.find({'_id': country})[0]
		document['region']=sheet.cell(i,1).value
		default_spread=sheet.cell(i,6).value
		if str(default_spread)!='NA':
			document['default_spread']=default_spread+us_spread
			document['country_risk_premium']=sheet.cell(i,8).value
			document['equity_risk_premium']=sheet.cell(i,7).value
		db.equity_risk_premium.replace_one({'_id':document['_id']},document,upsert=True)

def populate_ratings_spreads(db):

	#Ratings and spreads
	sheet = xlrd.open_workbook(config.ratings_file).sheet_by_index(0)
	document={}
	document['_id']='large'
	document['spreads']=[]
	for i in range(18, 33):
		spread={}
		ratings=sheet.cell(i,2).value
		ratings=ratings.split('/')
		spread['rating_moodys']=ratings[0]
		spread['rating_sp']=ratings[1]
		spread['coverage_ratio_lower']=sheet.cell(i,0).value
		spread['coverage_ratio_higher']=sheet.cell(i,1).value
		spread['spread']=sheet.cell(i,3).value
		document['spreads'].append(spread)
	db.ratings_spreads.replace_one({'_id': document['_id']}, document, upsert=True)

	document['_id']='financial'
	document['spreads']=[]
	for i in range(18, 33):
		spread={}
		ratings=sheet.cell(i,7).value
		ratings=ratings.split('/')
		spread['rating_moodys']=ratings[0]
		spread['rating_sp']=ratings[1]
		spread['coverage_ratio_lower']=sheet.cell(i,7).value
		spread['coverage_ratio_higher']=sheet.cell(i,6).value
		spread['spread']=sheet.cell(i,8).value
		document['spreads'].append(spread)
	db.ratings_spreads.replace_one({'_id': document['_id']}, document, upsert=True)

	document['_id']='small'
	document['spreads']=[]
	for i in range(37, 52):
		spread={}
		ratings=sheet.cell(i,2).value
		ratings=ratings.split('/')
		spread['rating_moodys']=ratings[0]
		spread['rating_sp']=ratings[1]
		spread['coverage_ratio_lower']=sheet.cell(i,0).value
		spread['coverage_ratio_higher']=sheet.cell(i,1).value
		spread['spread']=sheet.cell(i,3).value
		document['spreads'].append(spread)
	db.ratings_spreads.replace_one({'_id': document['_id']}, document, upsert=True)

def main():

	client=MongoClient(config.mongo_client, config.mongo_port)
	db=client[config.mongo_dbname]

	#Start with macroeconomic data
	#Currencies
	populate_currencies(db)

	#Effective Tax Rates

	populate_tax_rates(db)

	#Diversified Betas

	populate_diversified_betas(db)

	#Undiversified Betas
	populate_undiversified_betas(db)

	#Equity Risk Premiums
	populate_erps(db)

	#Populating ratings and spreads
	populate_ratings_spreads(db)

		
if __name__ == '__main__':

	main()