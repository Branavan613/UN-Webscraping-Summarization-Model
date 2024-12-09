# UN Document Summarization AI Chatbot

## Overview

The UN is one of the largest organizations in the world, responsible for protecting global peace, human rights, humanitarian aid and support development. 
As a result, their extensive database holds hundreds of thousands of official documents that tell the story of our modern human world.
This project is a sophisticated AI-powered chatbot designed to scrape, process, and summarize UN documents. It provides users with concise, accessible summaries of complex reports while allowing users to locate the most relevant documents to their search query. 
The chatbot leverages vector storing and similarity search algorithms to help independent social justice lawyers or anyone interested in human rights with a faster way to search through long long reports.

---

## Features

- **Web Scraping**: Downloads UN documents as PDFs using Selenium and BeautifulSoup.
- **Summarization**: Extracts and summarizes key points from documents.
- **AI Chatbot Interface**: Enables interactive querying of document content.
- **Multi-language Support**: Processes documents in multiple languages.
- **Scalable Storage**: Embeds processed summaries into ChromaDB for efficient retrieval.
- **Real-time Updates**: Periodically scrapes new documents and integrates them into the database.

---

## Prerequisites

### Software
- Python 3.9+
- Web browser (Chrome recommended) and ChromeDriver
- NVIDIA GPU (optional for accelerated NLP tasks)

### Python Dependencies
- Selenium
- BeautifulSoup (bs4)
- 
- ChromaDB
- Hugging Face Transformers

### Installation
1. Clone the repository:
   ```bash
   git clone https://github.com/your-username/un-chatbot.git
   cd un-chatbot
   ```
2. Install the backend dependencies
   ```bash
   cd backend
   pip install -r requirements.txt
   ```
3. Install the frontend dependencies
   ```bash
   cd front
   npm install
   ```
4. Start the program
   In Backend:
   ```bash
   python app.py
   ```
   In Frontend:
   ```bash
   npm start
   ```
5. Explore the program! Define your own search collection, let the program automatically scrape the documents from UN's official document database and once completed, research hundreds of documents in seconds

## License
This project is licensed under the MIT License. See the LICENSE file for details.

## Acknowledgments
Llama-3.1 & Hugging Face: For providing state-of-the-art LLM and embedding models.
UN OHCHR: For the source documents and their invaluable contributions to human rights work.
