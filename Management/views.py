from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.http import JsonResponse
from Simulator.models import *
from .models import Word,Word_Form
import Amirnetix.prompts as prompts
from deep_translator import GoogleTranslator
import pandas as pd

# Create your views here.

def index(request):
    try:
        simulators = Simulator.objects.all()
        return render(request,'Management/index.html',{
            'simulators' : simulators
        })
    except:
        return render(request,'Management/index.html')

def edit_test(request, simulator_id = None):
    if simulator_id is None:
        return render(request, 'Management/edit_test.html')
    else:
        simulator_to_edit = Simulator.objects.get(id = simulator_id)
        return render(request, 'Management/edit_test.html', {
            'existing_simulator' : simulator_to_edit
        })

@user_passes_test(lambda u: u.is_superuser, login_url='login')
def generate_test(request):
    if request.method == "POST":
        try:
            last_simulator_id = Simulator.objects.all().last().id
            simulator = Simulator(name = f"Simulator number {last_simulator_id + 1}", description="mixed level Simulator")
        except:
            simulator = Simulator(name = f"First Simulator", description="mixed level Simulator")

        test = []
        for i in range(1,7,1):
            order = i
            current_chapter = {'order' : order, 'questions' : []}
            this_chapter_object = None
            chapter_json_lst = None
            chapter_type = None
            title = ""
            time_limit = 0
            if i in (1,2,6):
                chapter_type = ChapterType.SENTENCE_COMPLETION
                title = f"{chapter_type} - {i}"
                time_limit = 4
                this_chapter_object = Chapter(simulator = simulator, order = order,chapter_type = chapter_type, title = title, time_limit = time_limit)
                chapter_json_lst = prompts.Generate_Sentence_Completion_Chapter()
                
            elif i == 3:
                chapter_type = ChapterType.READING_COMPREHENSION
                title = f"{chapter_type} - {i}"
                time_limit = 15
                this_chapter_object = Chapter(simulator = simulator, order = order,chapter_type = chapter_type, title = title, time_limit = time_limit)
                chapter_json_lst = prompts.Generate_Reading_Comprehension_Chapter()
                current_chapter['text'] = chapter_json_lst['text']
                current_chapter['heb_text'] = translate_text(current_chapter['text'])
            elif i in (4,5):
                chapter_type = ChapterType.RESTATEMENT
                title = f"{chapter_type} - {i}"
                time_limit = 6
                this_chapter_object = Chapter(simulator = simulator, order = order,chapter_type = chapter_type, title = title, time_limit = time_limit)
                chapter_json_lst = prompts.Generate_Restatement_Chapter()
            
            question_order = 0
            for question in chapter_json_lst['questions']:
                    question_order += 1
                    question_desc = ""
                    current_question = None
                    answers = []
                    for key in question:
                        if key == "q":
                            question_desc = question[key]
                            heb_question_desc = translate_text(question_desc)
                            current_question = Question(chapter = this_chapter_object,order = question_order, description = question_desc,hebrew_desc=heb_question_desc)
                        elif key.startswith('a'):
                            answer_order = int(key[-1])
                            answer_desc = question[key]
                            heb_answer_desc = translate_text(answer_desc)
                            if key.endswith(str(question['c'])):
                                is_correct = True
                            else:
                                is_correct = False
                            currect_answer = AnswerOption(question = current_question, description = answer_desc, hebrew_desc = heb_answer_desc, order = answer_order, is_correct = is_correct)
                            answers.append(currect_answer)
                    current_chapter['questions'].append({'order' : question_order, 'question' : current_question, 'answers' : answers})

            current_chapter['type'] = chapter_type
            test.append(current_chapter)

        return render(request, 'Management/edit_test.html', {
            'new_simulator' : test
        })
    
    return render(request, 'Management/index.html')

