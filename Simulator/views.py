from django.shortcuts import render,redirect
# import Amirnetix.prompts as prompts
import json
import datetime
from .models import *

# Create your views here.

def index(request):
    simulators_to_exclude = Get_SimulatorsIds_To_Exclude()
    simulators_to_exclude.append(6)
    all_simulators = Simulator.objects.exclude(id__in = simulators_to_exclude)
    all_simulator_attempts = []
    user = request.user
    if user is not None:
        for simulator in all_simulators:
            if simulator.get_last_attempt(user) is not None:
                all_simulator_attempts.append({'simulator' : simulator, 'last_attempt' : simulator.get_last_attempt(user)})
            else:
                print(f"simulator: {simulator}")
                print(f"last_attempt: {simulator.get_last_attempt(user)}")
                all_simulator_attempts.append({'simulator' : simulator})
        print(all_simulator_attempts)
        return render(request,'Simulator/index.html', {
            'all_simulators' : all_simulator_attempts
        })
    return render(request,'Simulator/index.html',{
        'all_simulators' : all_simulator_attempts
    })

def start_simulator(request,simulator_id : int):
    simulator = Simulator.objects.get(id=int(simulator_id))
    if request.user:
        simulator_attempt = SimulatorAttempt.objects.create(user = request.user,simulator = simulator)
        return render(request,'Simulator/simulator.html',{
            'simulator' : simulator,
            'simulator_attempt' : simulator_attempt
        })
    return render(request,'Simulator/simulator.html',{
        'simulator' : simulator,
        })

def finish_simulator(request):
    if request.method == "POST":
        user = request.user
        answer_dict = None
        times_dict = None
        attempt = None
        finish_time = datetime.now()
        fictive_simulator = Simulator.objects.update_or_create(id = 0, name = "fictive simulator")
        fictive_simulator = Simulator.objects.get(id = 0)
        fictive_chapter = Chapter.objects.update_or_create(id = 0, simulator = fictive_simulator, order = 1, chapter_type = 'OT', title = "Fictive Chapter", time_limit = 1)
        fictive_chapter = Chapter.objects.get(id = 0)
        fictive_question = Question.objects.update_or_create(id = 0, chapter = fictive_chapter, order = 1, description = "Fictive Question")
        fictive_question = Question.objects.get(id = 0)
        fictive_answer = AnswerOption.objects.update_or_create(id=0, question = fictive_question, order = 1, description = "Fictive Answer", is_correct = False)
        for key,value in request.POST.items():
            if key.strip() == "user_answers":
                answer_dict = json.loads(value)
            elif key.strip() == "answer_times":
                times_dict = json.loads(value)
            elif key.strip() == "attempt_id" and user is not None:
                attempt = SimulatorAttempt.objects.get(user = user,id = int(value.strip()))
        attempt.end_time = finish_time
        attempt.save()
        if answer_dict is not None:
            for key in answer_dict:
                answered_question = Question.objects.get(id = int(key))
                selected_answer = AnswerOption.objects.get(id = int(answer_dict[key]))
                if times_dict[key] > 0:
                    time_answered = datetime.fromtimestamp(int(times_dict[key])/1000)
                else:
                    time_answered = finish_time
                UserAnswer.objects.create(user = user, simulator_attempt = attempt, question = answered_question, selected_option = selected_answer, timestamp = time_answered )
    return redirect('simulator_list')

def Get_SimulatorsIds_To_Exclude() -> list:
    return [-1,0]

def exit_simulator(request, attempt_id: int):
    if request.method == "POST":
        SimulatorAttempt.objects.get(id = attempt_id).delete()
    return redirect('/Simulator')