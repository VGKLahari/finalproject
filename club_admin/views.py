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

# Create your views here.
alert = 0
flag=0
alert2=0
flag2=0
delsuper=0
global sadmintoken
@never_cache
def delete_session(request):
    global delsuper
    d = request.GET.get("logout")
    if(d == 'slogout'):

        try:
            print(request.session['suserid'])
            del request.session['suserid']
            del request.session['spassword']
            delsuper = 1
            logout(request)
            
            return redirect(index)
        except:
            logout(request)
            
            return redirect(index)
    else:
        try:
            
            del request.session['userid']
            del request.session['password']
            logout(request)
            
            return redirect(adminlog)
        except:
            logout(request)
            
            return redirect(adminlog)
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
            clubs.append(i['clubname'].capitalize()+"_Club")
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
    global delsuper
        #print('hello')
    try:                         #to check if the user is already logged in also useful when moving from sub super admin
                                     #pages to main super admin page using user made back button
        print('welcome')
        id2=request.session['suserid']
            
        s = sadmintoken
        print('hi')
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
    if(deleteadmin==1):
        deleteadmin=0
    
    if(flag2==1):
        alert2 = 1
        flag2 = 0
    else:
        alert2 = 0
    
    return render(request,'admin2.html',{'alert':alert2})

@never_cache
def admin(request):
    global alert2
    global flag2
    global admintoken
    try:
        id3 = request.session['userid']
        a = admintoken
        return render(request,'admin.html')
    except:
        try:
            id=request.POST["id"]
            pword=request.POST["pword"]
            response = requests.post('http://localhost:5000/adminlog',data={'username':id,'password':pword})
            result = response.json()
            #print(result)
            try:
                admintoken=result['access_token']
                
                request.session['userid'] =id
                request.session['password']=pword
                alert2 = 0
                return render(request,"admin.html")
            except:
                alert2 = 1
                flag2 = 1
                return redirect(adminlog)
        except:
            return render(request,"admin.html")


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
        print(response)
        return redirect(viewadmin)
    else:
        return redirect(index)
@never_cache
def addadmin(request):
    if(request.session['suserid']):

        return render(request,'addadmin.html')
    else:
        return redirect(index)

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
        return render(request,'confirmdelete.html',{'data':data,'club':club_name,'admin':admin_name})
    else:
        return redirect(index)
@never_cache
def confirmdelete(request):
    if(request.session['suserid']):

        admin_name =request.GET.get("admin_name")
        global sadmintoken
        response = requests.post('http://localhost:5000/del',data={'username':admin_name},headers = {'Authorization':f'Bearer {sadmintoken}'})
        return redirect(super_admin)
    else:
        redirect(index)
