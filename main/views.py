from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import Group
from django.views.generic import DetailView
from django.contrib import messages
from .forms import *
import datetime
import json
# Create your views here.

def home(request):
    return render(request, 'home.html',)

def advertisements(request):
    all_posts = Post.objects.order_by('-date_created')
    if request.method == 'POST':
        post_id = request.POST.get('detele_post_id')
        post = Post.objects.filter(id = post_id).first()
        if post:
            post.delete()

    return render(request, 'advertisements.html', {'all_posts': all_posts})

def sign_up(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        profile_form = ProfileForm()
        if form.is_valid():
            user = form.save()
            Profile.objects.create(user_id = user.id)
            login(request, user)
            return redirect('/home')
    else:
        form = RegisterForm()

    return render(request, 'registration/sign_up.html', {'form':form})

# region DOCTOR
def is_doctor(user):
    return user.groups.filter(name='Doctor_perm').exists()

@login_required(login_url='home.html')
@user_passes_test(is_doctor)
def profile(request, id):
    next_visits = Visit.objects.filter(user_id = id, 
                            date__gte=datetime.datetime.today()).order_by('-date', '-time')
    past_visits = Visit.objects.filter(user_id = id, 
                            date__lt=datetime.datetime.today()).order_by('-date', '-time')

    next_visits = change_doctor_info(next_visits)
    past_visits = change_doctor_info(past_visits)

    user = User.objects.get(id=id)
    profile = Profile.objects.get(user_id = id)

    return render(request, 'doctor/profile.html', {'user': user, 'profile': profile, 'past_visits': past_visits, 'next_visits': next_visits})

@login_required(login_url='home.html')
@user_passes_test(is_doctor)
def create_post(request):
    if request.method == 'POST':
        form = PostForm(request.POST)
        if form.is_valid():
            post = form.save()
            return redirect('/home')
    else:
        form = PostForm()
    
    return render(request, 'doctor/create_post.html', {'form':form})

@login_required(login_url='home.html')
@user_passes_test(is_doctor)
def patients(request):
    users = User.objects.filter(groups__isnull=True)
    return render(request, 'doctor/patients.html', {'users':users})

@login_required(login_url='home.html')
@user_passes_test(is_doctor)
def schedule(request):
    if request.method == 'POST':
        date=request.POST.get('date')
        visits = Visit.objects.filter(doctor = request.user.id, date=date)
        visits.order_by('-time')
        for v in visits:
            patient = User.objects.filter(id = v.user_id)
            v.user_id = patient[0]
        print(date, visits)
        return render(request, 'doctor/schedule.html', {'date': date, 'visits':visits})
    else:
        date = datetime.date.today().strftime('%Y-%m-%d')
        visits = Visit.objects.filter(doctor = request.user.id, date=date)
        visits.order_by('date')
        for v in visits:
            patient = User.objects.filter(id = v.user_id)
            v.user_id = patient[0]
        return render(request, 'doctor/schedule.html', {'date': date, 'visits':visits, 'default': True})

#endregion

# region PATIENT
@login_required(login_url='home.html')
def my_profile(request):
    profile = Profile.objects.get(user_id=request.user.id)
    if request.method == 'POST':
        profile.tel = request.POST.get('tel')
        if profile.is_doctor:
            user = User.objects.get(id=request.user.id)
            user.email = request.POST.get('email')
            profile.spec = request.POST.get('spec')
            profile.desc = request.POST.get('desc')
            user.save()
        else:
            profile.pesel = request.POST.get('pesel')
            profile.city = request.POST.get('city')
            profile.zip_code = request.POST.get('zip_code')
            profile.street = request.POST.get('street')
            profile.addr_number = request.POST.get('addr_number')
        profile.save()
        messages.success(request, 'Profile updated!')
        return redirect('/my-profile')
    return render(request, 'my-profile.html', {'profile': profile})


@login_required(login_url='home.html')
def my_visits(request):
    next_visits = Visit.objects.filter(user_id = request.user.id, 
                                        date__gt=datetime.datetime.today()).order_by('-date', '-time')
    today_visits = Visit.objects.filter(user_id = request.user.id, 
                                        date=datetime.datetime.today()).order_by('-time')
    past_visits = Visit.objects.filter(user_id = request.user.id, 
                                        date__lt=datetime.datetime.today()).order_by('-date', '-time')

    next_visits = change_doctor_info(next_visits)
    today_visits = change_doctor_info(today_visits)
    past_visits = change_doctor_info(past_visits)

    return render(request, 'patient/my_visits.html', {'next_visits':next_visits, 'past_visits':past_visits, 'today_visits':today_visits})

@login_required(login_url='home.html')
def new_visit(request):
    doctors = User.objects.filter(groups__name='Doctor_perm')
    profiles =  Profile.objects.filter(is_doctor = True)
    return render(request, 'patient/new_visit.html', {'doctors':doctors, 'profiles':profiles})

@login_required(login_url='home.html')
def select_time(request, id):
    if request.method == 'POST':

        booking = request.POST.get('booking').split(',')

        _date = booking[0].split('-')
        date = datetime.date(int(_date[0]), int(_date[1]), int(_date[2]))

        _time = booking[1].split(':')
        time = datetime.time(int(_time[0]), int(_time[1]))

        visit = Visit.objects.filter(doctor = id, date = date, time = time)
        if visit.exists():
            messages.error(request, 'Visit aslready taken, book another time!')
            return redirect(f'/new-visit/{id}')

        _mutable = request.POST._mutable
        request.POST._mutable = True
        request.POST['user_id'] = request.user.id
        request.POST['doctor'] = id
        request.POST['time'] = time
        request.POST['date'] = date
        request.POST._mutable = _mutable
        form = VisitForm(request.POST)
        print(request.POST)
        if form.is_valid():
            visit = form.save()
            messages.success(request, 'Visit booked succesfullty!')
            return redirect('/my-visits')
    elif request.method == 'GET':
        visits = Visit.objects.filter(doctor = id, date__gte=datetime.datetime.today())
        booked_time = []
        for vis in visits:
            vis.time = vis.time.strftime('%H:%M')
            booked_time.append(f'{vis.date}{vis.time}')
        
        working_time = WORKING_TIME.copy()
        title = [(datetime.datetime.today() + datetime.timedelta(days=i)).strftime('%A %Y-%m-%d') for i in range(7)]
        date = [(datetime.datetime.today() + datetime.timedelta(days=i)).strftime('%Y-%m-%d') for i in range(7)]
        return render(request, 'patient/select_time.html', {'visits':visits, 'working_time':working_time, 'title':title, 'date':date, 'booked_time':booked_time})
    return redirect('/new-visit')

WORKING_TIME=['08:00', '08:30',
            '09:00', '09:30',
            '10:00', '10:30',
            '11:00', '11:30',
            '12:00', '12:30',
            '13:00', '13:30',
            '14:00', '14:30',
            '15:00', '15:30',
            '16:00', '16:30',
            '17:00', '17:30']

def change_doctor_info(visits):
    for v in visits:
        v.doctor = User.objects.filter(id = v.doctor)
        v.doctor = v.doctor[0]
    return visits
#endregion

# profil - pakiet?, recepty json, sms, 
# lekarz ustawia swoje godzinki + urlopy




