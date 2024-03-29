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

# region FOR ALL


def home(request):
    all_posts = Post.objects.order_by("-date_created")
    if request.method == "POST":
        post_id = request.POST.get("detele_post_id")
        post = Post.objects.filter(id=post_id).first()
        if post:
            post.delete()

    return render(request, "home.html", {"all_posts": all_posts})


def sign_up(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)
        profile_form = ProfileForm()
        if form.is_valid():
            user = form.save()
            Profile.objects.create(user=user)
            login(request, user)
            return redirect("/home")
    else:
        form = RegisterForm()

    return render(request, "registration/sign_up.html", {"form": form})


# endregion

# region DOCTOR


def is_doctor(user):
    profile = Profile.objects.get(user=user)
    return profile.is_doctor


@user_passes_test(is_doctor)
@login_required(login_url="home.html")
def patient_profile(request, id):
    user = User.objects.get(id=id)
    profile = Profile.objects.get(user=user)

    next_visits = Visit.objects.filter(
        user=user, date__gte=datetime.datetime.today()
    ).order_by("-date", "-time")
    past_visits = Visit.objects.filter(
        user=user, date__lt=datetime.datetime.today()
    ).order_by("-date", "-time")

    return render(
        request,
        "doctor/patient-profile.html",
        {
            "user": user,
            "profile": profile,
            "past_visits": past_visits,
            "next_visits": next_visits,
        },
    )


@login_required(login_url="home.html")
@user_passes_test(is_doctor)
def create_post(request):
    if request.method == "POST":
        form = PostForm(request.POST)
        if form.is_valid():
            post = form.save()
            return redirect("/home")
    else:
        form = PostForm()

    return render(request, "doctor/create_post.html", {"form": form})


@login_required(login_url="home.html")
@user_passes_test(is_doctor)
def patients(request):
    profiles = Profile.objects.filter(is_doctor=False)
    users = []
    for prof in profiles:
        users.append(prof.user)

    return render(request, "doctor/patients.html", {"users": users})


@login_required(login_url="home.html")
@user_passes_test(is_doctor)
def schedule(request):
    if request.method == "POST":
        date = request.POST.get("date")
        visits = Visit.objects.filter(doctor=request.user, date=date).order_by("-time")
        return render(request, "doctor/schedule.html", {"date": date, "visits": visits})
    else:
        date = datetime.date.today().strftime("%Y-%m-%d")
        visits = Visit.objects.filter(doctor=request.user, date=date).order_by("date")
        return render(
            request,
            "doctor/schedule.html",
            {"date": date, "visits": visits, "default": True},
        )


# endregion

# region PATIENT


@login_required(login_url="home.html")
def my_profile(request):
    profile = Profile.objects.get(user=request.user)
    if request.method == "POST":
        data = request.POST
        if data.get("email") != "":
            user = User.objects.get(id=request.user.id)
            user.email = data.get("email")
            user.save()

        profile.tel = data.get("tel") if data.get("tel") != "" else profile.tel

        if profile.is_doctor:
            profile.spec = data.get("spec") if data.get("spec") != "" else profile.spec
            profile.desc = data.get("desc") if data.get("desc") != "" else profile.desc
        else:
            profile.pesel = (
                data.get("pesel") if data.get("pesel") != "" else profile.pesel
            )
            profile.city = data.get("city") if data.get("city") != "" else profile.city
            profile.zip_code = (
                data.get("zip_code") if data.get("zip_code") != "" else profile.zip_code
            )
            profile.street = (
                data.get("street") if data.get("street") != "" else profile.street
            )
            profile.addr_number = data.get("addr_number")
        profile.save()
        messages.success(request, "Profile updated!")
        return redirect("/my-profile")
    return render(request, "my-profile.html", {"profile": profile})


@login_required(login_url="home.html")
def my_visits(request):
    next_visits = Visit.objects.filter(
        user=request.user, date__gt=datetime.datetime.today()
    ).order_by("-date", "-time")
    today_visits = Visit.objects.filter(
        user=request.user, date=datetime.datetime.today()
    ).order_by("-time")
    past_visits = Visit.objects.filter(
        user=request.user, date__lt=datetime.datetime.today()
    ).order_by("-date", "-time")

    return render(
        request,
        "patient/my_visits.html",
        {
            "next_visits": next_visits,
            "past_visits": past_visits,
            "today_visits": today_visits,
        },
    )


@login_required(login_url="home.html")
def delete_visit(request, id):
    visit = Visit.objects.get(id=id)
    if visit:
        if request.user == visit.user:
            visit.delete()
            messages.success(request, "Visit deleted")
    else:
        messages.error(request, "There was a problem deleting a visit")
    return redirect("/my-visits")


@login_required(login_url="home.html")
def new_visit(request):
    # doctors = User.objects.filter(groups__name='Doctor_perm')
    profiles = Profile.objects.filter(is_doctor=True)
    doctors = []
    for prof in profiles:
        doctors.append(prof.user)
    return render(
        request, "patient/new_visit.html", {"doctors": doctors, "profiles": profiles}
    )


