import openai
# from models import *
from dotenv import load_dotenv
import json
import os
from Simulator.models import *

load_dotenv(override=True)
client = openai.OpenAI(api_key = os.getenv('OPENAI_API_KEY'))


def Generate_Sentence_Completion_Chapter():
    sc_irrelevant_answer_lst = AnswerOption.objects.filter(question__chapter__chapter_type = 'SC', is_correct = True).all()
    irrelevant_words = []
    for answer in sc_irrelevant_answer_lst:
        irrelevant_words.append(answer.description)
    messages = [
        {'role' : 'system', 'content' : '''
            You're an experienced English teacher, a master in enriching student's vocabulary in a short period of time.
         ''',
         },
         {
             'role' : 'user', 'content' : f'''
                Generate four Sentence Completion questions focuses on enriching vocabulary with common and important English words.
                The missing words should be different than all of the following words: {irrelevant_words}
             '''
         },
         {
             'role' : 'assistant',
             'content' : '''
                The output should be in a JSON array format without any additional characters, including a question and four options for answers. The missing word is marked by: ___.
                The sentences should be based on real life facts. The correct answer must be clearly the correct option.
                The format should look like this:
                [
                {"q" : (generated question),
                "a1" : (1st generated answer),
                "a2" : (2nd generated answer),
                "a3" : (3rd generated answer),
                "a4" : (4th generated answer),
                "c" : (the number of the correct answer)
                },
                ...
                ]
             '''
         }
    ]
    response = client.chat.completions.create(
        model = "gpt-3.5-turbo-1106",
        messages = messages,
        temperature = 0.7
    )
    
    try:
        questions = json.loads(response.choices[0].message.content)
        return {"questions" : questions}
    except json.JSONDecodeError:
        # If parsing fails, return a message with the raw text
        return {"error": "Failed to parse response", "response": response.choices[0].message.content}

def Generate_Reading_Comprehension_Chapter():
    messages = [
        {'role' : 'system', 'content' : '''
            You're an English level tester, who knows to generate texts and questions about real subjects in order to test student's English level.
         ''',
         },
         {
             'role' : 'user', 'content' : '''
                Generate a text about a random subject in English.
             '''
         },
         {
             'role' : 'assistant',
             'content' : '''
                The text should not have a title. The text should consist of clear paragraphs. The text should only consist of between 15 to 25 written lines.
                Generate the text only according to these instructions. Avoid using any additional characters that are not part of the text, not even an opening and ending messages to the user.
             '''
         }
    ]
    response = client.chat.completions.create(
        model = "gpt-3.5-turbo",
        messages = messages,
        temperature = 0.7
    )

    generated_text = response.choices[0].message.content

    messages[0]['content'] = '''
        You're an English teacher, who knows to check student's understanding of a text.
    '''
    messages[1]['content'] = f'''
        {generated_text}
        Generate five Reading Comprehension questions to measure the user's understanding of the above text.
    '''
    messages[2]['content'] = '''
        The output should be in a JSON array format without any additional characters.
        Use both specific and general questions: specific questions - trying to check if the student manages to understand the particular reffered sentence/word in the text, general questions - Trying to check if the student manages to fully understand the text as a hole.
        Here's an example for the format:
        [{
            'q' : (your generated question),
            'a1' : (1st generated answer),
            'a2' : (2nd generated answer),
            'a3' : (3rd generated answer),
            'a4' : (4th generated answer),
            'c' : (the number of the correct answer)
        },...
        ]
    '''
    
    response = client.chat.completions.create(
        model = "gpt-3.5-turbo-1106",
        messages = messages,
        temperature = 0.7
    )
    
    try:
        question_lst = json.loads(response.choices[0].message.content)
    except json.JSONDecodeError:
        # If parsing fails, return a message with the raw text
        question_lst = {"error": "Failed to parse response", "response": response.choices[0].message.content}
    
    reading_comprehension_chapter = {
        'text' : generated_text,
        'questions' : question_lst
    }

    return reading_comprehension_chapter

def Generate_Restatement_Chapter():
    messages = [
        {'role' : 'system', 'content' : '''
            You're an English level tester for the academy.
         '''
         },
         {
             'role' : 'user', 'content' : '''
                Generate 3 Restatement questions according to the assistant's instructions.
             '''
         },
         {
             'role' : 'assistant',
             'content' : '''
                The restatement questions should be formatted in a JSON array format without any additional characters. 
                A Restatement question is a statement in an academic level of English, made of a sophisticated sentence or two, about a random subject, and the answer options are statements that potentially could replace the original statement.
                The correct answer should replace the statement perfectly by it's meaning. One other answer option should be close, and the two other answer options should not be close. Here's an example for the format:
                [{
                'q' : (The generated phrase to restate),
                'a1' : (1st option of answer),
                'a2' : (2nd option of answer),
                'a3' : (3rd option of answer),
                'a4' : (4th option of answer),
                'c' : (the number of the correct answer)
                },
                ...]
             '''
         }
    ]

    response = client.chat.completions.create(
        model = "gpt-3.5-turbo-1106",
        messages = messages,
        temperature = 0.7
    )

    try:
        questions = json.loads(response.choices[0].message.content)
        return {"questions" : questions}
    except json.JSONDecodeError:
        # If parsing fails, return a message with the raw text
        return {"error": "Failed to parse response", "response": response.choices[0].message.content}