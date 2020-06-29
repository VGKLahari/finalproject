from django.shortcuts import render,redirect
from django.db import models
from django.db import connection
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import cache_control,never_cache
from django.http import HttpResponse
import requests
from password_generator import PasswordGenerator
from django.utils.cache import add_never_cache_headers
import random
import math
from password_generator import PasswordGenerator
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags

# Create your views here.
alert = 0
flag=0
alert2=0
flag2=0
club=''
ids=[]
global sadmintoken
global admintoken
global params
@never_cache
def delete_session(request):
    
    d = request.GET.get("logout")
    if(d == 'slogout'):

        try:
            print(request.session['suserid'])
            del request.session['suserid']
            del request.session['spassword']
            logout(request)
            
            return redirect(index)
        except:
            logout(request)
            
            return redirect(index)
    else:
        try:
            
            del request.session['userid']
            del request.session['password']
            club=''
            ids=[]
            del request.session['club']
            del request.session['ids']
            logout(request)
            
            return redirect(index)
        except:
            logout(request)
            
            return redirect(index)
@never_cache
def index(request):
    global alert
    global flag
    global delsuper
    #print(alert)
    #print('hello')
    
    try:
        a=request.session['suserid']
        b=request.session['spassword']
        
        return redirect(super_admin)
        
    except:
        #print('hi')
        response=requests.get('http://localhost:5000/clubnames')
        club_names=response.json()
        #print(club_names)
        clubs=[]
        for i in club_names:
            clubs.append(i['clubname'])
            
        if(flag==1):
            alert = 1
            flag = 0
        else:
            alert = 0
        return render(request,'index2.html',{'club':clubs,'alert':alert})

@never_cache
def super_admin(request):
    global alert
    global flag
    global sadmintoken
    try:                        
        
        id2=request.session['suserid']
            
        s = sadmintoken
        return render(request,'super_admin.html')
    except:
        if(request.method=='POST'):
            id=request.POST["sid"]
            pword=request.POST["spword"]
            #print(id,pword,'hello',delsuper)
            response = requests.post('http://localhost:5000/login',data={'username':id,'password':pword})
            result = response.json()
            try:
                sadmintoken = result['access_token']
                print(sadmintoken)
                request.session['suserid'] =id
                request.session['spassword']=pword
                alert = 0
                return redirect(super_admin)
            except:
                alert=1
                flag=1
                return redirect(index)
        else:

            '''try:                         #to check if the user is logging in for the first time
                id=request.POST["sid"]
                pword=request.POST["spword"]
                print(id,pword,'hello',delsuper)
                if(delsuper==1):'''
            try:
                ID = request.session['suserid']
                return render(request,'super_admin.html')
            except:
                return redirect(index)
                    
     


@never_cache
def adminlog(request):
    
    global alert2
    global flag2
    global deleteadmin
    '''try:
        a=request.session['userid']
        b=request.session['password']
        return render(request,'admin.html')'''

    club = request.GET.get('club')
    if(flag2==1):
        alert2 = 1
        flag2 = 0
    else:
        alert2 = 0
    
    return render(request,'admin2.html',{'alert':alert2,'club':club})

@never_cache
def admin(request):
    global alert2
    global flag2
    global admintoken
    global club
    try:
        id3 = request.session['userid']
        a = admintoken
        print('hello')
        return render(request,'admin.html')
    except:
        print('fkjd')
        if(request.method=='POST'):
            
            aid = int(request.POST["id"])
            apword = request.POST["pword"]
            club = request.POST["club_name"]
            
            #print(club)
            response  = requests.post('http://localhost:5000/adminlog',data={'userid':aid,'password':apword,'clubname':club})
            #print(response)
            result = response.json()
            #print(result)
            try:

                admintoken=result['access_token']
                print('hi')    
                request.session['userid'] =aid
                request.session['password']=apword
                request.session['club']=club
                alert2 = 0
                return redirect(admin)
            except:
                alert2 = 1
                flag2 = 1
                return redirect(adminlog)
        else:
            try:
                aID =request.session['userid']
                return render(request,'admin.html')
            except:
                return redirect(adminlog)


