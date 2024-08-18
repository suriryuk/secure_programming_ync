from django.shortcuts import render
from django.db import connection
from django.http import HttpResponse
from django.template import engines
from django.views.decorators.csrf import csrf_exempt
from typing import List, Dict
from xml.sax import make_parser
from xml.sax.handler import feature_external_ges, ContentHandler
from xml.dom.pulldom import parseString, START_ELEMENT
import xml.etree.ElementTree as ET
from lxml import etree

class MyHandler(ContentHandler):
    def __init__(self):
        self.buffer = ""
        self.data = {}

    def startElement(self, name, attrs):
        self.buffer = ""

    def endElement(self, name):
        self.data[name] = self.buffer.strip()

    def characters(self, content):
        self.buffer += content

def fetchall(cursor) -> List[Dict]:
    desc = cursor.description
    ret: List[Dict] = []
    columns = [info[0] for info in desc]

    for data in cursor.fetchall():
        row = {}
        for i, column in enumerate(columns):
            row[column] = data[i]
        ret.append(row)

    return ret

# Create your views here.
def index(request):
    if 'userid' in request.session:
        return render(request, 'unsecu/index.html', {'login': 'Logout'})
    else:
        return render(request, 'unsecu/index.html', {'login': 'Login'})

def login(request):
    pass

def sqli(request):
    return render(request, 'unsecu/sqli.html')

def sqli_action(request):
    username = request.POST.get('username')
    password = request.POST.get('password')

    cursor = connection.cursor()
    cursor.execute(f'select * from unsecu_user where userid="{username}" and userpw="{password}"')

    result: List[Dict] = fetchall(cursor)

    if result:
        loginState = 'success'
    else:
        loginState = 'fail'

    return render(request, 'unsecu/sqli_action.html', {'message': loginState})

def xxe(request):
    return render(request, 'unsecu/xxe.html')

def xxe_action(request):
    if request.method == 'POST':
        xml_data = request.POST.get('xml_data')
        parser = etree.XMLParser(resolve_entities=True)
        try:
            root = etree.fromstring(xml_data, parser=parser)
            name = root.find('name').text
            school = root.find('school').text
            return render(
                request,
                'unsecu/xxe_action.html',
                {'name': name, 'school': school}
            )
        except Exception as e:
            return HttpResponse(f"Error Parsing XML: {e}", status=400)
    else:
        return HttpResponse('Only POST requests are allowed.', status=405)

def xss_action(request):
    if request.method == 'GET':
        payload = request.GET.get('payload')
        try:
            cursor = connection.cursor()
            cursor.execute('SELECT content FROM unsecu_content WHERE content LIKE %s', ['%' + payload + '%'])
            results = [row[0] for row in cursor.fetchall()]

            return render(request, 'unsecu/xss_action.html', {'payload': payload, 'results': results})
        except Exception as e:
            return HttpResponse(f'Error Renderring: {e}', status=400)
    else:
        return render(request, 'unsecu/xss_action.html', {'payload': None})
