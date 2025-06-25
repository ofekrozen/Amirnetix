## 📘 Amirnetix – Smarter Prep for the AmirNet (previously Amiram) English Tests

**Amirnetix** is an advanced, AI-powered study platform designed to help Israeli students prepare effectively for the **AmirNet** English placement tests. With a strong focus on vocabulary mastery, sentence comprehension, and restatement skills, Amirnetix offers a fully interactive test simulation environment alongside personalized learning tools.

### ✨ Features

* 🎯 **Realistic Test Simulation**
  Simulates all 6 sections of the AmirNet test (Sentence Completion, Reading Comprehension, and Restatements) with multiple chapters and question navigation.

* 📚 **AI-Generated Practice Questions**
  Hundreds of practice questions dynamically generated with Hebrew explanations to boost understanding and retention.

* 🧠 **Smart Vocabulary Builder**
  Track how well you know each word with intuitive buttons: ✅ Perfect, ➖ Partial, ❌ Don’t Know. Includes definitions, Hebrew translations, example sentences, and tips.

* 📊 **Progress Tracking**
  Monitor your strengths and weaknesses to focus study time more effectively.

* 📝 **Hebrew-English Translation Mode**
  Flip cards to reveal Hebrew translations and focus on learning in context.

### 🚀 Technologies Used

* **Django** (Backend + Admin Panel)
* **HTML, CSS, JavaScript** (Frontend)
* **SQLite** (Database)
* **OpenAI API** for question generation and AI chat

### To Use/Update
go to the main folder Amirnetix (not Amirnetix/Amirnetix)
* cd [your path]/Amirnetix
Install requirements (if requirements.txt doesn't work, go to all .py files and download relevant libraries)
* pip install -r requirements.txt
Go to /Amirnetix/Amirnetix and create .env file
* Inside .env enter your OPENAI_API_KEY = "your-openai-api-key"
to run the project
* python manage.py runserver


### ToDos

* fix - repeating words in the answers of Simulator Questions within each Chapter (fix in prompts)
* fix requirements.txt
* Synchronize style/css
* Add Simulators