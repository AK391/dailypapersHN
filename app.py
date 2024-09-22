import gradio as gr
import requests
from datetime import datetime, timezone

API_URL = "https://huggingface.co/api/daily_papers"

class PaperManager:
    def __init__(self, papers_per_page=30):
        self.papers_per_page = papers_per_page
        self.current_page = 1
        self.papers = []
        self.total_pages = 1
        self.sort_method = "hot"  # Default sort method
        self.raw_papers = []  # To store fetched data

    def calculate_score(self, paper):
        """
        Calculate the score of a paper based on upvotes and age.
        This mimics the "hotness" algorithm used by platforms like Hacker News.
        """
        upvotes = paper.get('paper', {}).get('upvotes', 0)
        published_at_str = paper.get('publishedAt', datetime.now(timezone.utc).isoformat())
        try:
            published_time = datetime.fromisoformat(published_at_str.replace('Z', '+00:00'))
        except ValueError:
            # If parsing fails, use current time to minimize the impact on sorting
            published_time = datetime.now(timezone.utc)
        
        time_diff = datetime.now(timezone.utc) - published_time
        time_diff_hours = time_diff.total_seconds() / 3600  # Convert time difference to hours

        # Avoid division by zero and apply the hotness formula
        score = upvotes / ((time_diff_hours + 2) ** 1.5)
        return score

    def calculate_rising_score(self, paper):
        """
        Calculate the rising score of a paper.
        This emphasizes recent upvotes and the rate of upvote accumulation.
        """
        upvotes = paper.get('paper', {}).get('upvotes', 0)
        published_at_str = paper.get('publishedAt', datetime.now(timezone.utc).isoformat())
        try:
            published_time = datetime.fromisoformat(published_at_str.replace('Z', '+00:00'))
        except ValueError:
            published_time = datetime.now(timezone.utc)

        time_diff = datetime.now(timezone.utc) - published_time
        time_diff_hours = time_diff.total_seconds() / 3600  # Convert time difference to hours

        # Rising score favors papers that are gaining upvotes quickly
        # Adjusted to have a linear decay over time
        score = upvotes / (time_diff_hours + 1)
        return score

    def fetch_papers(self):
        try:
            response = requests.get(f"{API_URL}?limit=100")
            response.raise_for_status()
            data = response.json()

            if not data:
                print("No data received from API.")
                return False

            # Debug: Print keys of the first paper
            print("Keys in the first paper:", data[0].keys())

            self.raw_papers = data  # Store raw data

            self.sort_papers()
            self.total_pages = max((len(self.papers) + self.papers_per_page - 1) // self.papers_per_page, 1)
            self.current_page = 1
            return True
        except requests.RequestException as e:
            print(f"Error fetching papers: {e}")
            return False
        except Exception as e:
            print(f"Unexpected error: {e}")
            return False

    def sort_papers(self):
        if self.sort_method == "hot":
            self.papers = sorted(
                self.raw_papers,
                key=lambda x: self.calculate_score(x),
                reverse=True
            )
        elif self.sort_method == "new":
            self.papers = sorted(
                self.raw_papers,
                key=lambda x: x.get('publishedAt', ''),
                reverse=True
            )
        elif self.sort_method == "rising":
            self.papers = sorted(
                self.raw_papers,
                key=lambda x: self.calculate_rising_score(x),
                reverse=True
            )
        else:
            self.papers = sorted(
                self.raw_papers,
                key=lambda x: self.calculate_score(x),
                reverse=True
            )

    def set_sort_method(self, method):
        if method not in ["hot", "new", "rising"]:
            method = "hot"
        print(f"Setting sort method to: {method}")
        self.sort_method = method
        self.sort_papers()
        self.current_page = 1
        return True  # Assume success

    def format_paper(self, paper, rank):
        title = paper.get('title', 'No title')
        paper_id = paper.get('paper', {}).get('id', '')
        url = f"https://huggingface.co/papers/{paper_id}"
        authors = ', '.join([author.get('name', '') for author in paper.get('paper', {}).get('authors', [])]) or 'Unknown'
        upvotes = paper.get('paper', {}).get('upvotes', 0)
        comments = paper.get('numComments', 0)
        published_time_str = paper.get('publishedAt', datetime.now(timezone.utc).isoformat())
        try:
            published_time = datetime.fromisoformat(published_time_str.replace('Z', '+00:00'))
        except ValueError:
            published_time = datetime.now(timezone.utc)
        time_diff = datetime.now(timezone.utc) - published_time
        time_ago_days = time_diff.days
        time_ago = f"{time_ago_days} days ago" if time_ago_days > 0 else "today"

        return f"""
        <tr class="athing">
            <td align="right" valign="top" class="title"><span class="rank">{rank}.</span></td>
            <td valign="top" class="title">
                <a href="{url}" class="storylink" target="_blank">{title}</a>
            </td>
        </tr>
        <tr>
            <td colspan="2" class="subtext">
                <span class="score">{upvotes} points</span> Authors: {authors} {time_ago} | {comments} comments
            </td>
        </tr>
        <tr class="spacer"><td colspan="2"></td></tr>
        """

    def render_papers(self):
        start = (self.current_page - 1) * self.papers_per_page
        end = start + self.papers_per_page
        current_papers = self.papers[start:end]

        if not current_papers:
            return "<div class='no-papers'>No papers available for this page.</div>"

        papers_html = "".join([self.format_paper(paper, idx + start + 1) for idx, paper in enumerate(current_papers)])
        return f"""
        <table border="0" cellpadding="0" cellspacing="0" class="itemlist">
            {papers_html}
        </table>
        """

    def next_page(self):
        if self.current_page < self.total_pages:
            self.current_page += 1
        return self.render_papers()

    def prev_page(self):
        if self.current_page > 1:
            self.current_page -= 1
        return self.render_papers()

paper_manager = PaperManager()

def initialize_app():
    if paper_manager.fetch_papers():
        return paper_manager.render_papers()
    else:
        return "<div class='no-papers'>Failed to fetch papers. Please try again later.</div>"

def change_sort_method(method):
    method_lower = method.lower()
    print(f"Changing sort method to: {method_lower}")
    if paper_manager.set_sort_method(method_lower):
        print("Sort method set successfully.")
        return paper_manager.render_papers()
    else:
        print("Failed to set sort method.")
        return "<div class='no-papers'>Failed to sort papers. Please try again later.</div>"

css = """
/* Hacker News-like CSS */

body {
    background-color: white;
    font-family: "Helvetica Neue", Helvetica, Arial, sans-serif;
    font-size: 11px;
    color: #000;
    margin: 0;
    padding: 0;
}

a {
    color: #0000ff;
    text-decoration: none;
}

a:visited {
    color: #551a8b;
}

.container {
    width: 85%;
    margin: auto;
    padding-top: 10px;
}

.itemlist {
    width: 100%;
    border-collapse: collapse;
}

.header-table {
    width: 100%;
    background-color: #ff6600;
    padding: 2px 10px;
}

.header-table a {
    color: black;
    font-weight: bold;
    font-size: 14pt;
    text-decoration: none;
}

.athing {
    background-color: #f6f6ef;
}

.rank {
    font-size: 10px;
    color: #828282;
    padding-right: 5px;
}

.storylink {
    font-size: 13px;
    font-weight: bold;
}

.subtext {
    font-size: 10px;
    color: #828282;
    padding-left: 40px;
}

.subtext a {
    color: #828282;
    text-decoration: none;
}

.subtext a:hover {
    text-decoration: underline;
}

.spacer {
    height: 5px;
}

.no-papers {
    text-align: center;
    color: #828282;
    padding: 1rem;
    font-size: 14pt;
}

.pagination {
    padding: 10px 0;
    text-align: center;
}

.pagination button {
    background-color: #f0f0f0;  // Light gray background
    border: 1px solid #d0d0d0;  // Light border
    color: #0066cc;  // Blue text color
    padding: 6px 12px;
    margin: 0 3px;
    cursor: pointer;
    font-size: 14px;
    font-weight: bold;
    border-radius: 3px;
    transition: background-color 0.2s ease, color 0.2s ease;
}

.pagination button:hover {
    background-color: #e0e0e0;  // Slightly darker on hover
    color: #004499;  // Darker blue on hover
}

.pagination button:disabled {
    background-color: #f8f8f8;
    color: #999999;  // Gray text for disabled state
    cursor: not-allowed;
}

@media (max-width: 640px) {
    .header-table a {
        font-size: 12pt;
    }

    .storylink {
        font-size: 11px;
    }

    .subtext {
        font-size: 9px;
    }

    .rank {
        font-size: 9px;
    }

    .pagination button {
        padding: 8px 16px;
        font-size: 16px;
    }
}

/* Dark mode */
@media (prefers-color-scheme: dark) {
    body {
        background-color: #121212;
        color: #e0e0e0;
    }

    a {
        color: #add8e6;
    }

    a:visited {
        color: #9370db;
    }

    .header-table {
        background-color: #333;
    }

    .header-table a {
        color: #e0e0e0;
    }

    .athing {
        background-color: #1e1e1e;
    }

    .rank {
        color: #b0b0b0;
    }

    .subtext {
        color: #b0b0b0;
    }

    .subtext a {
        color: #b0b0b0;
    }

    .no-papers {
        color: #b0b0b0;
    }

    .pagination button {
        background-color: #2a2a2a;
        border-color: #3a3a3a;
        color: #4499ff;  // Lighter blue for dark mode
    }

    .pagination button:hover {
        background-color: #3a3a3a;
        color: #66b3ff;  // Even lighter blue on hover for dark mode
    }

    .pagination button:disabled {
        background-color: #222222;
        color: #666666;
    }
}

/* Add these rules to explicitly remove all borders */
table, tr, td {
    border: none;
    border-collapse: collapse;
    border-spacing: 0;
}

/* Remove border and add padding for the radio buttons */
.sort-radio {
    border: none !important;
    padding: 10px 10px 10px 10px !important;  // Added left and right padding
}

/* Style the radio buttons to match the Hacker News theme */
.sort-radio .gr-form {
    border: none !important;
    background: transparent !important;
}

.sort-radio .gr-form.gr-box {
    border-radius: 0 !important;
    box-shadow: none !important;
}

.sort-radio .gr-radio-row {
    padding: 0 !important;
}

/* Style the radio button labels */
.sort-radio label span {
    font-size: 14px;
    color: #828282;
    margin-left: 5px;
    margin-right: 15px;  // Add some space between options
}

/* Style the selected radio button */
.sort-radio input[type="radio"]:checked + label span {
    color: #ff6600;
    font-weight: bold;
}
"""

demo = gr.Blocks(css=css)

with demo:
    with gr.Column(elem_classes=["container"]):
        # Accordion for Submission Instructions
        with gr.Accordion("How to Submit a Paper", open=False):
            gr.Markdown("""
            **Submit the paper to Daily Papers:**
            [https://huggingface.co/papers/submit](https://huggingface.co/papers/submit)

            Once your paper is submitted, it will automatically appear in this demo.
            """)
        # Header without Refresh Button
        with gr.Row():
            gr.HTML("""
            <table border="0" cellpadding="0" cellspacing="0" class="header-table">
                <tr>
                    <td>
                        <span class="pagetop">
                            <b class="hnname"><a href="#">Daily Papers</a></b>
                        </span>
                    </td>
                    <!-- Removed the Refresh button cell -->
                </tr>
            </table>
            """)
        # Sorting Options
        with gr.Column():
            sort_radio = gr.Radio(
                choices=["Hot", "New", "Rising"],
                value="Hot",
                label="",  # Remove the original label
                interactive=True,
                elem_classes=["sort-radio"]
            )
        # Paper list
        paper_list = gr.HTML()
        # Navigation Buttons
        with gr.Row(elem_classes=["pagination"]):
            prev_button = gr.Button("Prev")
            next_button = gr.Button("Next")

    # Load papers on app start
    demo.load(initialize_app, outputs=[paper_list])

    # Button clicks for pagination
    prev_button.click(paper_manager.prev_page, outputs=[paper_list])
    next_button.click(paper_manager.next_page, outputs=[paper_list])

    # Sort option change
    sort_radio.change(
        fn=change_sort_method,
        inputs=[sort_radio],
        outputs=[paper_list]
    )

demo.launch()