@never_cache
def viewadmin(request):
    if(request.session['suserid']):
        response=requests.get('http://localhost:5000/adminlogin',headers = {'Authorization':f'Bearer {sadmintoken}'})
        data=response.json()
        admin={}
        for i in data:
            admin[i["clubname"]]=i["username"]
        return render(request,"viewadmins.html",{'data':admin})
    else:
        return redirect(index)



    
@never_cache
def addadmins(request):
    global sadmintoken
    global params
    if(request.session['suserid']):
        id=int(request.POST["id"])
        name=request.POST["name"]
        cname=request.POST["cname"]
        pwo=PasswordGenerator()
        pword=pwo.generate()
        
        params = dict(uid=id,username=name,password=pword,clubname=cname)
        print(sadmintoken)
        print(params)
        response=requests.post('http://localhost:5000/addclub',data=params,headers ={'Authorization':f'Bearer {sadmintoken}'})
        #print(response)
        if 'message' not in response:
            return redirect(mailadmin)
        else:
            return HttpResponse(response['message'])
    else:
        return redirect(index)
    
@never_cache
def addadmin(request):
    if(request.session['suserid']):

        return render(request,'addadmin.html')
    else:
        return redirect(index)

@never_cache
def mailadmin(request):
    global sadmintoken
    global params
    param=params
    print(param)
    response = requests.get('http://localhost:5000/mail',data={'userid':param['uid']},headers = {'Authorization':f'Bearer {sadmintoken}'})
    admin_emailid=response.json()
    if 'message' not in admin_emailid:
        subject="Congratulations you are appointed as Admin"
        html_message = render_to_string('mail_admin.html', {'user': param['username'],'password':param['password'],'clubname':param['clubname']})
        plain_message = strip_tags(html_message)
        from_email = 'teamcosc555@gmail.com'
        print(admin_emailid)
        to = admin_emailid[0]['emailid']
        send_mail(subject, plain_message, from_email, [to], html_message=html_message,fail_silently=False)
        return HttpResponse("Success")
    else:
        return HttpResponse(admin_emailid['message'])

@never_cache
def deladmin(request):
    if(request.session['suserid']):
        global sadmintoken
        response=requests.get('http://localhost:5000/adminlogin',headers = {'Authorization':f'Bearer {sadmintoken}'})
        data=response.json()
        admin={}
        for i in data:
            admin[i["clubname"]]=i["username"]
        return render(request,'deleteadmin.html',{'data':admin})
    else:
        return redirect(index)

@never_cache
def deleteadmin(request):
    if(request.session['suserid']):
        admin_name=request.GET.get("admin_name")
        club_name =request.GET.get("club_name")
        #print(admin_name,club_name)
        global sadmintoken
        response = requests.post('http://localhost:5000/clubmembers',data={'clubname':club_name},headers = {'Authorization':f'Bearer {sadmintoken}'})
        data = response.json()
        #print(data)
        for i in range(0,len(data)):
            d=dict()
            d['stuid']=data[i]['stuid']
            d['name']=data[i]['name']
            d['branch']=data[i]['branch']
            d['crole']=data[i]['crole']
            data[i] = d
        #print(data)
        return render(request,'confirmdelete.html',{'data':data,'club':club_name,'admin':admin_name})
    else:
        return redirect(index)
@never_cache
def confirmdelete(request):
    if(request.session['suserid']):

        
        admin_name =request.GET.get("admin_name")
        global sadmintoken
        response = requests.post('http://localhost:5000/del',data={'username':admin_name},headers = {'Authorization':f'Bearer {sadmintoken}'})
        response=response.json()
        if (response['message']=="deleted"):
            print('message received')
            response = requests.get('http://localhost:5000/mail',data={'username':admin_name},headers = {'Authorization':f'Bearer {sadmintoken}'})
            admin_emailid=response.json()
            if 'message' not in admin_emailid:
                subject="Your Club is DeRegistered"
                html_message = render_to_string('mail_deladmin.html', {'user':admin_name})
                plain_message = strip_tags(html_message)
                from_email = 'teamcosc555@gmail.com'
                to = admin_emailid[0]['emailid']
                send_mail(subject, plain_message, from_email, [to], html_message=html_message,fail_silently=False)
                return HttpResponse("Success")
            else:
                return HttpResponse(admin_emailid['message'])
    else:
        redirect(index)

def generateOTP() :
    string = '0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'
    OTP = ""
    length = len(string)
    for i in range(6) :
        OTP += string[math.floor(random.random() * length)]
    return OTP
