# News RAG Summarizer & Q&A

A Python application that scrapes articles from The Straits Times, uses a local Large Language Model (LLM) via Ollama and Retrieval-Augmented Generation (RAG) to create a concise summary, and allows you to ask questions about the scraped content.

## Features

*   Scrapes recent news articles based on user-selected topics (e.g., "World", "Tech", "Sport").
*   Processes and chunks article text using LangChain.
*   Generates vector embeddings locally using Ollama and stores them in a Chroma vector database (in-memory).
*   Utilizes a local LLM (e.g., Phi-3 Mini, Llama 3) via Ollama for:
    *   Generating a summary of all scraped articles.
    *   Answering user questions based *only* on the context of the scraped articles (RAG).
*   Interactive command-line interface for topic selection and Q&A.

## How it Works

1.  **Scraping (`scraper.py`):** Prompts the user for a news topic, constructs the URL for The Straits Times section, scrapes the main page for article links, and then visits each article link to extract the main text content.
2.  **Processing & Vectorization (`rag_summarizer.py`):**
    *   Takes the list of scraped article texts.
    *   Chunks the texts into smaller, manageable pieces using `RecursiveCharacterTextSplitter`.
    *   Uses an Ollama embedding model (e.g., `mxbai-embed-large`) to convert text chunks into vectors.
    *   Stores these vectors in an in-memory Chroma vector database.
3.  **RAG Chain Setup (`rag_summarizer.py`):**
    *   Initializes a local chat model via Ollama (e.g., `phi3`).
    *   Sets up two LangChain chains:
        *   A "stuff" chain for summarizing all documents provided.
        *   A retrieval chain for Q&A, which first retrieves relevant text chunks from the vector database based on the user's question and then feeds them as context to the LLM to generate an answer.
4.  **Interaction (`main.py`):**
    *   Orchestrates the scraping and RAG setup.
    *   Presents the initial summary to the user.
    *   Enters a loop where the user can ask questions about the articles.
    *   Queries the RAG chain to get answers based on the retrieved context.
    *   Allows the user to exit with `/exit`.

## Prerequisites

Before you begin, ensure you have the following installed:

1.  **Python:** Version 3.9 or higher recommended.
2.  **Git:** For cloning the repository.
3.  **Ollama:** You **must** have Ollama installed and running. Download it from [https://ollama.com/](https://ollama.com/).
4.  **Ollama Models:** You need the embedding and chat models used by the script. Pull them using the Ollama CLI:
    ```bash
    # Default models used in the script (adjust if you change them)
    ollama pull mxbai-embed-large:latest
    ollama pull phi3:latest # Or the specific model you configure, e.g., phi3:3.8b-mini-instruct-4k-q4_K_M

    # Verify models are available
    ollama list
    ```
    *Note: Model names and availability can change. Check the Ollama library for current models.*

## Installation

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/solilei/straitstimes-summarizer-rag.git
    cd news-rag-summarizer
    ```

2.  **Create and activate a virtual environment (Recommended):**
    *   **Linux/macOS:**
        ```bash
        python3 -m venv venv
        source venv/bin/activate
        ```
    *   **Windows:**
        ```bash
        python -m venv venv
        .\venv\Scripts\activate
        ```

3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

## Configuration

Key parameters can be adjusted directly in the scripts:

*   **Target Website & Topics:** Modify `available_topics` and URL construction logic in `scraper.py`. The scraping logic (HTML tags/classes) is specific to `straitstimes.com` and may need updating if the site changes.
*   **Scraping:** Change `max_articles` in `scraper.py`.
*   **LLM Models:** Change `embed_model` and `llm_model` defaults in the `__init__` method of `RagSummarizer` in `rag_summarizer.py`. Ensure the chosen models are available in your Ollama instance.
*   **Chunking:** Adjust `chunk_size` and `chunk_overlap` in `rag_summarizer.py`.
*   **Retrieval:** Modify `search_kwargs={"k": 5}` in `setup_rag_chain` within `rag_summarizer.py` to change the number of retrieved chunks.

*(Future Improvement: Move these settings to a `config.yaml` or `.env` file for easier management).*

## Usage

1.  **Ensure Ollama is running:** Start the Ollama application or run `ollama serve` in your terminal.
2.  **Run the main script:**
    ```bash
    python main.py
    ```
3.  **Follow the prompts:**
    *   Choose a news topic from the provided list.
    *   Wait for the scraping and RAG setup to complete.
    *   Read the generated summary.
    *   Enter your questions about the articles when prompted.
    *   Type `/exit` to quit the application.

## Disclaimer & Important Notes

*   **Web Scraping:** This script scrapes content from `straitstimes.com`. Please be mindful of their `robots.txt` file and Terms of Service. Web scraping can be fragile; if the website's HTML structure changes, the scraper (`scraper.py`) will likely need updates. Use responsibly.
*   **Ollama Performance:** The speed of embedding generation, summarization, and Q&A depends heavily on your local hardware (CPU/GPU, RAM) and the specific Ollama models used. Larger models require more resources.
*   **In-Memory Vector Store:** The Chroma vector database is created in memory each time the script runs. It is not persisted between runs.
*   **Information Accuracy:** The LLM's summary and answers are based *solely* on the text scraped from the articles during that run. The quality of the output depends on the source text and the capabilities of the chosen LLM. It may not always be perfectly accurate or complete. Do not rely on this for critical decisions.

---