def upload_words(request, list_type:str):
    existing_words = [w.eng_word for w in Word.objects.all()]
    existing_word_forms = [w.eng_word for w in Word_Form.objects.all()]
    if list_type == "AWL":
        awl_df = pd.read_excel(r'Amirnetix\academic_word_list.xlsx')
        for i,row in awl_df.iterrows():
            root = row['Headword']
            related_words = str(row['Related word forms']) if str(row['Related word forms']).lower() != "nan" else None
            if root not in existing_words:
                root_word = Word.objects.create(eng_word = root, heb_word = heb_trans, is_root = True, sublist = sublist, word_level = sublist)
                heb_trans = root_word.heb_word
                sublist = root_word.sublist
                print(f"created the root: {root_word}")
            else:
                root_word = Word.objects.get(eng_word = root)
                heb_trans = translate_text(root)
                sublist = row['Sublist']
                root_word.word_level = sublist
                root_word.source = "AWL"
                root_word.save()
            if related_words is not None:
                for sub_word in related_words.split(','):
                    word_form_eng = sub_word
                    if sub_word not in existing_word_forms:
                        heb_trans = translate_text(word_form_eng)
                        word_form = Word_Form.objects.create(root_word = root_word, eng_word = word_form_eng, heb_word = heb_trans)
                        print(f"successfully created: {word_form}")
    elif list_type == "GSL":
        words_df = pd.read_csv(r'Amirnetix\GSL Words List.csv',header=None)
        cnt = 0
        word_level = 1
        for i,words_list in words_df.iterrows():
            for word in words_list:
                cnt += 1
                if cnt % 200 == 0:
                    word_level += 1
                if word not in existing_words and word not in existing_word_forms:
                    heb_trans = translate_text(word)
                    current_word = Word.objects.create(eng_word = word, heb_word = heb_trans, word_level = word_level)
                    print(f'Created {current_word}')
                else:
                    current_word = Word.objects.get(eng_word = word)
                    current_word.word_level = word_level
                    current_word.source = "GSL"
                    print(current_word)
                    current_word.save()

    
    return redirect(reverse('english_vocab'))

def save_new_simulator(request):
    if request.method == "POST":
        try:
            simulator_number = Simulator.objects.all().count()
            simulator = Simulator.objects.create(name = f"Simulator number {simulator_number + 1}", description="mixed level Simulator")
        except:
            simulator = Simulator.objects.create(name = f"First Simulator", description="mixed level Simulator")
        chapter_type = None
        chapter_text = None
        time_limit = 0
        current_chapter_object = None
        current_question_object = None
        for key,value in request.POST.items():
            if key.strip().startswith('chapter_type'):
                chapter_text = None
                if value.strip() == 'SC':
                    chapter_type = ChapterType.SENTENCE_COMPLETION
                    time_limit = 4
                elif value.strip() == 'RC':
                    chapter_type = ChapterType.READING_COMPREHENSION
                    time_limit = 15
                elif value.strip() == 'RS':
                    chapter_type = ChapterType.RESTATEMENT
                    time_limit = 6
                chapter_order = int(key.strip().split('-')[-1])
                current_chapter_object = Chapter.objects.create(simulator = simulator, order = chapter_order, chapter_type = chapter_type, title = f'{simulator.name} - chapter number {chapter_order} - {chapter_type}', time_limit = time_limit)
            elif key.strip().startswith('text-'):
                chapter_text = value.strip()
                current_chapter_object.reading_text = chapter_text
                simulator.name += " - " + prompts.Generate_Text_Title(chapter_text)
                simulator.save()
                current_chapter_object.save()
            elif key.strip().startswith('hebrew_text-'):
                hebrew_text = value.strip()
                current_chapter_object.hebrew_text = hebrew_text
                current_chapter_object.save()
            elif key.strip().startswith('question-'):
                question_order = int(key.strip().split('-')[-1])
                question_desc = value.strip()
                current_question_object = Question.objects.create(chapter = current_chapter_object, order = question_order, description = question_desc)
            elif key.strip().startswith('heb_question-'):
                hebrew_question_desc = value.strip()
                current_question_object.hebrew_desc = hebrew_question_desc
                current_question_object.save()
            elif key.strip().startswith('answer_desc-'):
                answer_order = int(key.strip().split('-')[-1])
                answer_desc = value.strip()
                current_answer_object = AnswerOption.objects.create(question = current_question_object, order = answer_order, description = answer_desc)
            elif key.strip().startswith('heb_answer_desc-'):
                hebrew_answer_desc = value.strip()
                current_answer_object.hebrew_desc = hebrew_answer_desc
                current_answer_object.save()
            elif key.strip().startswith('is_correct-'):
                current_answer_object.is_correct = True
                current_answer_object.save()
    
    return redirect('index')

