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
	print(driver.title)
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


	data={"summary":"Discharge, 23 days ago at Douala, CM",
   "details":[
      {
         "port":"cameroun",
         "transactions":[
            {
               "date":"25 Mar 2019 15:25",
               "action":"discharge of container"
            },
            {
               "date":"25 Mar 2019 17:25",
               "action":"gate in"
            }
         ]
      },
      {
         "port":"Pointe Noire Terminal /Terminal/Con, Pointe Noire",
         "transactions":[
            {
               "date":"28 Mar 2019 15:25",
               "action":"transportation"
            },
            {
               "date":"29 Mar 2019 17:25",
               "action":"Load on CMA CGM PLATON Voyage No.: 1915"
            }
         ]
      }
   ]
}

	try:
		mid=createpage(data)
		summary=data['summary']
	except Exception:
		print(Exception)
		mid="<h4>Cargo Container Not Found</h4>"
		return jsonify(data) #render_template("search.html",**locals())

@app.route('/get_slides')
def send_slides():
	slides=['/static/img/mountains.jpg','/static/img/monkey.jpg','/static/img/front.jpg']  #data=saf_marine_crawler(code)
	return jsonify(slides)

@app.route('/get_news')
def send_news():
	news=[
{
	"title":"new port open in cameroun",
	"description":"the new port in cameroun can support many ships and can load and unload at the same time, it really is a change to the country's economy"	
},
{
	"title":"a discount for big shipments",
	"description":"all large shipments (greater than 50KG) will have a 10% discount"
}
]
	
	return jsonify(news)



if __name__ == "__main__":
	app.run(host= '0.0.0.0')

