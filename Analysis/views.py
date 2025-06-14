from django.shortcuts import render,redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required, user_passes_test
import json
from Simulator.models import *
from Auth.models import *
from Management.models import * # Level_Choices should be here
from django.shortcuts import get_object_or_404

# Create your views here.
def index(request):
    simulator_attempts = SimulatorAttempt.objects.all()
    return render(request, 'Analysis/index.html',{
        "simulator_attempts" : simulator_attempts
    })

@login_required(login_url='login')
def vocab_home(request):
    if request.user.is_authenticated:
        user = request.user # Keep user for existing logic
        knowledge_data = Student_Word_Knowledge.objects.filter(student=user)
    else:
        # Handle case for unauthenticated user if necessary, or rely on @login_required
        knowledge_data = Student_Word_Knowledge.objects.none()

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

def analyze_simulator(request, attempt_id):
    simulator_to_analyze = get_object_or_404(SimulatorAttempt, id=int(attempt_id))

    answered_chapters = simulator_to_analyze.simulator.chapters.all()
    simulator_analysis_data = {'simulator_attempt': simulator_to_analyze, 'chapters': []} # Changed key name for clarity
    for chapter in answered_chapters:
        current_chapter_dict = {'chapter': chapter}
        questions_data = []
        chapter_q_count = 0
        chapter_correct_count = 0
        for question in chapter.questions.all():
            chapter_q_count += 1
            current_question_dict = {'question': question}
            user_answer_obj = simulator_to_analyze.get_user_answer(question=question)
            selected_answer_obj = user_answer_obj.selected_option if user_answer_obj else None

            is_question_correct = False
            if selected_answer_obj and selected_answer_obj.is_correct:
                chapter_correct_count += 1
                is_question_correct = True
            current_question_dict['is_user_correct'] = is_question_correct

            answers_data = []
            for answer_option in question.answer_options.all():
                current_answer_dict = {'answer': answer_option}
                current_answer_dict['is_correct'] = answer_option.is_correct
                current_answer_dict['is_selected'] = (answer_option == selected_answer_obj)
                answers_data.append(current_answer_dict)
            current_question_dict['answers'] = answers_data
            questions_data.append(current_question_dict)
        current_chapter_dict['questions'] = questions_data
        current_chapter_dict['q_cnt'] = chapter_q_count
        current_chapter_dict['correct_cnt'] = chapter_correct_count
        simulator_analysis_data['chapters'].append(current_chapter_dict)

    return render(request, 'Analysis/analyze_simulator.html',{
        'simulator_analysis_data' : simulator_analysis_data # Pass the new data structure
    })

@login_required(login_url='login')
def english_vocab(request):
    # Get selected level from query parameter
    selected_level = request.GET.get('level')
    if selected_level:
        words = Word.objects.filter(word_level=selected_level).all()
    else:
        words = Word.objects.all() # This is a queryset of Word objects
    
    if request.user.is_authenticated:
        user_knowledge_map = {
            swk.word_id: swk.familiarity
            for swk in Student_Word_Knowledge.objects.filter(student=request.user).select_related('word')
        }
        words_list = []
        for word_obj in words: # Iterate over the queryset
            familiarity = user_knowledge_map.get(word_obj.id, Level_Choices.NOT_CHOSEN)
            words_list.append({'word': word_obj, 'familiarity': familiarity})
    else:
        # Should not happen due to @login_required, but as a fallback:
        words_list = []
        for word_obj in words:
            words_list.append({'word': word_obj, 'familiarity': Level_Choices.NOT_CHOSEN})

    # Get unique word levels for dropdown options
    levels = Word.objects.values_list('word_level', flat=True).distinct().order_by('word_level')
    fam_levels = []
    for fam_level in Level_Choices.choices:
        if fam_level[0] != 0:
            fam_levels.append(fam_level)
    
    return render(request, 'Analysis/english_vocab.html', {
        'words': words,
        'levels': levels,
        'selected_level': selected_level,
        'words_list' : words_list,
        'fam_levels' : fam_levels
    })

# @csrf_exempt # Removed, ensure CSRF token is sent by AJAX
@login_required(login_url='login')
def update_familiarity(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            word_id = data.get('word_id')
            fam_level_input = data.get('fam_level') # Assuming this is the integer value of the choice
            user = request.user

            # Validate fam_level_input (ensure it's a valid choice in Level_Choices)
            valid_familiarity_levels = [choice[0] for choice in Level_Choices.choices]
            if int(fam_level_input) not in valid_familiarity_levels:
                return JsonResponse({'success': False, 'error': 'Invalid familiarity level'}, status=400)

            word = get_object_or_404(Word, id=word_id) # Use get_object_or_404 for Word
            
            word_fam, created = Student_Word_Knowledge.objects.update_or_create(
                student=user,
                word=word,
                defaults={'familiarity': int(fam_level_input)}
            )
            
            # Optionally, log if it was created or updated
            # action_taken = "Created" if created else "Updated"
            # print(f"{action_taken} Familiarity level! Familiarity: {word_fam}")

            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=400)

    return JsonResponse({'success': False, 'error': 'Invalid request'}, status=400)