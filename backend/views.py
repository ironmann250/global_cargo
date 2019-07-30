# -*- coding: utf-8 -*-
from django.shortcuts import render, get_object_or_404
from backend.models import *
from django.http import HttpResponse,JsonResponse,HttpResponseRedirect
import requests,json
from django.contrib.auth.decorators import login_required
from django.utils.timezone import now

# Create your views here.
def postprocess(request,fields,exc=['',None]):
	'''
	process post variables and return a list
	'''
	data=[]
	for f in fields:
		if request.POST[f].strip() not in exc:
			data.append(request.POST[f])
		else:
			return None
	return data

def getprocess(request,fields,exc=['',None]):
	'''
	process post variables and return a list
	'''
	data=[]
	for f in fields:
		if request.GET[f].strip() not in exc:
			data.append(request.GET[f])
		else:
			return None
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

def processcode(code='msku0377509',operator='maeu'):
	data={}
	summary=[]
	ports=[]
	url="https://api.maerskline.com/track/"+code+"?operator="+operator
	jdata=json.loads(requests.get(url).text)
	summary.append(','.join([jdata['origin']['country'],jdata['origin']['city'],jdata['origin']['terminal']]))
	summary.append(','.join([jdata['destination']['country'],jdata['destination']['city'],jdata['destination']['terminal']]))
	summary.append(' on '.join(jdata['containers'][0]['eta_final_delivery'].split('T')))
	summary.append(jdata['containers'][0]['status'])
	data['summary']=summary
	for i in jdata['containers'][0]['locations']:
		p=[]                                                                                      
		p.append(','.join([i['country'],i['city'],i['terminal']]))                                                                   
		for e in i['events']:                                                                     
			p.append([' on '.join(e['expected_time'].split('T')),e['activity']+" "+e['vessel_name']])                        
		ports.append(p)  
	data['details']=ports
	return data

def search(request):
	code=getprocess(request,['code'])[0]
	data=[]

	try:
		search_data=SEARCH.objects.get(code=code)
		data=json.loads(search_data.data)
		mid=createpage(data)
		summary=data['summary']
		return render(request,'search.html',locals())
	except Exception as e:
		print e
		pass

	try:
		data=processcode(code,'maeu')
		if SEARCH.objects.filter(code=code).count()==0:
			new_data=SEARCH(code=code,data=json.dumps(data))
			new_data.save()
	except:
		pass
	try:
		data=processcode(code,'safm')
		if SEARCH.objects.filter(code=code).count()==0:
			new_data=SEARCH(code=code,data=json.dumps(data))
			new_data.save()
	except:
		pass

	if data:
		mid=createpage(data)
		summary=data['summary']
	else:
		mid="<h4> Cargo Container Not Found </h4>"
		summary=['Unknown Cargo']
	return render(request,'search.html',locals())
