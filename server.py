from flask import Flask, request, jsonify, render_template
#from flask.ext.jsonpify import jsonify
from selenium import webdriver
from selenium.webdriver.firefox.options import Options

import pprint
app = Flask(__name__)
driver = None


def saf_marine_crawler(code):
	options = Options()
	options.headless = True
	driver=webdriver.Firefox(options=options)
	data={"summary":None,"details":[]}
	details=[]#[[title,[time,detail],...]
	url="https://www.safmarine.com/how-to-ship/tracking?trackingNumber="
	driver.get(url+code)
	print driver.title
	try:
		driver.find_element_by_css_selector("#ign-accept-cookie").click()
	except:
		pass
	summary=driver.find_elements_by_css_selector("tr.bg--saf-orange td")[3].text
	#show details
	driver.find_element_by_css_selector("a span.tracking__results__table__row__more-details__link__span").click()
	details_rows=driver.find_elements_by_css_selector(".tracking__results__table__row--details li")
	for row in details_rows:
		#point to port
		fields=[]
		port=row.find_elements_by_css_selector("div")
		fields.append(port[0].text)
		for field in port[1:]:
			#go trough port rows
			tmp=[]
			for span in field.find_elements_by_css_selector("span")[1:]:
				tmp.append(span.text)
			fields.append(tmp)
		details.append(fields)
	data['summary']=summary
	data['details']=details
	driver.quit()
	return data


def createpage(data):
	mid="<section>\n"
	for rows in data['details']:
		mid=mid+"<ul class='collection with-header'>"
		mid=mid+"<li class='collection-header'><h4>"+rows[0]+"</h4></li>\n"
		for row in rows[1:]:
			mid=mid+"<li class='collection-item'><div>"+row[1]+"<span class='secondary-content'> "+row[0]+"</span></div></li>\n"
		mid=mid+"</ul>"
	mid=mid+"</section"

	return mid


@app.route('/search')
def index():
	code=request.args.get("code")
	data={'details': [['Unknown location,',
              ['25 Mar 2019 15:25', 'Gate out, empty']],
             ['GZ Oceangate Container Terminal, Nansha New Port, Guangdong, China',
              ['26 Mar 2019 05:16', 'Gate in'],
              ['01 Apr 2019 04:29',
               'Load on MAERSK SEOUL Voyage No.: 911W']],
             ['Pointe Noire Terminal /Terminal/Con, Pointe Noire, Congo',
              ['03 May 2019 10:38', 'Discharge'],
              ['06 May 2019 14:02',
               'Load on CMA CGM PLATON Voyage No.: 1915']],
             ['Douala Terminal, Douala, Cameroon',
              ['11 May 2019 14:31', 'Discharge']]],
 'summary': 'Discharge, 23 days ago at Douala, CM'}
 	try:
 		data=saf_marine_crawler(code)
 		mid=createpage(data)
 		summary=data['summary']
 	except Exception as e:
 		print e
 		mid="<h4>Cargo Container Not Found</h4>"
	return render_template("search.html",**locals())






if __name__ == "__main__":
	app.run(host= '0.0.0.0')

