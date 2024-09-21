# Daily Papers HN

Daily Papers HN is a web application that displays a curated list of daily academic papers in a Hacker News-like interface. It fetches papers from the Hugging Face Daily Papers API and presents them in a sortable, paginated list.

## Features

- Fetches and displays academic papers from Hugging Face's Daily Papers API
- Sorts papers by "Hot", "New", or "Rising" algorithms
- Paginated interface for easy navigation
- Responsive design with dark mode support
- Hacker News-inspired UI

## How it works

1. The app fetches papers from the Hugging Face API on initialization
2. Papers can be sorted using different algorithms:
   - Hot: Based on upvotes and age
   - New: Based on publication date
   - Rising: Emphasizes recent upvotes and rate of upvote accumulation
3. Users can navigate through pages of papers
4. Each paper displays title, authors, upvotes, comments, and time since publication

## Technologies Used

- Python
- Gradio (for the web interface)
- Requests (for API calls)

## How to Submit a Paper

Papers can be submitted directly to Hugging Face's Daily Papers:
https://huggingface.co/papers/submit

Submitted papers will automatically appear in the application.

## Running the Application

To run the Daily Papers HN application locally, follow these steps:

1. Clone the repository:
   ```
   git clone https://github.com/your-username/dailypapersHN.git
   cd dailypapersHN
   ```

2. Create a virtual environment (optional but recommended):
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
   ```

3. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Run the application:
   ```
   python app.py
   ```

5. Open your web browser and navigate to the URL displayed in the console (typically http://127.0.0.1:7860).

Note: Make sure you have Python 3.7 or higher installed on your system.
