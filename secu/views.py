from django.shortcuts import render
from django.db import connection
from django.http import HttpResponse
from typing import List, Dict
from lxml import etree

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
        return render(request, 'secu/index.html', {'login': 'Logout'})
    else:
        return render(request, 'secu/index.html', {'login': 'Login'})

def sqli(request):
    return render(request, 'secu/sqli.html')

def sqli_action(request):
    username = request.POST.get('username')
    password = request.POST.get('password')

    cursor = connection.cursor()
    cursor.execute(f'select * from unsecu_user where userid=%s and userpw=%s', [username, password])

    result: List[Dict] = fetchall(cursor)

    if result:
        loginState = 'success'
    else:
        loginState = 'fail'

    return render(request, 'secu/sqli_action.html', {'message': loginState})

def xss_action(request):
    if request.method == 'GET':
        payload = request.GET.get('payload')
        try:
            cursor = connection.cursor()
            cursor.execute('SELECT content FROM unsecu_content WHERE content LIKE %s', ['%' + payload + '%'])
            results = [row[0] for row in cursor.fetchall()]

            return render(request, 'secu/xss_action.html', {'payload': payload, 'results': results})
        except Exception as e:
            return HttpResponse(f'Error Renderring: {e}', status=400)
    else:
        return render(request, 'secu/xss_action.html', {'payload': None})

def xxe(request):
    return render(request, 'secu/xxe.html')

def xxe_action(request):
    if request.method == 'POST':
        xml_data = request.POST.get('xml_data')
        parser = etree.XMLParser(resolve_entities=False)
        try:
            root = etree.fromstring(xml_data, parser=parser)
            name = root.find('name').text
            school = root.find('school').text
            return render(
                request,
                'secu/xxe_action.html',
                {'name': name, 'school': school}
            )
        except Exception as e:
            return HttpResponse(f"Error Parsing XML: {e}", status=400)
    else:
        return HttpResponse('Only POST requests are allowed.', status=405)

