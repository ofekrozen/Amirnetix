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
    if request.user.is_authenticated:
        user = request.user # Keep user variable as it's used below
        for simulator in all_simulators:
            if simulator.get_last_attempt(user) is not None:
                all_simulator_attempts.append({'simulator' : simulator, 'last_attempt' : simulator.get_last_attempt(user)})
            else:
                all_simulator_attempts.append({'simulator' : simulator})
        return render(request,'Simulator/index.html', {
            'all_simulators' : all_simulator_attempts
        })
    # For unauthenticated users, or if you want to show simulators without attempt data
    # You might want to adjust this part based on desired behavior for unauthenticated users
    # For now, it will render with an empty all_simulator_attempts if user is not authenticated
    return render(request,'Simulator/index.html',{
        'all_simulators' : Simulator.objects.exclude(id__in = simulators_to_exclude) # Pass simulators directly
    })

def start_simulator(request,simulator_id : int):
    simulator = Simulator.objects.get(id=int(simulator_id))
    if request.user.is_authenticated:
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
        for key,value in request.POST.items():
            if key.strip() == "user_answers":
                answer_dict = json.loads(value)
            elif key.strip() == "answer_times":
                times_dict = json.loads(value)
            elif key.strip() == "attempt_id" and request.user.is_authenticated:
                try:
                    attempt = SimulatorAttempt.objects.get(user=request.user, id=int(value.strip()))
                except SimulatorAttempt.DoesNotExist:
                    # Handle error appropriately, e.g., log it, return an error response, or redirect
                    # For now, let's assume redirecting to simulator_list if attempt not found
                    return redirect('simulator_list') # Or an error page

        if not attempt: # If attempt couldn't be fetched or wasn't set
            # Handle cases where attempt_id wasn't found or user not authenticated properly
            return redirect('simulator_list') # Or an error page

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
        # Ensure user owns the attempt before deleting, or is superuser
        attempt_to_delete = SimulatorAttempt.objects.filter(id=attempt_id, user=request.user).first()
        if attempt_to_delete:
            attempt_to_delete.delete()
        # else: handle case where user tries to delete an attempt not belonging to them, or non-existent
    return redirect('simulator_list')