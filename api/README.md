quickfinstats-api
=================

Original blog post: [My personal site](https://www.javierandres.me/importing-and-visualizing-financial-data/).
Available at https://api.quickfinstats.com

## Equity Risk Premiums:
```bash
curl -k 'https://api.quickfinstats.com/equityRiskPremiums?country=United%20States'

[{"rating": "Aaa", "country_risk_premium": 0.0, "default_spread": 0.0038, "region": "North America", "currency_id": "USD", "currency": "US Dollar", "marginal_tax": 0.4, "equity_risk_premium": 0.04323, "_id": "United States"}]
```
## Risk-free rates:
```bash
curl -k 'https://api.quickfinstats.com/currencyRates?currency=EUR'

[{"risk_free_rate": 0.002199999999999999, "_id": "EUR", "name": "Euro", "countries": ["Andorra (Principality of)", "Austria", "Belgium", "Cyprus", "Estonia", "Finland", "France", "Germany", "Greece", "Ireland", "Italy", "Latvia", "Lithuania", "Luxembourg", "Malta", "Montenegro", "Netherlands", "Portugal", "Slovakia", "Slovenia", "Spain"]}]
```
```bash
curl -k 'https://api.quickfinstats.com/currencyRates?country=Morocco'

[{"country": "Morocco", "risk_free_rate": 0.011200000000000002, "_id": "MAD", "name": "Moroccan Dirham", "countries": ["Morocco"]}]
```
## Bond yields:
```bash
curl -k 'https://api.quickfinstats.com/bondYields?country=Spain'

[{"_id": "Spain", "yield": 0.0147}]
```
## Relative risk measures:
```bash
curl -k 'https://api.quickfinstats.com/riskByIndustryPublic?region=eur&sector=Education'

[{"sector": "Education", "cash_firm": 0.03344990590594695, "market_beta": 0.128232026, "unlevered_beta_cash_corrected": 0.06037200868271735, "region": "eur", "sigma_price": 0.682532357, "tax_rate": 0.075386103, "sigma_ebit": 0.550127568, "debt_equity": 1.2951769338004155, "_id": "eurEducation", "unlevered_beta": 0.05835257067292744}]
```
```bash
curl -k 'https://api.quickfinstats.com/riskByIndustryPrivate?country=Canada&sector=Real%20Estate%20(Development)'

[{"sector": "Real Estate (Development)", "unlevered_beta_partial": 0.469273293568202, "market_correlation": 0.214444136, "levered_beta": 3.1908923450347926, "region": "us", "levered_beta_partial": 0.684268152, "_id": "usReal Estate (Development)", "unlevered_beta": 2.1883242056486076}]
```

## Some additional endpoints so we can know the valid parameters for all requests:


`/allSectors`

`/allCurrencies`

`/allCountriesToEcon`

`/allCountriesYields`

`/allRegions`



License
=======

**This software is released under the [MIT License](http://opensource.org/licenses/MIT).**

  The MIT License (MIT)

  Copyright (c) Javier Andrés

  Permission is hereby granted, free of charge, to any person obtaining a copy
  of this software and associated documentation files (the "Software"), to deal
  in the Software without restriction, including without limitation the rights
  to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
  copies of the Software, and to permit persons to whom the Software is
  furnished to do so, subject to the following conditions:

  The above copyright notice and this permission notice shall be included in all
  copies or substantial portions of the Software.

  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
  IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
  FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
  AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
  LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
  OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
  SOFTWARE.