@never_cache
def forgetpassword(request):
    global admintoken
    otp=generateOTP()
    adminid=request.session['userid']
    response = requests.post('http://localhost:5000/forgetpassword',data={'userid':adminid,'otp':otp},headers = {'Authorization':f'Bearer {admintoken}'})
    admin_emailid=response.json()
    if 'message' not in admin_emailid:
        subject="Change your Password"
        html_message = render_to_string('mail_template.html', {'otp': otp,'link':'http://localhost:8000/reset/'})
        plain_message = strip_tags(html_message)
        from_email = 'saitejach096@gmail.com'
        to = admin_emailid[0]['emailid']
        send_mail(subject, plain_message, from_email, [to], html_message=html_message,fail_silently=False)
        return HttpResponse("Check your registered mail for OTP for password change.")
    else:
        return HttpResponse(admin_emailid['message'])

@never_cache
def reset(request):
    return render(request,'ResetPassword.html')

@never_cache
def changepassword(request):
    otp=request.GET.get('otp')
    password=request.GET.get('pword')
    print(otp,password)
    response=requests.post('http://localhost:5000/changepassword',data={'otp':otp,'password':password})
    result=response.json()
    return HttpResponse(result['message'])
@never_cache
def checkclub(request):
    global sadmintoken
    response=requests.get('http://localhost:5000/adminlogin',headers = {'Authorization':f'Bearer {sadmintoken}'})
    data=response.json()
    admin={}
    for i in data:
        admin[i["clubname"]]=i["username"]
    return render(request,'checkclub.html',{'data':admin})
@never_cache
def checkoutclub(request):
    admin_name=request.GET.get("admin_name")
    club_name =request.GET.get("club_name")
    global sadmintoken
    response = requests.post('http://localhost:5000/clubmembers',data={'clubname':club_name},headers = {'Authorization':f'Bearer {sadmintoken}'})
    data = response.json()
    for i in range(0,len(data)):
        d=dict()
        d['stuid']=data[i]['stuid']
        d['name']=data[i]['name']
        d['branch']=data[i]['branch']
        d['crole']=data[i]['crole']
        data[i] = d
    print(data)
    return render(request,'checkoutclub.html',{'data':data,'club':club_name,'admin':admin_name})

@never_cache
def edit(request):
    admin_name=request.GET.get("admin_name")
    return render(request,'edit.html',{'oldadmin':admin_name})
@never_cache
def editadmin(request):
    global sadmintoken
    admin_name=request.GET.get("admin_name")
    newadminid=request.GET.get("id")
    response = requests.post('http://localhost:5000/editadmin',data={'admin_name':admin_name,'newadminid':newadminid},headers = {'Authorization':f'Bearer {sadmintoken}'})
    response=response.json()
    return HttpResponse(response['message'])

@never_cache
def viewrequests(request):
    global admintoken
    global club
    global ids
    #print(club)
    response = requests.get('http://localhost:5000/requesttoclub',data={'clubname':club})
    data = response.json()
    #print(data)
    checks = []
    ids = []

    for i in data:
        checks.append(' Request from'+' '+i['name']+','+str(i['stuid'])+','+i['branch']+','+'year'+' '+str(i['year']))
        ids.append(i['stuid'])
    request.session['ids']=ids     
    return render(request,'showrequests.html',{'club':club,'len':len(data),'packed':zip(checks,ids)})

@never_cache
def dealrequests(request):
    global admintoken
    club = request.session['club']
    req = request.GET.getlist('accept')
    success=0
    #print(type(req))
    #print(type(req),type(req[0]))
    req = list(map(int,req))
    ids=request.session['ids']
    #print(req,ids,admintoken)
    for i in ids:
        if i in req:
            acceptstatus=1
        else:
            acceptstatus=0
        #print(acceptstatus) 
        response=requests.post('http://localhost:5000/requesttoclub',data={'cid':0,'stuid':i,'clubname':club,'crole':'Member','acceptstatus':acceptstatus},headers = {'Authorization':f'Bearer {admintoken}'})
        response = requests.get('http://localhost:5000/mail',data={'userid':i},headers = {'Authorization':f'Bearer {admintoken}'})
        
        admin_emailid = response.json()
        if 'message' not in admin_emailid:

            subject="Congratulations you are added to "+club
            html_message = render_to_string('mail_student.html', {'user':i,'clubname':club})
            plain_message = strip_tags(html_message)
            from_email = 'teamcosc555@gmail.com'
            to = admin_emailid[0]['emailid']

            send_mail(subject, plain_message, from_email, [to], html_message=html_message,fail_silently=False)
            success=1
        else:
            success=0
    if(success):
        return HttpResponse("Success")
    else:
        return HttpResponse(admin_emailid["message"])

    

