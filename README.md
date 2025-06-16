# Amirnetix

## Description
A brief overview of what the project does. (Placeholder for user to fill in)

## Features
- User Authentication
- Simulation
- Data Analysis
- Management Interface

## Project Structure
- **Auth:** Handles user authentication and management.
- **Simulator:** Manages simulation functionalities.
- **Analysis:** Provides data analysis tools and insights.
- **Management:** Offers a management interface for administrative tasks.

## Getting Started

### Prerequisites
- Python 3.x
- pip

### Installation
1. Clone the repository:
   ```bash
   git clone <repository-url>
   ```
2. Navigate to the project directory:
   ```bash
   cd Amirnetix
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Apply database migrations:
   ```bash
   python manage.py migrate
   ```
5. Run the development server:
   ```bash
   python manage.py runserver
   ```

## Usage
(Placeholder for how to use the application)

## Contributing
(Placeholder for contribution guidelines)

## License
(Placeholder - recommend MIT or specify if another is used)

## Project Data Setup (for Word Upload Feature)

The application includes a feature within the 'Management' app to upload word lists from predefined Excel (`.xlsx`) and CSV (`.csv`) files. This is useful for populating the vocabulary database.

To enable this functionality, you need to:

1.  **Create a `project_data` directory:**
    In the root directory of this project (the same directory where `manage.py` is located), create a new folder named `project_data`.

2.  **Place data files into `project_data`:**
    Obtain the following data files and place them inside the `project_data` directory:
    *   `academic_word_list.xlsx`
    *   `GSL Words List.csv`

The `upload_words` view in the `Management` app is configured to look for these files in `[Your Project Root]/project_data/`. Without these files in the specified location, the word upload feature will not work and may result in errors.

## Key Local Modules

### `Amirnetix.prompts` Module

The simulator content generation features within the `Management` app (specifically in `Management/views.py` functions like `generate_test` and `generate_simulator_using_words`) rely heavily on a local Python module located at `Amirnetix/prompts.py`.

This module is responsible for creating the actual text and structure for chapters, questions, and answers, potentially interacting with external AI services or using predefined templates and logic.

**Important Note:** The internal workings of the `Amirnetix.prompts` module have not been reviewed or modified during the recent refactoring. Its correct functionality is assumed and is critical for the success of the simulator content generation features. Any issues with content generation likely stem from this module.
