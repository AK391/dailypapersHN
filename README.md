# Daily Papers HN

Daily Papers HN is a Python-based web application that displays academic papers in a Hacker News-like interface. It utilizes the Hugging Face Daily Papers API to fetch and present papers in a sortable, paginated list.

![Screen Shot 2024-09-22 at 4 18 23 PM](https://github.com/user-attachments/assets/21373474-43b0-4704-9a91-f7de925a7b79)


## Web Demo

You can try out the Daily Papers HN application online without any local setup:

[Daily Papers HN Demo](https://huggingface.co/spaces/akhaliq/dailypapershackernews)

This demo is hosted on Hugging Face Spaces and provides the full functionality of the application.

## Technical Overview

- **Backend**: Python 3.7+
- **Web Framework**: Gradio
- **API Interaction**: Requests library
- **Data Processing**: Custom `PaperManager` class
- **Hosting**: Hugging Face Spaces
- **Development Environment**: Cursor with Claude 3.5-sonnet AI assistance

## Key Components

1. **PaperManager Class**: Handles paper fetching, sorting, and rendering
   - Implements custom sorting algorithms: Hot, New, and Rising
   - Manages pagination and paper formatting

2. **API Integration**: 
   - Endpoint: `https://huggingface.co/api/daily_papers`
   - Fetches up to 100 papers per request

3. **Sorting Algorithms**:
   - Hot: `score = upvotes / ((time_diff_hours + 2) ** 1.5)`
   - Rising: `score = upvotes / (time_diff_hours + 1)`
   - New: Based on `publishedAt` timestamp

4. **Gradio Interface**:
   - Utilizes `gr.Blocks` for layout
   - Implements custom CSS for Hacker News-like styling
   - Responsive design with dark mode support

## Core Functionality

1. **Paper Fetching**: 
   ```python
   def fetch_papers(self):
       response = requests.get(f"{API_URL}?limit=100")
       self.raw_papers = response.json()
       self.sort_papers()
   ```

2. **Sorting**:
   ```python
   def sort_papers(self):
       if self.sort_method == "hot":
           self.papers = sorted(self.raw_papers, key=self.calculate_score, reverse=True)
       # Similar for "new" and "rising"
   ```

3. **Rendering**:
   ```python
   def render_papers(self):
       current_papers = self.papers[start:end]
       papers_html = "".join([self.format_paper(paper, idx) for idx, paper in enumerate(current_papers)])
       return f"<table class='itemlist'>{papers_html}</table>"
   ```

4. **Pagination**:
   ```python
   def next_page(self):
       if self.current_page < self.total_pages:
           self.current_page += 1
       return self.render_papers()
   ```

## Setup and Running

1. Clone the repository:
   ```
   git clone https://github.com/your-username/dailypapersHN.git
   cd dailypapersHN
   ```

2. Set up a virtual environment:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Run the application:
   ```
   python app.py
   ```

5. Access the web interface at `http://127.0.0.1:7860`

## Development Notes

- The application uses Gradio's `gr.Blocks` for a flexible layout.
- Custom CSS is implemented for styling, including dark mode support.
- Error handling is in place for API requests and data processing.
- The `PaperManager` class is designed for easy extension and modification of sorting algorithms.

## Future Enhancements

- Implement caching to reduce API calls
- Add unit tests for sorting algorithms and rendering functions
- Explore asynchronous paper fetching for improved performance

## Contributing

Contributions are welcome! Please fork the repository and submit a pull request with your changes.

## Deployment

The application is deployed on Hugging Face Spaces, which provides a serverless environment for hosting Gradio apps. To deploy your own version:

1. Fork this repository to your GitHub account.
2. Create a new Space on Hugging Face, linking it to your forked repository.
3. Configure the Space to use the `app.py` file as the entry point.
4. Hugging Face Spaces will automatically deploy and update the app based on your repository changes.

---

*Note: This application was developed using Cursor with Claude 3.5-sonnet AI assistance. This README was also generated with the assistance of Claude 3.5-sonnet in Cursor AI.*