@never_cache
def addevent(request):
    global admintoken
    club = request.session['club']
    return render(request,'addevent.html')
@never_cache
def newevent(request):
    global admintoken
    club = request.session['club']
    eventname=request.GET.get("eventname")
    desc = request.GET.get("description")
    date = request.GET.get("eventdate")
    venue =request.GET.get("venue")
    start=request.GET.get("start")
    end = request.GET.get("end")
    coordinator = request.GET.get("coordinator")
    contact = request.GET.get("contact")
    print(eventname,desc,date,type(date))
    requests.post('http://localhost:5000/displaypostevents',data={'eventname':eventname,'eventdate':date,'clubname':club,'description':desc,'venue':venue,'start':start,'end':end,'coordinator':coordinator,'contact':contact},headers = {'Authorization':f'Bearer {admintoken}'})
    return redirect(admin)

@never_cache
def members(request):
    global admintoken
    club = request.session['club']
    response = requests.post('http://localhost:5000/clubmembers',data={'clubname':club},headers = {'Authorization':f'Bearer {admintoken}'})
    data = response.json()
    for i in range(0,len(data)):
        d=dict()
        d['stuid']=data[i]['stuid']
        d['name']=data[i]['name']
        d['branch']=data[i]['branch']
        d['crole']=data[i]['crole']
        data[i] = d
    return render(request,'members.html',{'data':data})

@never_cache
def deletemembers(request):
    global admintoken
    club = request.session['club']
    response = requests.post('http://localhost:5000/clubmembers',data={'clubname':club},headers = {'Authorization':f'Bearer {admintoken}'})
    data = response.json()
    id=[]
    for i in range(0,len(data)):
        d=dict()
        d['stuid']=data[i]['stuid']
        d['name']=data[i]['name']
        d['branch']=data[i]['branch']
        d['crole']=data[i]['crole']
        d['year']=data[i]['year']
        data[i] = d
        id.append(data[i]['stuid'])
    return render(request,'deletemembers.html',{'data':data,'packed':zip(data,id)})

@never_cache
def confirmdelmembers(request):
    global admintoken
    club = request.session['club']
    dels = request.GET.getlist('delmembers')
    dels = list(map(int,dels))
    success=0
    for d in dels:
        response = requests.post('http://localhost:5000/delmembers',data={'clubname':club,'stuid':d},headers = {'Authorization':f'Bearer {admintoken}'})
        response = requests.get('http://localhost:5000/mail',data={'userid':d},headers = {'Authorization':f'Bearer {admintoken}'})
        admin_emailid=response.json()
        if 'message' not in admin_emailid:
            subject="You got removed from Club"
            html_message = render_to_string('mail_delstudent.html', {'user': d,'clubname':club})
            plain_message = strip_tags(html_message)
            from_email = 'teamcosc555@gmail.com'
            to = admin_emailid[0]['emailid']
            send_mail(subject, plain_message, from_email, [to], html_message=html_message,fail_silently=False)
            success=1
        else:
            success=0
    if(success):
        return HttpResponse("Success")
    else:
        return HttpResponse(admin_emailid["message"])

    return redirect(deletemembers)

@never_cache
def events(request):
    global admintoken
    club = request.session['club']
    response = requests.get('http://localhost:5000/displaypostevents',data={'clubname':club})
    data=response.json()
    print(data)
    for i in range(0,len(data)):
        d=dict()
        d['eventname']=data[i]['eventname']
        d['eventdate']=data[i]['eventdate']
        d['description']=data[i]['description']
        d['venue']=data[i]['venue']
        d['start']=data[i]['time_format(start,"%T")']
        d['end']=data[i]['time_format(end,"%T")']
        d['coordinator']=data[i]['coordinator']
        d['contact']=data[i]['contact']
        data[i] = d
    return render(request,'events.html',{'data':data})


