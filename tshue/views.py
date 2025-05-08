from django.shortcuts import render
from django.template import RequestContext

# Create your views here.
from django.http import HttpResponse, HttpResponseRedirect, FileResponse, StreamingHttpResponse
from django.urls import reverse

from .models import WikiData
from .forms import SearchForm, SearchTermForm, HanModForm, LmjModForm, UploadFileForm, SearchImikForm, OutModForm
import socket
import os
from django_ratelimit.decorators import ratelimit

def getClientIP(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
       ip = x_forwarded_for.split(',')[0]
    else:
       ip = request.META.get('REMOTE_ADDR')
    return ip

@ratelimit(key='user_or_ip', rate='100/h')
def index(request):
    form = SearchForm(request.POST or None)
    if form.is_valid():
        key = form.cleaned_data['key']
    else:
        key = ''

    hanmodform = HanModForm(request.POST or None)
    if hanmodform.is_valid():
        hanmod = hanmodform.cleaned_data['hanmod']
    else:
        hanmod = '0'

    lmjmodform = LmjModForm(request.POST or None)
    if lmjmodform.is_valid():
        lmjmod = lmjmodform.cleaned_data['lmjmod']
    else:
        lmjmod = '0'

    lines = []
    if key:
        import socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect(("localhost", 9999))
        # SETIP
        isStart = False
        isSent = False
        output = b""
        buf = ''
        while True:
            if not isStart:
                response = sock.recv(1024).decode()
                if response == "$ ":
                    isStart = True
                continue
            else:
                if not isSent:
                    string = "SETIP %s" % getClientIP(request)
                    sock.sendall(string.encode())
                    isSent = True
                else:
                    response = sock.recv(1024)
                    output += response
                    try:
                        if "DONE" in response.decode():
                            break
                    except:
                        pass
        for line in output.decode().split('\n'):
            if line.startswith('DONE'):
                buf = line[4:]
                break

        # TRANSLATE
        isStart = False
        isSent = False
        output = b""
        while True:
            if not isStart:
                if buf == '$ ':
                    buf = ''
                    isStart = True
                else:
                    response = sock.recv(1024).decode()
                    if response == "$ ":
                        isStart = True
                continue
            else:
                if not isSent:
                    string = "TRANSLATE%s%s0 %s" % (hanmod, lmjmod, key.replace('\r\n', '\n'))
                    sock.sendall(string.encode())
                    isSent = True
                else:
                    response = sock.recv(1024)
                    output += response
                    try:
                        if "DONE" in response.decode():
                            break
                    except:
                        pass
        for line in output.decode().split('\n'):
            if line.startswith('DONE'):
                break
            lines.append(line)
        sock.close()

    context = {
        'trans': {'lines': lines},
        'form': form,
        'hanmodform': hanmodform,
        'lmjmodform': lmjmodform,
    }
    return render(request, 'index.html', context)

def terms(request):
    form = SearchTermForm(request.POST or None)
    if form.is_valid():
        key = form.cleaned_data['key']
        form = SearchTermForm()
    else:
        key = ''

    if key:
        wd = WikiData.objects.filter(en__contains=key)[:20]
    else:
        wd = []

    context = {
        'wd': wd,
        'form': form
    }
    return render(request, 'terms.html', context)

def imik(request):
    form = SearchImikForm(request.POST or None)
    if form.is_valid():
        key = form.cleaned_data['key']
        form = SearchImikForm()
    else:
        key = ''

    lines = []
    if key:
        import socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect(("localhost", 10999))
        isStart = False
        isSent = False
        output = b""
        while True:
            if not isStart:
                response = sock.recv(1024).decode()
                if response == "$ ":
                    isStart = True
                continue
            else:
                if not isSent:
                    string = "TRANSLATE %s" % (key.replace('\r\n', '\n'))
                    sock.sendall(string.encode())
                    isSent = True
                else:
                    response = sock.recv(1024)
                    output += response
                    try:
                        if "DONE" in response.decode():
                            break
                    except:
                        pass
        for line in output.decode().split('\n'):
            if line.startswith('DONE'):
                break
            lines.append(line)
        sock.close()

    context = {
        'trans': {'lines': lines},
        'form': form,
    }
    return render(request, 'imik.html', context)

def isTimestamp(line):
    if "-->" not in line:
        return False
    if [c for c in line if c not in "0123456789:, -->"]:
        return False
    return True

def isSRT(filename):
    f = open(filename, encoding='utf8')
    isUtf8 = True
    try:
        f.read(2)
    except:
        isUtf8 = False
    f.close()

    if isUtf8:
        f = open(filename, encoding='utf8')
    else:
        f = open(filename, encoding='utf16')

    offset = 0
    buf2 = None
    buf = ''
    ret = True
    for i, line in enumerate(f):
        line = line.rstrip()
        if i == 0:
            pass
        elif i - offset > 25:    # limitation of single subtitle
            ret = False
            break
        elif len(line) > 100:    # limitation of single line
            ret = False
            break
        elif isTimestamp(line) and buf2 == '' and not [c for c in buf if c not in "0123456789"]:    # a new timestamp
            offset = i
        else:    # normal line
            pass

        buf2 = buf
        buf = line
    f.close()

    return ret

import datetime as dt

def getRendered(uid, sock, hanmod, lmjmod, outmod, filename, ip):
    fn = "/tmp/%s" % uid
    fn2 = "/tmp/%s.out" % uid
    f = open(fn, encoding='utf8')
    isUtf8 = True
    try:
        f.read(2)
    except:
        isUtf8 = False
    f.close()

    if isUtf8:
        f = open(fn, encoding='utf8')
    else:
        f = open(fn, encoding='utf16')
    ff = open(fn2, "w", encoding='utf8')

    tic = dt.datetime.now()
    buf = ''
    for line in f:
        line = line.replace('\r\n', '\n').rstrip()
        if not [c for c in line if c not in "0123456789 ->,:"]:
            print(line, file=ff)
            yield line.encode() + b'\r\n'
            continue

        isStart = False
        isSent = False
        output = b""
        while True:
            if not isStart:
                if buf == '$ ':
                    buf = ""
                    isStart = True
                else:
                    response = sock.recv(1024).decode()
                    if response == "$ ":
                        isStart = True
                continue
            else:
                if not isSent:
                    string = "TRANSRT%s%s%s %s" % (hanmod, lmjmod, outmod, line)
                    sock.sendall(string.encode())
                    isSent = True
                else:
                    response = sock.recv(1024)
                    output += response
                    try:
                        if "DONE" in response.decode():
                            break
                    except:
                        pass
        for li in output.decode().split('\n'):
            if li.startswith('DONE'):
                buf = li[4:]
                break
            print(li, file=ff)
            yield li.encode() + b'\r\n'
    ff.close()
    f.close()

    ff = open("/var/log/trans.log", "a")
    print("IP: %s" % ip, file=ff)
    print("Time start: %s" % tic, file=ff)
    print("Time end: %s" % dt.datetime.now(), file=ff)
    print("UID: %s" % uid, file=ff)
    print("Filename: %s" % filename, file=ff)
    print("Status: OK")
    print("", file=ff)
    ff.close()

    string = "QUIT"
    sock.sendall(string.encode())
    sock.close()

def subtitle(request):
    hanmodform = HanModForm(request.POST or None)
    if hanmodform.is_valid():
        hanmod = hanmodform.cleaned_data['hanmod']
    else:
        hanmod = '0'

    lmjmodform = LmjModForm(request.POST or None)
    if lmjmodform.is_valid():
        lmjmod = lmjmodform.cleaned_data['lmjmod']
    else:
        lmjmod = '0'

    outmodform = OutModForm(request.POST or None)
    if outmodform.is_valid():
        outmod = outmodform.cleaned_data['outmod']
    else:
        outmod = '0'

    if request.method == "POST":
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            import uuid
            import random
            uid = "%s" % uuid.uuid4()

            import socket
            import urllib.parse
            the_file = request.FILES["file"]
            with open("/tmp/%s" % uid, "wb+") as f:
                for chunk in the_file.chunks():
                    f.write(chunk)

            ip = getClientIP(request)
            try:
                ret = isSRT("/tmp/%s" % uid)
            except:
                ret = False
            if ret:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
                sock.connect(("localhost", 9999+random.randint(1,4)))
                response = StreamingHttpResponse(getRendered(uid, sock, hanmod, lmjmod, outmod, the_file.name, ip))
                response['Content-Disposition'] = "attachment; filename*=UTF-8''%s" % urllib.parse.quote(the_file.name)
                return response
            else:
                ff = open("/var/log/trans.log", "a")
                print("IP: %s" % ip, file=ff)
                print("Time start: %s" % tic, file=ff)
                print("Time end: %s" % dt.datetime.now(), file=ff)
                print("UID: %s" % uid, file=ff)
                print("Filename: %s" % the_file.name, file=ff)
                print("Status: ERROR", file=ff)
                print("", file=ff)
                ff.close()
                return HttpResponse('檔案格式錯誤！')
        return HttpResponse('錯誤！')

    else:
        form = UploadFileForm()

    context = {
        'form': form,
        'hanmodform': hanmodform,
        'lmjmodform': lmjmodform,
        'outmodform': outmodform,
    }
    return render(request, "subtitle.html", context)
