from scraper import Scraper
from rag_summarizer import RagSummarizer


def run_pipeline():
    """Runs the main scraping, processing, and interaction pipeline."""
    try:
        st_scraper = Scraper()

        articles = st_scraper.get_articles_list()

        if not articles:
            print("Failed to scrape any articles. Exiting...")
            return

        rag = RagSummarizer(text_list=articles)
        chunks = rag.chunker()
        rag.create_vector_db(chunks=chunks)
        rag.setup_rag_chain()
        summary = rag.summary()

        print("\n---------------------")
        print(summary)
        print("---------------------\n")

        print("Setup complete. You can now ask questions about the articles.\n\n")

        while True:
            query = input("Enter your question (Type '/exit' to quit): ")

            if query.lower().strip() == "/exit":
                print("Thank you for using the summarizer!")
                break
            if not query.strip():
                continue

            try:
                resp = rag.query(query=query)
                print("\n--- Answer ---")
                print(resp)
                print("--------------\n")
            except Exception as e:
                raise Exception(f"Error: {str(e)}")
    except Exception as e:
        return Exception(f"Error: {str(e)}")

if __name__ == "__main__":
    run_pipeline()