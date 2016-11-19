# Kerboodler
# By Eddie Hart from TechJunk.co.uk
#
# https://www.techjunk.co.uk

import urllib.request, urllib.parse, xmltodict, tempfile, getpass
from os.path import expanduser
import os
import sys
from fpdf import FPDF

version = 0.913

import ctypes
title = "Kerboodler v"+str(version)+" By Eddie Hart - TechJunk.co.uk"
ctypes.windll.kernel32.SetConsoleTitleA(title.encode("utf-8"))

class NoRedirectHandler(urllib.request.HTTPRedirectHandler):
    def http_error_302(self, req, fp, code, msg, headers):
        infourl = urllib.response.addinfourl(fp, headers, req.get_full_url())
        infourl.status = code
        infourl.code = code
        return infourl
    http_error_300 = http_error_302
    http_error_301 = http_error_302
    http_error_303 = http_error_302
    http_error_307 = http_error_302

def post(url, headers, data):
    # make a string with the request type in it:
    method = "POST"
    # create a handler. you can specify different handlers here (file uploads etc)
    # but we go for the default
    handler = NoRedirectHandler()#urllib.request.HTTPHandler()
    # create an openerdirector instance
    opener = urllib.request.build_opener(handler)
    # build a request
    data = urllib.parse.urlencode(data).encode("utf-8")
    request = urllib.request.Request(url, data=data)
    # add any other information you want
    for header, val in headers.items():
        request.add_header(header,val)
    # overload the get method function with a small anonymous function...
    request.get_method = lambda: method
    # try it; don't forget to catch the result
    try:
        connection = opener.open(request)
    except urllib.request.HTTPError as e:
        connection = e

    # check. Substitute with appropriate HTTP code.]
    headers = {}
    for header in connection.getheaders():
        if header[0] in headers:
            if type(headers[header[0]]) is list:
                headers[header[0]].append(header[1])
            else:
                headers[header[0]] = [headers[header[0]], header[1]]
        else:
            headers[header[0]] = header[1]
    return {"headers": headers, "data":connection.read().decode('utf-8')}

def get(url, headers, data):
    # make a string with the request type in it:
    method = "GET"
    # create a handler. you can specify different handlers here (file uploads etc)
    # but we go for the default
    handler = NoRedirectHandler()#urllib.request.HTTPHandler()
    # create an openerdirector instance
    opener = urllib.request.build_opener(handler)
    # build a request
    data = urllib.parse.urlencode(data).encode("utf-8")
    request = urllib.request.Request(url, data=data)
    # add any other information you want
    for header, val in headers.items():
        request.add_header(header,val)
    # overload the get method function with a small anonymous function...
    request.get_method = lambda: method
    # try it; don't forget to catch the result
    try:
        connection = opener.open(request)
    except urllib.request.HTTPError as e:
        connection = e

    # check. Substitute with appropriate HTTP code.]
    headers = {}
    for header in connection.getheaders():
        if header[0] in headers:
            if type(headers[header[0]]) is list:
                headers[header[0]].append(header[1])
            else:
                headers[header[0]] = [headers[header[0]], header[1]]
        else:
            headers[header[0]] = header[1]
    return {"headers": headers, "data":connection.read().decode('utf-8')}