def save_edited_simulator(request):
    if request.method == "POST":
        for key,value in request.POST.items():
            input_name = key.strip()
            input_value = value.strip()
            if input_name.startswith('chapter_text'):
                chapter = Chapter.objects.get(id = int(input_name.split('-')[-1]))
                chapter.reading_text = input_value
                chapter.save()
            elif input_name.startswith('heb_chapter_text'):
                chapter = Chapter.objects.get(id = int(input_name.split('-')[-1]))
                chapter.hebrew_text = input_value
                chapter.save()
            elif input_name.startswith('question-'):
                question = Question.objects.get(id = int(input_name.split('-')[-1]))
                question.description = input_value
                question.save()
            elif input_name.startswith('heb_question-'):
                question = Question.objects.get(id = int(input_name.split('-')[-1]))
                question.hebrew_desc = input_value
                question.save()
            elif input_name.startswith('answer_desc-'):
                answer = AnswerOption.objects.get(id = int(input_name.split('-')[-1]))
                answer.description = input_value
                answer.save()
            elif input_name.startswith('heb_answer_desc-'):
                answer = AnswerOption.objects.get(id = int(input_name.split('-')[-1]))
                answer.hebrew_desc = input_value
                answer.save()
            elif input_name.startswith('correct_answer-'):
                question = Question.objects.get(id = int(input_name.split('-')[-1]))
                correct_answer_id = int(input_value)
                for answer in question.answer_options.all():
                    if answer.id == correct_answer_id:
                        answer.is_correct = True
                    else:
                        answer.is_correct = False
                    answer.save()
        print('Edited Simulator was saved successfully!')
    return redirect("index")

### Translate a whole given simulator by id
def add_simulator_heb_translation(request, simulator_id: int):
    simulator = Simulator.objects.get(id = simulator_id)
    simulator_chapters = Chapter.objects.filter(simulator = simulator).all()
    for chapter in simulator_chapters:
        if chapter.reading_text is not None and chapter.hebrew_text is None:
            chapter.hebrew_text = translate_text(chapter.reading_text)
            chapter.save()
        for question in chapter.questions.all():
            if question.hebrew_desc is None:
                question.hebrew_desc = translate_text(question.description)
                question.save()
            for answer in question.answer_options.all():
                if answer.hebrew_desc is None:
                    answer.hebrew_desc = translate_text(answer.description)
                    answer.save()
    return redirect('index')

### Translate a given text ###
def translate_text(text_to_translate:str):
    translated_text = GoogleTranslator(source='en', target='hebrew').translate(text_to_translate)

    print(f"{text_to_translate} -> {translated_text}")
    return translated_text

### Delete Simulator ###
def delete_test(request, simulator_id = None):
    simulators = Simulator.objects.all()
    if simulator_id is None:
        return render(request, 'Management/index.html',{
            'simulators' : simulators,
            'simulator_to_delete' : None
        })
    else:
        simulator_to_delete = Simulator.objects.get(id = simulator_id)
        simulator_name = simulator_to_delete.name
        simulator_to_delete.delete()
        simulators = Simulator.objects.all()
        
        return render(request, 'Management/index.html', {
            'simulators' : simulators,
            'simulator_to_delete' : simulator_name
        })

def create_simulator(request):
    if request.method == 'POST':
        words_ids_list = request.POST.get('selected_words')
        topic = request.POST.get('topic')

        # Process the input or send it to the API
        if not words_ids_list or not topic:
            messages.error(request, "All fields are required.")
        else:
            words_ids_list = words_ids_list.split(",")
            word_object_list = [Word.objects.get(id = word_id) for word_id in words_ids_list]
            test_to_edit = generate_simulator_using_words(word_object_list,topic)
            messages.success(request, "Your request has been sent successfully.")
            print(f"Creating a test with according to:\n{words_ids_list}\ntext topic: {topic}")
            print(f"Generated test:\n{test_to_edit}")
            # **** Create a new Generate Test function! **** #
            return render(request, 'Management/edit_test.html', {
                'new_simulator' : test_to_edit
            })
        return render(request,'Management/index.html')

    return render(request, 'Management/create_simulator.html')

