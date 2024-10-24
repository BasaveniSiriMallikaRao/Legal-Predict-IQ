# LEGAL PREDICT IQ AN AI DRIVEN CHATBOT FOR LAWYERS 
Legal Predict IQ is an interactive assistant designed to help users understand and navigate through various case  files by generating summaries and responding to user queries. The application leverages natural language processing (NLP) models and machine learning techniques to provide relevant information based on the uploaded  files.

# Features:

File Upload: Users can upload project files in different formats such as text, Python scripts, images, and videos.

File Summarization: Text and code files are summarized using NLP models, while images are analyzed for visual summaries.

Interactive Query System: Users can ask questions related to the uploaded files and get relevant responses.

File Management: Uploaded files are stored in a SQLite database.

# Technologies Used

Streamlit: For building the interactive web application.

SQLite: For storing the uploaded files.

Hugging Face Transformers: For text and code summarization using the BART model.

Replicate API: For generating image summaries.

scikit-learn: For calculating the similarity between user queries and file summaries using TF-IDF and cosine similarity.

# Models
BART (Bidirectional and Auto-Regressive Transformers): Used for summarizing text and code files. It is pre-trained on a large corpus of text and fine-tuned for summarization tasks.

# Setup and Installation
Clone the Repository:

bash


git clone <repository_url>
cd LegalPredictIQ
# Create a Virtual Environment:

bash

python3 -m venv venv

source venv/bin/activate

# Install Dependencies:

bash

pip install -r requirements.txt

# Set Up Database:

Ensure the database directory exists and create the SQLite database.

bash

mkdir -p database

python -c 'from chatbot import create_database; create_database()'

# Add Replicate API Token:

Update the chatbot.py file with your Replicate API token.

python

client = replicate.Client(api_token="Your-Replicate-API-Token")


# Run the Application:

bash

streamlit run app.py
# Usage

Upload Files: Use the file uploader to upload your project files.

Ask Questions: Use the input box to ask questions related to the uploaded files.

View Responses: The assistant will provide responses based on the uploaded files.


# File Structure

app.py: The main Streamlit application script.

chatbot.py: Contains functions for handling database operations, file processing, summarization, and query handling.

requirements.txt: Lists all Python dependencies.

# Contributing

Fork the repository.

Create a new branch (git checkout -b feature-branch).

Make your changes and commit them (git commit -am 'Add new feature').

Push to the branch (git push origin feature-branch).

Create a new Pull Request.
