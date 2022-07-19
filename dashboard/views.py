from django.conf import settings
from django.shortcuts import render,redirect
from django.http import HttpResponse
from django.contrib import messages
from matplotlib.pyplot import title
from sqlalchemy import false
from .forms import *
from django.views import generic
from youtubesearchpython import VideosSearch
import requests
import wikipedia
import random
from newsapi import NewsApiClient
from django.http import JsonResponse
from Portfolio import flask_app
import os
# Create your views here.
def home(request):
    return render(request,'dashboard/home.html')

def notes(request):
    if request.method == "POST":
        form = NotesForm(request.POST)
        if form.is_valid():
            notes = Notes(user=request.user,title=request.POST['title'],description = request.POST['description'])
            notes.save()
        messages.success(request,f"Notes added from {request.user.username} successfully")
    else:
        form = NotesForm()
    notes = Notes.objects.all()
    context = {"notes":notes,'form':form}
    return render(request,'dashboard/notes.html',context)

def delete_note(request,pk):
    Notes.objects.get(id = pk).delete()
    return redirect("notes")

class NotesDetailView(generic.DetailView):
    model = Notes

def homework(request):
    if request.method == "POST":
        form = HomeworkForm(request.POST)
        if form.is_valid():
            try:
                finished = request.POST['is_finishhed']
                if finished == 'on':
                    finished = True
                else:
                    finished = False
            except:
                finished = False
            homework = Homework(user = request.user,subject = request.POST['subject'],title = request.POST['title'],description = request.POST['description'],due = request.POST['due'])
            homework.save()
    else:
        form = HomeworkForm()
    homework = Homework.objects.all()
    context = {"homework":homework,'form':form}
    return render(request,'dashboard/homework.html',context)

def update_homework(request,pk):
    homework = Homework.objects.get(id = pk)
    if homework.is_finished == True:
        homework.is_finished = False
    else:
        homework.is_finished = True
    homework.save()
    return redirect('homework')



def delete_homework(request,pk):
    Homework.objects.get(id = pk).delete()
    return redirect("homework")

def youtube(request):
    if request.method == "POST":
        form = DashboardForm(request.POST)
        text = request.POST['text']
        video = VideosSearch(text,limit=10)
        result_list = []
        for i in video.result()['result']:
            result_dict = {'input':text,'title':i['title'],'duration':i['duration'],'thumbnails':i['thumbnails'][0]['url'],'channel':i['channel']['name'],'link':i['link'],'views':i['viewCount']['short'],'published':i['publishedTime']}
            description = ""
            if i['descriptionSnippet']:
                for j in i['descriptionSnippet']:
                    description+=j['text']
            result_dict['description'] = description
            result_list.append(result_dict)
            context = {'form':form,'results':result_list}
        return render(request,'dashboard/youtube.html',context)
    else:
        form = DashboardForm()
    context = {'form':form}
    return render(request,'dashboard/youtube.html',context)

def todo(request):
    if request.method == 'POST':
        form = TodForm(request.POST)
        if form.is_valid():
            try:
                finished = request.POST["is_finished"]
                if finished =="on":
                    finished = True
                else:
                    finished = False
            except:
                finished = False
            todos = Todo(
                user = request.user,
                title = request.POST['title'],
                is_finished = finished
            )
            todos.save()
    else:
        form = TodForm()
    todo = Todo.objects.all()
    if len(todo) == 0:
        todos_done = True
    else:
        todos_done = False
    
    context = {'form':form,'todos':todo,'todos_done':todos_done
    }
    return render(request,'dashboard/todo.html',context)


def update_todo(request,pk=None):
    todo = Todo.objects.get(id = pk)
    if todo.is_finished == True:
        todo.is_finished = False
    else:
        todo.is_finished = True
    todo.save()
    return redirect('todo')

def delete_todo(request,pk):
    Todo.objects.get(id = pk).delete()
    return redirect("todo")