print("Kerboodler v"+str(version))
print("By Eddie Hart from TechJunk.co.uk")
print()
sessionID = input("Please paste session ID, or press enter to login: ").strip().lower()
if(sessionID==""):
    if 'idlelib.run' in sys.modules:
        print()
        print("==== PLEASE READ ====")
        print("You are running Kerboodler in IDLE. This means we cannot mask your password.")
        print("Please either reload Kerboodler in a terminal emulator or be aware your password")
        print("will be visible as you are typing it.")
        print("==== PLEASE READ ====")
        print()
        input("Press any key to continue... ")
    print("In that case, type your login details below. Be warned that this will sign you out of any active Kerboodle sessions.")
    loginLoop = True
    while loginLoop:
        uname = input("Username or email address: ")
        passw = ""
        if 'idlelib.run' in sys.modules:
            passw = input("Password: ")
        else:
            passw = getpass.getpass("Password: ")
        icode = input("Institution code: ")
        print("Attempting login...")
        response = post("https://www.kerboodle.com/users/login", {}, {"user[login]":uname,"user[password]":passw,"user[institution_code]":icode})
        if "One or more of your details are incorrect." in response["data"]:
            print()
            print("  ===> One or more of your details are incorrect. Please try logging in again.")
        elif '/app">redirected' in response["data"]:
            print("Login OK")
            loginLoop = False
            if type(response["headers"]['Set-Cookie']) is list:
                for cookie in response["headers"]['Set-Cookie']:
                    if(cookie.startswith("_session_id")):
                        sessionID = cookie.split(";")[0].split("=")[1]
            else:
                sessionID = response["headers"]['Set-Cookie'].split(";")[0].split("=")[1]
        elif '/active_session">redirected' in response["data"]:
            print("Forcing login...")
            session_id = ""
            if type(response["headers"]['Set-Cookie']) is list:
                for cookie in response["headers"]['Set-Cookie']:
                    if(cookie.startswith("_session_id")):
                        session_id = cookie.split(";")[0].split("=")[1]
            else:
                session_id = response["headers"]['Set-Cookie'].split(";")[0].split("=")[1]
            response2 = response = get("https://www.kerboodle.com/users/force_login", {"Cookie": "_session_id="+session_id, "Referer": "https://www.kerboodle.com/users/active_session"}, {})
            if "Set-Cookie" in response2["headers"]:
                if type(response2["headers"]['Set-Cookie']) is list:
                    for cookie in response2["headers"]['Set-Cookie']:
                        if(cookie.startswith("_session_id")):
                            session_id = cookie.split(";")[0].split("=")[1]
                else:
                    session_id = response2["headers"]['Set-Cookie'].split(";")[0].split("=")[1]
            sessionID = session_id
            loginLoop = False
kerboodleURL = input("Please paste the entire Kerboodle textbook URL: ").strip()
apiURL = kerboodleURL.split(".html", 1)[0]+".xml?file=interaction-0.xml"#.replace("https://", "http://")
print()
print("Downloading textbook info...")
opener = urllib.request.build_opener()
opener.addheaders.append(('Cookie', '_session_id='+sessionID))
apiContent = xmltodict.parse(opener.open(apiURL).read().decode("utf-8"))
ebook = apiContent["assessmentItem"]["itemBody"]["div"][1]["div"]["ebook"]

print("Textbook is", ebook["@title"])

pageURLs = []

for page in ebook["pages"]["page"]:
	pageURLs.append(page["@url"])

print("Detected",len(pageURLs),"pages.")

tempDir = tempfile.TemporaryDirectory()

pageFiles = []
print("Downloading pages... This may take some time")
count = 0
endchar = '\n' if 'idlelib.run' in sys.modules else '\r'
print("Starting...", end=endchar)
for page in pageURLs:
    pageFiles.append(tempfile.NamedTemporaryFile(dir=tempDir.name, suffix=".jpg", delete=False))
    #print((count+1),len(pageURLs))
    print(str(round((count+1)/len(pageURLs)*100, 1))+"%       ", end=endchar)
    pageFiles[count].write(opener.open(page).read())
    pageFiles[count].close()
    count += 1
print("Done downloading pages.")

pdflocation = expanduser("~\\")+ebook["@title"]+".pdf"
pdf = FPDF()
count = 0
print("Creating PDF...")
print("Starting...", end=endchar)
for page in pageFiles:
    pdf.add_page()
    pdf.image(page.name,0,0,210,297)
    #print((count+1),len(pageURLs))
    print(str(round((count+1)/len(pageURLs)*100, 1))+"%       ", end=endchar)
    count += 1
print("Done creating PDF.")
print("Saving PDF... This may take a minute or two...")
pdf.output(pdflocation, "F")
print("Saved PDF to", pdflocation)
print("Cleaning up temp files...")
tempDir.cleanup()
