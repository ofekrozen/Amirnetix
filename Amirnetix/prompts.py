import openai
# from models import *
from dotenv import load_dotenv
import json
import os
from Simulator.models import *

load_dotenv(override=True)
client = openai.OpenAI(api_key = os.getenv('OPENAI_API_KEY'))


def Generate_Sentence_Completion_Chapter(words_list: list[str]):
    # sc_irrelevant_answer_lst = AnswerOption.objects.filter(question__chapter__chapter_type = 'SC', is_correct = True).all()
    # irrelevant_words = []
    # for answer in sc_irrelevant_answer_lst:
    #     irrelevant_words.append(answer.description)
    messages = [
        # You're an experienced English teacher, a master in enriching student's vocabulary in a short period of time,
        #     with a creative mind of creating unique questions.
        {'role' : 'system', 'content' : '''
            You're an experienced question creator for a formal pre-academy English test, that creatively create unique questions
            with the purpose of improving the student's vocabulary.
         ''',
         },
         {
                # The missing words should be different than all of the following words: {irrelevant_words}.
             'role' : 'user', 'content' : f'''
                Generate four Sentence Completion questions focuses on enriching vocabulary with common and important English words.
                The missing words should be within the following words: {words_list}.
             '''
         },
         {
             'role' : 'assistant',
             'content' : '''
                Your goal is to simulate Sentence Completion questions of a pre-academy English test as accurate as possible.
                The input would be a list of words to choose the correct answers from.
                The output should be in a JSON array format without any additional characters, including a question and four options for answers. The missing word is marked by: ___.
                The sentences should be based on real life facts. The correct answer must be clearly the correct option.
                Two IMPORTANT instructions:
                1. The number of the correct answer should differ between each question.
                2. The set of answers should include a correct answer from the given words list, and three other random words that ARE NOT in the given words list.
                
                An IMPORATANT REMINDER: The output should be a text that looks like a Json Array format, without any additional text.
                The format should look exactly like this:
                [
                {
                "q" : (generated question),
                "a1" : (1st generated answer),
                "a2" : (2nd generated answer),
                "a3" : (3rd generated answer),
                "a4" : (4th generated answer),
                "c" : (the number of the correct answer)
                }
                ]

                for example:
                Input: Generate four Sentence Completion questions with the following list of words: flapping, immense, incorporate, vendors.
                Output:
                [
                {
                "q" : "The butterfly fish can leap out of the water and soar thorugh the air, ___ its fins like wings",
                "a1" : "flapping",
                "a2" : "stripping",
                "a3" : "pressing",
                "a4" : "padding",
                "c" : 1
                },
                {
                "q" : "The collection of rare books and manuscripts from Tibet housed in the National Library of Mongolia is ___ , comprising more than a million items",
                "a1" : "accurate",
                "a2" : "urgent",
                "a3" : "immense",
                "a4" : "oral",
                "c" : 3
                },
                {
                "q" : "The compositions of twentieth-century musician John Zorn ___ elements from jazz, klezmer, and punk rock",
                "a1" : "allocate",
                "a2" : "dispatch",
                "a3" : "incorporate",
                "a4" : "verify",
                "c" : 3
                },
                {
                "q" : "In Jerusalem's Machane Yehuda market, over 250 ___ sell everything from fruit and vegetables to clothing and household goods",
                "a1" : "captors",
                "a2" : "aviators",
                "a3" : "janitors",
                "a4" : "vendors",
                "c" : 4
                }
                ]
             '''
         }
    ]
    response = client.chat.completions.create(
        model = "gpt-3.5-turbo-1106",
        messages = messages,
        temperature = 0.7
    )
    response.choices[0].message.content = response.choices[0].message.content.replace("json","")
    response.choices[0].message.content = response.choices[0].message.content.replace("```","")
    print(response.choices[0].message.content)
    try:
        questions = json.loads(response.choices[0].message.content)
        return {"questions" : questions}
    except json.JSONDecodeError:
        # If parsing fails, return a message with the raw text
        return {"error": "Failed to parse response", "response": response.choices[0].message.content}

