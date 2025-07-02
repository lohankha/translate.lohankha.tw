import json
import os
import socket

import requests
from django.http import (FileResponse, HttpResponse, HttpResponseRedirect,
                         JsonResponse, StreamingHttpResponse)
from django.shortcuts import render
from django.template import RequestContext
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from .forms import (InputModForm, OutputModForm, SearchForm, SearchImikForm,
                    SearchTermForm, TranslationAPIHelper, UploadFileForm)
from .models import WikiData


@csrf_exempt
@require_http_methods(["POST"])
def translation_proxy(request):
    """
    Proxy endpoint for translation API to handle CORS issues
    """
    try:
        # Get form data from request
        input_lang = request.POST.get('input_lang')
        output_format = request.POST.get('output_format') 
        input_text = request.POST.get('key')  # Frontend sends 'key' parameter
        
        print(f"DEBUG: Received parameters:")
        print(f"  input_lang: {input_lang}")
        print(f"  output_format: {output_format}")
        print(f"  input_text: {input_text}")
        
        if not all([input_lang, output_format, input_text]):
            missing = []
            if not input_lang: missing.append('input_lang')
            if not output_format: missing.append('output_format')
            if not input_text: missing.append('input_text')
            
            return JsonResponse({
                'success': False,
                'error': f'Missing required parameters: {", ".join(missing)}'
            }, status=400)
        
        # Generate API parameters using helper
        api_params = TranslationAPIHelper.get_api_params(input_lang, output_format, input_text)
        
        print(f"DEBUG: Generated API parameters: {api_params}")
        
        # Make request to translation API
        api_url = 'http://lohankha.tw:10999'
        response = requests.post(
            api_url,
            data=api_params,
            headers={'Content-Type': 'application/x-www-form-urlencoded'},
            timeout=30
        )
        
        print(f"DEBUG: API response status: {response.status_code}")
        print(f"DEBUG: API response content: {response.text[:200]}...")
        
        if response.status_code == 200:
            # Parse the API response
            try:
                result_data = response.json()
                return JsonResponse({
                    'success': True,
                    'result': result_data
                })
            except json.JSONDecodeError:
                return JsonResponse({
                    'success': False,
                    'error': 'Invalid JSON response from translation API'
                }, status=500)
        else:
            return JsonResponse({
                'success': False,
                'error': f'API request failed with status {response.status_code}',
                'details': response.text[:200]
            }, status=response.status_code)
            
    except requests.RequestException as e:
        print(f"DEBUG: Network error: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': f'Network error: {str(e)}'
        }, status=500)
    except Exception as e:
        print(f"DEBUG: Server error: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': f'Server error: {str(e)}'
        }, status=500)
            
    except requests.RequestException as e:
        return JsonResponse({
            'status': 'error',
            'message': f'Network error: {str(e)}'
        }, status=500)
    except Exception as e:
        return JsonResponse({
            'status': 'error', 
            'message': f'Server error: {str(e)}'
        }, status=500)

def getClientIP(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
       ip = x_forwarded_for.split(',')[0]
    else:
       ip = request.META.get('REMOTE_ADDR')
    return ip

def index(request):
    form = SearchForm(request.POST or None)
    if form.is_valid():
        key = form.cleaned_data['key']
    else:
        key = ''

    input_lang_form = InputModForm(request.POST or None)
    if input_lang_form.is_valid():
        input_lang = input_lang_form.cleaned_data['input_lang']
    else:
        input_lang = 'zh-tw' # defult

    output_format_form = OutputModForm(input_lang=input_lang, data=request.POST or None)
    if output_format_form.is_valid():
        output_format = output_format_form.cleaned_data['output_format']
    else:
        # default output format based on input language
        output_options = TranslationAPIHelper.get_output_options(input_lang)
        output_format = output_options[0][0] if output_options else 'tai-han'

    lines = []
    api_params = {}
    
    if key and input_lang and output_format:
        # generate API parameters based on input language and output format
        api_params = TranslationAPIHelper.get_api_params(input_lang, output_format, key)
        
        # TODO: use new API parameters format
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
                    # TODO: use new API parameters format
                    cmd = api_params.get('cmd', 'H2T')
                    lang = api_params.get('lang', '')
                    hanjimod = api_params.get('hanjimod', 1)
                    outmod = api_params.get('outmod', 1)
                    
                    # old format handling
                    if cmd == 'H2T':
                        hanmod = '1' if input_lang == 'zh-tw' else '0'
                    elif cmd == 'G2T':
                        hanmod = lang
                    else:
                        hanmod = '0'
                    
                    lmjmod = '0' if output_format == 'tai-han' else '1'
                    
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
        'input_lang_form': input_lang_form,
        'output_format_form': output_format_form,
        'api_params': api_params, # debug
        'input_lang': input_lang,
        'output_format': output_format,
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
    input_lang_form = InputModForm(request.POST or None)
    if input_lang_form.is_valid():
        input_lang = input_lang_form.cleaned_data['input_lang']
    else:
        input_lang = 'zh-tw'

    output_format_form = OutputModForm(input_lang=input_lang, data=request.POST or None)
    if output_format_form.is_valid():
        output_format = output_format_form.cleaned_data['output_format']
    else:
        output_options = TranslationAPIHelper.get_output_options(input_lang)
        output_format = output_options[0][0] if output_options else 'tai-han'

    outmodform = OutputModForm(request.POST or None)
    if outmodform.is_valid():
        outmod = outmodform.cleaned_data['output_format']
    else:
        outmod = '0'

    if request.method == "POST":
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            import random
            import uuid
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
                # generate API parameters based on input language and output format
                api_params = TranslationAPIHelper.get_api_params(input_lang, output_format, "dummy")
                # convert to old format
                if api_params.get('cmd') == 'H2T':
                    hanmod = '1' if input_lang == 'zh-tw' else '0'
                elif api_params.get('cmd') == 'G2T':
                    hanmod = api_params.get('lang', 'en')
                else:
                    hanmod = '0'
                
                lmjmod = '0' if output_format == 'tai-han' else '1'
                
                response = StreamingHttpResponse(getRendered(uid, sock, hanmod, lmjmod, outmod, the_file.name, ip))
                response['Content-Disposition'] = "attachment; filename*=UTF-8''%s" % urllib.parse.quote(the_file.name)
                return response
            else:
                tic = dt.datetime.now()
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
        'input_lang_form': input_lang_form,
        'output_format_form': output_format_form,
        'outmodform': outmodform,
    }
    return render(request, "subtitle.html", context)
