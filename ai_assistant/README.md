# 🌱 Smart Agriculture Management System

A Django-based Smart Agriculture Management System designed to help farmers manage their agricultural activities efficiently using technology and AI.

## 🚀 Features

- **User Authentication:** Secure user registration, login, profile management and password change.
- **Crop Management:** Add, view, edit and manage crop details.
- **AI Disease Detection:** Detect plant diseases using leaf images with AI assistance.
- **Irrigation Management:** Create irrigation schedules and track irrigation history.
- **Soil Test Management:** Store and manage soil test reports.
- **Crop Recommendation:** Get crop recommendations.
- **Weather Information:** Access weather-related information.
- **Inventory Management:** Manage agricultural inventory and usage.
- **Finance Management:** Track income and expenses.
- **AI Assistant:** Get smart agricultural guidance.
- **Multilingual Support:** Language switching for a better user experience.

## 🛠️ Technologies Used

- Python
- Django
- HTML
- CSS
- JavaScript
- SQLite
- Google Gemini API
- Bootstrap

## 📂 Project Structure

- `accounts/` - User authentication and profile management
- `ai_assistant/` - AI assistant and disease detection services
- `farm/` - Crop, irrigation and soil management
- `finance/` - Financial management
- `inventory/` - Inventory management
- `config/` - Django project configuration
- `templates/` - HTML templates

## ⚙️ Installation and Setup

1. Clone the repository:

   `git clone https://github.com/ganeshghayal86-ai/Smart-Agriculture-Management-System.git`

2. Navigate to the project folder:

   `cd Smart-Agriculture-Management-System`

3. Create a virtual environment:

   `python -m venv venv`

4. Activate the virtual environment:

   `venv\Scripts\activate`

5. Install dependencies:

   `pip install -r requirements.txt`

6. Configure environment variables in a `.env` file. Add your Django secret key and Gemini API key as required by the project.

7. Run database migrations:

   `python manage.py migrate`

8. Start the development server:

   `python manage.py runserver`

9. Open in your browser:

   `http://127.0.0