def generate_simulator_using_words (words_list : list[Word], topic: str) -> list:
    try:
            simulator_number = Simulator.objects.all().count()
            simulator = Simulator(name = f"Simulator number {simulator_number + 1}", description="mixed level Simulator")
    except:
            simulator = Simulator(name = f"First Simulator", description="mixed level Simulator")
    
    test = []
    words_list_copy = words_list.copy()
    for i in range(1,7,1):
        try:
            order = i
            current_chapter = {'order' : order, 'questions' : []}
            this_chapter_object = None
            chapter_json_lst = None
            chapter_type = None
            title = ""
            time_limit = 0
            chapter_word_list = []
            if i in (1,2,6):
                chapter_type = ChapterType.SENTENCE_COMPLETION
                title = f"{chapter_type} - {i}"
                time_limit = 4
                # Create a 
                this_chapter_object = Chapter(simulator = simulator, order = order,chapter_type = chapter_type, title = title, time_limit = time_limit)
                for j in (1,2,3,4):
                    chapter_word_list.append(words_list_copy.pop().eng_word)
                chapter_json_lst = prompts.Generate_Sentence_Completion_Chapter(chapter_word_list)
                print(f"Sentence Completions {i}:")
                print(chapter_json_lst['questions'])
            elif i == 3:
                chapter_type = ChapterType.READING_COMPREHENSION
                title = f"{chapter_type} - {i}"
                time_limit = 15
                chapter_json_lst = prompts.Generate_Reading_Comprehension_Chapter(topic)
                print(f"Reading Comprehension {i}:")
                print(chapter_json_lst['questions'])
                simulator.save()
                this_chapter_object = Chapter(simulator = simulator, order = order,chapter_type = chapter_type, title = title, time_limit = time_limit)
                current_chapter['text'] = chapter_json_lst['text']
                current_chapter['hebrew_text'] = translate_text(current_chapter['text'])
            elif i in (4,5):
                    chapter_type = ChapterType.RESTATEMENT
                    title = f"{chapter_type} - {i}"
                    time_limit = 6
                    this_chapter_object = Chapter(simulator = simulator, order = order,chapter_type = chapter_type, title = title, time_limit = time_limit)
                    for j in (1,2,3):
                        chapter_word_list.append(words_list_copy.pop().eng_word)
                    chapter_json_lst = prompts.Generate_Restatement_Chapter(chapter_word_list)
                    print(f"Restatements {i}:")
                    print(chapter_json_lst['questions'])
            question_order = 0
            for question in chapter_json_lst['questions']:
                question_order += 1
                question_desc = ""
                current_question = None
                answers = []
                for key in question:
                    # Add Question translation
                    if key == "q":
                        question_desc = question[key]
                        heb_question_desc = translate_text(question_desc)
                        # Question object to edit (the saving is later in the proccess)
                        current_question = Question(chapter = this_chapter_object,order = question_order, description = question_desc,hebrew_desc=heb_question_desc)
                    # Add Answer Translation
                    elif key.startswith('a'):
                        answer_order = int(key[-1])
                        answer_desc = question[key]
                        heb_answer_desc = translate_text(answer_desc)
                        if key.endswith(str(question['c'])):
                            is_correct = True
                        else:
                            is_correct = False
                        # Answer object to edit (the saving is later in the proccess)
                        currect_answer = AnswerOption(question = current_question, description = answer_desc, hebrew_desc = heb_answer_desc, order = answer_order, is_correct = is_correct)
                        answers.append(currect_answer)
                current_chapter['questions'].append({'order' : question_order, 'question' : current_question, 'answers' : answers})

            current_chapter['type'] = chapter_type
            test.append(current_chapter)
        except:
            print(f"Error generating chapter {i}")
            print(f"Deleting simulator")
            simulator.delete()
            return None
    simulator.delete()
    return test

def fetch_unused_words(request):
    words = Word.objects.exclude(word_level = 1).filter(is_used = False).all()

    search_query = request.GET.get('q', '')
    
    not_used_words = [{"id":word.id,"text":word.eng_word} for word in words]

    if search_query:
        not_used_words = [word for word in not_used_words if search_query.lower() in word["text"].lower()]

    return JsonResponse(not_used_words, safe=False)

### Select only the unused words from a list of words
def unused_words(word_list: list[Word]) -> list[Word]:
    new_words_list = list(Word.objects.filter(is_used = False).all())
    return new_words_list



def select_2(request):
    return render(request, "Management/select_2.html")

def first_100(request):
    first_100_words = Word.objects.filter(word_level = 2).all().order_by('word_level')
    for word in first_100_words:
        print(word)
    return render(request,"Management/index.html")