@login_required(login_url="home.html")
def select_time(request, id):
    doctor = User.objects.get(id=id)
    if request.method == "POST":
        booking = request.POST.get("booking").split(",")

        _date = booking[0].split("-")
        date = datetime.date(int(_date[0]), int(_date[1]), int(_date[2]))

        _time = booking[1].split(":")
        time = datetime.time(int(_time[0]), int(_time[1]))

        visit = Visit.objects.filter(doctor=doctor, date=date, time=time)
        if visit.exists():
            messages.error(request, "Visit aslready taken, book another time!")
            return redirect(f"/new-visit/{id}")

        _mutable = request.POST._mutable
        request.POST._mutable = True
        request.POST["user"] = request.user
        request.POST["doctor"] = doctor
        request.POST["time"] = time
        request.POST["date"] = date
        request.POST._mutable = _mutable
        form = VisitForm(request.POST)
        if form.is_valid():
            visit = form.save()
            messages.success(request, "Visit booked succesfullty!")
            return redirect("/my-visits")
    elif request.method == "GET":
        visits = Visit.objects.filter(
            doctor=doctor, date__gte=datetime.datetime.today()
        )

        booked_time, weekend = get_booked_time(visits)

        working_time = WORKING_TIME.copy()

        title = [
            (datetime.datetime.today() + datetime.timedelta(days=i)).strftime(
                "%A %Y-%m-%d"
            )
            for i in range(7)
        ]
        date = [
            (datetime.datetime.today() + datetime.timedelta(days=i)).strftime(
                "%Y-%m-%d"
            )
            for i in range(7)
        ]

        context = {
            "visits": visits,
            "working_time": working_time,
            "title": title,
            "date": date,
            "booked_time": booked_time,
            "weekend": weekend,
        }

        return render(request, "patient/select_time.html", context)
    return redirect("/new-visit")


def get_booked_time(visits):
    booked_time = []
    weekday = []
    weekend = []
    for vis in visits:
        vis.time = vis.time.strftime("%H:%M")
        booked_time.append(f"{vis.date}{vis.time}")
    days = [(datetime.datetime.today() + datetime.timedelta(days=i)) for i in range(7)]
    for day in days:
        if day.weekday() > 4:
            weekday.append(day.strftime("%Y-%m-%d"))
    for day in weekday:
        for t in WORKING_TIME:
            weekend.append(f"{day}{t}")
    return booked_time, weekend


@login_required(login_url="home.html")
def doctor_profile(request, id):
    doctor = User.objects.get(id=id)
    profile = Profile.objects.get(user=doctor)

    my_visits = Visit.objects.filter(
        user=request.user, doctor=doctor, date__gte=datetime.datetime.today()
    ).order_by("-date", "-time")

    return render(
        request,
        "patient/doctor_profile.html",
        {"doctor": doctor, "profile": profile, "my_visits": my_visits},
    )


@login_required(login_url="home.html")
def doctors(request):
    # doctors = User.objects.filter(groups__name='Doctor_perm')
    profiles = Profile.objects.filter(is_doctor=True)
    doctors = []
    for prof in profiles:
        doctors.append(prof.user)
    return render(
        request, "patient/doctors.html", {"doctors": doctors, "profiles": profiles}
    )


# endregion


# region CHAT
@login_required(login_url="home.html")
def create_chat(request, id):
    doctor = User.objects.get(id=id)
    try:
        chat = Chat.objects.get(user=request.user, doctor=doctor)
    except Exception as e:
        print(e)
        Chat.objects.create(user=request.user, doctor=doctor)
        chat = Chat.objects.get(user=request.user, doctor=doctor)
    return redirect(f"/chat/{chat.id}")


@login_required(login_url="home.html")
def chat(request, id):
    chat = Chat.objects.get(id=id)
    if request.method == "GET":
        msgs = Message.objects.filter(chat=chat)
        print(msgs)
        return render(request, "chat.html", {"messages": msgs})
    if request.method == "POST":
        msg = request.POST.get("message")
        if len(msg) > 1:
            Message.objects.create(chat=chat, author=request.user, text=msg)
        print(request.POST)
        return redirect(f"/chat/{id}")


@login_required(login_url="home.html")
def chat_list(request):
    chats = Chat.objects.filter(user=request.user)
    if not chats:
        chats = Chat.objects.filter(doctor=request.user)
    return render(request, "chat-list.html", {"chats": chats})


# endregion

WORKING_TIME = [
    "08:00",
    "08:30",
    "09:00",
    "09:30",
    "10:00",
    "10:30",
    "11:00",
    "11:30",
    "12:00",
    "12:30",
    "13:00",
    "13:30",
    "14:00",
    "14:30",
    "15:00",
    "15:30",
    "16:00",
    "16:30",
    "17:00",
    "17:30",
]

# profil - pakiet?, recepty json, sms,
# lekarz ustawia swoje godzinki + urlopy
# wejście na profile lekarza + wystawienie opini z ocenką i komentarzem
# powiadomienia że lekarz odpisał i o nowej opini na swój temat
# podgląd ostatniej wiadomości w zakłądce 'chats'
