from django.shortcuts import render,redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required, user_passes_test
import json
from Simulator.models import *
from Auth.models import *
from Management.models import *

# Create your views here.
def index(request):
    simulator_attempts = SimulatorAttempt.objects.all()
    return render(request, 'Analysis/index.html',{
        "simulator_attempts" : simulator_attempts
    })

def vocab_home(request):
    user = request.user
    knowledge_data = Student_Word_Knowledge.objects.filter(student=user)
    
    # Total words
    total_words = knowledge_data.count()
    
    # Familiarity levels
    perfect_count = knowledge_data.filter(familiarity=1).count()
    partial_count = knowledge_data.filter(familiarity=2).count()
    not_at_all_count = knowledge_data.filter(familiarity=3).count()
    
    # Percentages
    perfect_percentage = (perfect_count / total_words * 100) if total_words else 0
    partial_percentage = (partial_count / total_words * 100) if total_words else 0
    not_at_all_percentage = (not_at_all_count / total_words * 100) if total_words else 0
    
    context = {
        'total_words': total_words,
        'perfect_count': perfect_count,
        'partial_count': partial_count,
        'not_at_all_count': not_at_all_count,
        'perfect_percentage': round(perfect_percentage, 2),
        'partial_percentage': round(partial_percentage, 2),
        'not_at_all_percentage': round(not_at_all_percentage, 2),
        'words_knowledge': knowledge_data
    }
    return render(request, "Analysis/vocab_home.html", context)

def analyze_simulator(request,simulator_id):
    try:
        simulator_to_analyze = SimulatorAttempt.objects.get(id = int(simulator_id))
        
        answered_chapters = simulator_to_analyze.simulator.chapters.all()
        simulator_attempt = {'simulator':simulator_to_analyze,'chapters':[]}
        for chapter in answered_chapters:
            current_chapter = {'chapter':chapter}
            questions = []
            q_cnt,correct_cnt = (0,0)
            for question in chapter.questions.all():
                q_cnt += 1
                current_question = {'question' : question}
                selected_answer = simulator_to_analyze.get_user_answer(question=question).selected_option
                answers = []
                for answer in question.answer_options.all():
                    current_answer = {'answer' : answer}
                    current_answer['is_correct'] = answer.is_correct
                    current_answer['is_selected'] = True if answer == selected_answer else False
                    correct_cnt += 1 if answer == selected_answer and answer.is_correct else 0
                    answers.append(current_answer)
                current_question['answers'] = answers
                questions.append(current_question)
            current_chapter['questions'] = questions
            current_chapter['q_cnt'] = q_cnt
            current_chapter['correct_cnt'] = correct_cnt
            simulator_attempt['chapters'].append(current_chapter)
        return render(request, 'Analysis/analyze_simulator.html',{
            'simulator_attempt' : simulator_attempt
        })
    except:
        print("unsuccessful")
        return index(request)
    
@login_required(login_url='login')
def english_vocab(request, words_level:int = 1):
    # Get selected level from query parameter
    print(f"Selected words level: {words_level}")
    selected_level = request.GET.get('level')
    if selected_level:
        words = Word.objects.filter(word_level=selected_level).all()
    else:
        words = Word.objects.filter(word_level = words_level).all() # Update to get first level only if no level is selected
    words = Word.objects.filter(word_level = words_level).all()
    
    user = request.user
    if user:
        # user_knowledge1 = Student_Word_Knowledge.objects.filter(student = user, word__word_level = selected_level).all()
        user_knowledge = Student_Word_Knowledge.objects.all()
        words_list = []
        for word in words:
            try:
                familiarity = user_knowledge.order_by('selection_date').filter(word = word, student = user).last().familiarity
                words_list.append({'word':word,'familiarity':familiarity})
            except:
                words_list.append({'word':word,'familiarity':Level_Choices.NOT_CHOSEN})
    else:
        words_list = []
        for word in words:
            words_list.append({'word':word,'familiarity':Level_Choices.NOT_CHOSEN})
    # Get unique word levels for dropdown options
    levels = Word.objects.values_list('word_level', flat=True).distinct().order_by('word_level')
    fam_levels = []
    for fam_level in Level_Choices.choices:
        if fam_level[0] != 0:
            fam_levels.append(fam_level)
    
    return render(request, 'Analysis/english_vocab.html', {
        'words': words,
        'levels': levels,
        'selected_level': words_level,
        'words_list' : words_list,
        'fam_levels' : fam_levels
    })


@csrf_exempt
@login_required(login_url='login')
def update_familiarity(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            word_id = data.get('word_id')
            fam_level_symbol = data.get('fam_level')
            user = request.user

            # Update the word's familiarity level in the database
            word = Word.objects.get(id=word_id)
            
            try:
                word_fam = Student_Word_Knowledge.objects.get(student = user, word = word)
                word_fam.familiarity = Level_Choices.choices[int(fam_level_symbol)][0]
                word_fam.save()
                print(f"Updated Familiarity level!\nFamiliarity: {word_fam}")
            except:
                word_fam = Student_Word_Knowledge.objects.create(student = user, word=word, familiarity = Level_Choices.choices[int(fam_level_symbol)][0])
                print(f"Created Familiarity level!\nFamiliarity: {word_fam}")
                
            

            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=400)

    return JsonResponse({'success': False, 'error': 'Invalid request'}, status=400)