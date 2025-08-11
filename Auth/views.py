from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import AuthenticationForm
from .forms import CustomUserCreationForm, CustomLoginForm
from django.contrib.auth import logout
from Management.models import Student_Word_Knowledge, Word
from Simulator.models import SimulatorAttempt

def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        print(form.errors)
        if form.is_valid():
            print("form is valid")
            user = form.save()
            return render(request,'Auth/login.html',{'form' : form})
            # login(request, user)  # Log the user in after registration
            # return redirect('home')
        else:
            return render(request, 'Auth/register.html', {'form': form, "alert" : form.errors})
    
    form = CustomUserCreationForm()
    return render(request, 'Auth/register.html', {'form': form})


def login_view(request):
    if request.method == 'POST':
        form = CustomLoginForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('home')
    else:
        form = CustomLoginForm()
    
    return render(request, 'Auth/login.html', {'form': form})


def logout_view(request):
    logout(request)
    return redirect('login')

# Create your views here.

def index(request):
    user = request.user
    if user.is_authenticated:
        selected_words = Student_Word_Knowledge.objects.filter(student=user).all()
        fam_counts = {"perfect": 0,"partially": 0,"not_at_all": 0}
        level_stats = {}
        for stud_word in selected_words:
            if not stud_word.word.word_level in (level_stats.keys()):
                level_stats[stud_word.word.word_level] = {"perfect":0, "partially":0, "not_at_all":0}
            if stud_word.familiarity == 1:
                level_stats[stud_word.word.word_level]["perfect"] += 1
                fam_counts["perfect"] += 1
            elif stud_word.familiarity == 2:
                level_stats[stud_word.word.word_level]["partially"] += 1
                fam_counts["partially"] += 1
            elif stud_word.familiarity == 3:
                level_stats[stud_word.word.word_level]["not_at_all"] += 1
                fam_counts["not_at_all"] += 1
        for level in level_stats:
            level_stats[level]["total_in_level"] = Word.objects.filter(word_level=level).count()
        
        context = {
            'user': user,
            'fam_counts': fam_counts,
            'level_stats': level_stats
        }

                # Reorganize data for chart.js
        level_labels = []
        perfect_data = []
        partially_data = []
        not_at_all_data = []

        for level, stats in sorted(level_stats.items()):
            level_labels.append(f"Level {str(level)}")
            perfect_data.append(stats["perfect"])
            partially_data.append(stats["partially"])
            not_at_all_data.append(stats["not_at_all"])

        context.update({
            'level_labels': level_labels,
            'perfect_data': perfect_data,
            'partially_data': partially_data,
            'not_at_all_data': not_at_all_data,
        })

        # Render avarege simulator score
        average_score = 0
        ctr = 0
        for sim_att in SimulatorAttempt.objects.filter(user=user):
            average_score += sim_att.get_success_rate()
            ctr += 1
        if ctr > 0:
            average_score /= ctr
            average_score = str(round(average_score, 2)) + "%"
        else:
            average_score = "עדיין לא ביצעת סימולטור!"
        context['average_score'] = average_score

        return render(request, 'Auth/index.html', context)
    return render(request,'Auth/index.html')