def Generate_Reading_Comprehension_Chapter(topic: str):
    messages = [
        {'role' : 'system', 'content' : '''
            You're an experienced pre-academy English test creator, with a creative mindset for creating unique texts,
            that questions will be asked about, in a purpose of checking the student's vocabulary.
         '''
         },
         {
             'role' : 'user', 'content' : f'''
                Generate a text about the following subject in English: {topic}.
             '''
         },
         {
             'role' : 'assistant',
             'content' : '''
                The user will enter a topic for the text and you will generate a text according to the following instructions:
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
        You're an English teacher, who professionally knows to check a student's understanding of a text using unique Reading Comprehension questions.
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
        }
        ]
    '''
    
    response = client.chat.completions.create(
        model = "gpt-3.5-turbo-1106",
        messages = messages,
        temperature = 0.7
    )
    
    response.choices[0].message.content = response.choices[0].message.content.replace("json","")
    response.choices[0].message.content = response.choices[0].message.content.replace("```","")

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

def Generate_Restatement_Chapter(words_list: list[str]):
    messages = [
        {'role' : 'system', 'content' : '''
            You're an experienced question creator for a formal pre-academy English test, that creatively create unique questions
            with the purpose of improving the student's vocabulary.
         '''
         },
         {
             'role' : 'user', 'content' : f'''
                Generate 3 Restatement questions using the following words: {words_list}.
             '''
         },
         {
             'role' : 'assistant',
             'content' : '''
                The user will give you a list of words. Each question will use one of the words in the original statement, or in one of the answers.
                The restatement questions should be formatted in a JSON array format without any additional characters. 
                A Restatement question is a statement in an academic level of English, made of a sophisticated sentence or two, about a random subject, and the answer options are statements that potentially could replace the original statement.
                The correct answer should replace the statement perfectly by it's meaning. One other answer option should be close, and the two other answer options should not be close. 
                Here's an example for the format:
                [{
                "q" : (The generated phrase to restate),
                "a1" : (1st option of answer),
                "a2" : (2nd option of answer),
                "a3" : (3rd option of answer),
                "a4" : (4th option of answer),
                "c" : (the number of the correct answer)
                },
                ...]

                Here's an example:
                Input: Generate 3 Restatement questions using the following words: significance, fictional, reputation.
                Output:
                [{
                "q" : "Although the scientist's discovery was groundbreaking, it took years for the academic community to recognize its significance.",
                "a1" : "The scientist's discovery was immediately recognized as groundbreaking.",
                "a2" : "The scientist’s discovery was not considered significant at first.",
                "a3" : "The academic community quickly accepted the scientist's discovery.",
                "a4" : "The scientist's discovery was never acknowledged by the academic community.",
                'c' : 2
                },
                {
                "q" : "Unlike his previous novels, the author’s latest book focuses on historical events rather than fictional stories.",
                "a1" : "The author's latest book is about historical events, unlike his earlier novels.",
                "a2" : "The author’s latest book is a fictional story like his previous novels.",
                "a3" : "All of the author's books, including his latest, focus on historical events.",
                "a4": "The author's latest book is a mix of historical facts and fiction.",
                "c" : 1
                },
                {
                "q": "Even though the restaurant is quite expensive, it is always fully booked due to its excellent reputation.",
                "a1": "The restaurant is fully booked because it is very expensive.",
                "a2": "Despite its high prices, the restaurant remains popular because of its reputation.",
                "a3": "The restaurant is never fully booked because of its expensive menu.",
                "a4": "The restaurant’s reputation has declined due to its high prices.",
                "c": 2
                }
                ]
             '''
         }
    ]

    response = client.chat.completions.create(
        model = "gpt-3.5-turbo-1106",
        messages = messages,
        temperature = 0.7
    )
    response.choices[0].message.content = response.choices[0].message.content.replace("json","")
    response.choices[0].message.content = response.choices[0].message.content.replace("```","")

    print(response.choices[0].message.content)
    try:
        questions = json.loads(response.choices[0].message.content)
        return {"questions" : questions}
    except json.JSONDecodeError:
        # If parsing fails, return a message with the raw text
        print("the result: " + response.choices[0].message.content)
        return {"error": "Failed to parse response", "response": response.choices[0].message.content}

def Generate_Text_Title (text : str):
    messages = [
        {'role' : 'system', 'content' : """
            You're a creative titler, who manage to accurately sum a text to a few words.
        """
         },
         {
             'role' : 'user', 'content' : f'''
                Generate a title for the following text: 
                {text}
             '''
         },
         {
             'role' : 'assistant',
             'content' : '''
                The user will ask you to generate a title for a given text, and you'll act according to the following instructions:
                As a text-titler you try to give each text a unique name that clearly relates to the given text.
                The title should be a MAXIMUM of 3 words.
             '''
         }
    ]
    response = client.chat.completions.create(
        model = "gpt-3.5-turbo",
        messages = messages,
        temperature = 0.5
    )
    return response.choices[0].message.content