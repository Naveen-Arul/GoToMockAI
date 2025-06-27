# AI-Powered Mock Interview App

This project is a FastAPI-based web application that conducts AI-powered mock interviews based on a candidate's resume. It generates personalized interview questions, evaluates answers, and provides feedback using advanced language models.

## Features
- **Resume Upload:** Upload your resume in PDF format.
- **Personalized Questions:** Automatically generates interview questions tailored to your resume.
- **Answer Evaluation:** Compares your answers to ideal responses and provides detailed feedback.
- **Text-to-Speech (Optional):** Reads questions and feedback aloud for accessibility.
- **API-First:** Easily connect with frontend apps or use via Swagger UI.

## Getting Started

### Prerequisites
- Python 3.10+
- [pip](https://pip.pypa.io/en/stable/)

### Installation
1. **Clone the repository:**
   ```sh
   git clone https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git
   cd YOUR_REPO_NAME/MAIN
   ```
2. **Create a virtual environment (recommended):**
   ```sh
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```
3. **Install dependencies:**
   ```sh
   pip install -r requirements.txt
   ```
4. **Set up environment variables:**
   - Create a `.env` file in the `MAIN` directory:
     ```
     GROQ_API_KEY=your_groq_api_key_here
     ```

## Usage

### Run the API Server
```sh
python api.py
```
- The API will be available at `http://127.0.0.1:8000`.
- Access the interactive docs at `http://127.0.0.1:8000/docs`.

### API Endpoints
- `POST /interview/start` — Upload a resume to start a new interview session.
- `POST /interview/{interview_id}/submit` — Submit your answers and get evaluation feedback.

## Deployment (Render)
1. **Push your code to GitHub.**
2. **Create a new Web Service on [Render](https://render.com/):**
   - Connect your GitHub repo.
   - Set the build and start commands:
     - Build Command: `pip install -r requirements.txt`
     - Start Command: `python api.py`
   - Add your `GROQ_API_KEY` as an environment variable in the Render dashboard.
3. **Deploy!**

## Notes
- **Do not commit your `.env` file or API keys to GitHub.**
- For local testing, ensure your `.env` file is present.
- For production, set environment variables in your hosting platform.

## License
This project is for educational and demonstration purposes. 