def books(request):
    if request.method == "POST":
        form = DashboardForm(request.POST)
        text = request.POST['text']
        url = "https://www.googleapis.com/books/v1/volumes?q="+text
        r = requests.get(url)
        answer = r.json()
        result_list = []
        for i in range(10):
            result_dict = {
                'title':answer['items'][i]['volumeInfo']['title'],
                'subtitle':answer['items'][i]['volumeInfo'].get('subtitle'),
                'description':answer['items'][i]['volumeInfo'].get('description'),
                'count':answer['items'][i]['volumeInfo'].get('pageCount'),
                'categories':answer['items'][i]['volumeInfo'].get('categories'),
                'rating':answer['items'][i]['volumeInfo'].get('pagerating'),
                'thumbnail':answer['items'][i]['volumeInfo'].get('imageLinks').get('thumbnail'),
                'preview':answer['items'][i]['volumeInfo'].get('previewLink')
                
            }
            result_list.append(result_dict)
            context = {'form':form,'results':result_list}
        return render(request,'dashboard/books.html',context)
    else:
        form = DashboardForm()
    context = {'form':form}
    return render(request,'dashboard/books.html',context)

def dictionary(request):
    if request.method == "POST":
        form = DashboardForm(request.POST)
        text = request.POST['text']
        url = "https://api.dictionaryapi.dev/api/v2/entries/en_US/"+text
        r = requests.get(url)
        answer = r.json()
        try:
            phonetics = answer[0]['phonetics'][0]['text']
            audio = answer[0]['phonetics'][0]['audio']
            definition = answer[0]['meanings'][0]['definitions'][0]['definition']
            example = answer[0]['meanings'][0]['definitions'][0]['example']
            synonyms = answer[0]['meanings'][0]['definitions'][0]['synonyms']
            context = {
                'form':form,
                'input':text,
                'phonetics':phonetics,
                'audio':audio,
                'definition':definition,
                'example':example,
                'synonyms':synonyms
            }
        except:
            context = {
                'form':form,
                'input':''
            }
        return render(request,"dashboard/dictionary.html",context)
    else:
        form = DashboardForm()
        context = {'form':form}
    return render(request,"dashboard/dictionary.html",context)

def wiki(request):
    if request.method == 'POST':
        # try:
        text = request.POST['text']
        form = DashboardForm(request.POST)
        search = wikipedia.page(text)
        context = {
            'form':form,
            'title':search.title,
            'link':search.url,
            'details':search.summary
        }
        return render(request,"dashboard/wiki.html",context)
        # except wikipedia.DisambiguationError as e:
        #     s = random.choice(e.options)
        #     p = wikipedia.page(s)
    else:
        form = DashboardForm()
        context = {
            'form':form
        }
    return render(request,"dashboard/wiki.html",context)
 

temp_img = "https://images.pexels.com/photos/3225524/pexels-photo-3225524.jpeg?auto=compress&cs=tinysrgb&dpr=2&w=500"
apikey = "cb79a686f715431daa4661919c5f4d2d"

def news(request):
    page = request.GET.get('page', 10)
    search = request.GET.get('search', None)
    

    if search is None or search=="top":
        url = "https://newsapi.org/v2/top-headlines?country={}&page={}&apiKey={}".format(
            "us",1,apikey
        )
    else:
        url = "https://newsapi.org/v2/everything?q={}&sortBy={}&page={}&apiKey={}".format(
            search,"popularity",page,apikey
        )
    r = requests.get(url=url)
    
    data = r.json()
    if data["status"] != "ok":
        return HttpResponse("<h1>Request Failed</h1>")
    data = data["articles"]
    context = {
        "success": True,
        "data": [],
        "search": search
    }
    for i in data:
        context["data"].append({
            "title": i["title"],
            "description":  "" if i["description"] is None else i["description"],
            "url": i["url"],
            "image": temp_img if i["urlToImage"] is None else i["urlToImage"],
            "publishedat": i["publishedAt"]
        })
    return render(request, 'dashboard/news.html', context=context)

def register(request):
    if request.method == "POST":
        form  = UserRegistrationForm(request.POST)
        if form.is_valid():
            form.save
            username = form.cleaned_data.get('username')
            messages.success(request,f"Account created for {username}")
            return redirect('login')
    else:
        form  = UserRegistrationForm()
    context = {
        'form':form
    }
    return render(request,'dashboard/register.html',context)

def profile(request):    
    return redirect("https://www.linkedin.com/in/ippatapu-venkata-srisurya/")