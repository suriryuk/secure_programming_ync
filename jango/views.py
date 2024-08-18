from django.shortcuts import render
from django.http import HttpResponse
from django.db import connection

def index(request):
    if 'userid' in request.session:
        return render(request, 'unsecu/index.html', {'login': 'Logout'})
    else:
        return render(request, 'unsecu/index.html', {'login': 'Login'})

def login(request):
    return render(request, 'main/login.html')

def login_action(request):
    username = request.POST.get('username')
    password = request.POST.get('password')

    cursor = connection.cursor()
    cursor.execute(f'select * from unsecu_user where userid=%s and userpw=%s', [username, password])
    result = cursor.fetchall()
    print(result)

    if result:
        request.session['userid'] = username
        return HttpResponse('<script>alert("login success!"); location.href="/"; </script>')
    else:
        return HttpResponse('<script>alert("login failed!"); history.back(-1);</script>')

def logout(request):
    if 'userid' in request.session:
        request.session.flush()
        return HttpResponse('<script>alert("logout success!"); location.href="/"; </script>')
    else:
        return HttpResponse('<script>alert("login first!"); history.back(-1); </script>')
