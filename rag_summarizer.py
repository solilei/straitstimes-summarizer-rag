from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_ollama.embeddings import OllamaEmbeddings
from langchain_ollama.chat_models import ChatOllama
from langchain_community.vectorstores import Chroma
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.documents import Document
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains.retrieval import create_retrieval_chain


class RagSummarizer:
    def __init__(self,
                 embed_model: str = "mxbai-embed-large:latest",
                 llm_model: str = "phi4:14b-q4_K_M",
                 chunk_size: int = 1300,
                 chunk_overlap: int = 180,
                 text_list=list[str]
                 ):
        self.embed_model = embed_model
        self.llm_model = llm_model
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.vector_db = None
        self.llm = None
        self.retriever = None
        self.summarize_chain = None
        self.retrieval_qa_chain = None
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap
        )
        self.text_list = text_list
        self._all_chunks = []

    def chunker(self):
        self._all_chunks = []
        articles_loaded = 0

        for article_idx, article_text in enumerate(self.text_list):
            if not article_text or len(article_text) < 150:
                print(f"Skipping article {article_idx + 1} due to short/empty content.")
                continue

            else:
                try:
                    article = Document(page_content=article_text,
                                       metadata={"source": f"article_{article_idx + 1}"}
                                       )
                    chunks = self.splitter.split_documents(documents=[article])
                    print(f"Article {article_idx + 1} split into {len(chunks)} chunk(s).")

                    if chunks:
                        self._all_chunks.extend(chunks)
                        articles_loaded += 1

                except Exception as e:
                    raise Exception(f"Error loading article {article_idx + 1}: {str(e)}")

        if not self._all_chunks:
            raise ValueError(f"No articles were loaded.")

        print(f"{articles_loaded} article(s) were chunked with {len(self._all_chunks)} total chunk(s).")

        return self._all_chunks

    def create_vector_db(self, chunks: list[Document], collection_name: str = "article-rag"):
        if not chunks:
            raise ValueError("No chunks were loaded.")

        try:
            embeddings = OllamaEmbeddings(model=self.embed_model)

            self.vector_db = Chroma.from_documents(
                collection_name=collection_name,
                embedding=embeddings,
                documents=chunks
            )
            print(f"Vector DB created with collection_name: {collection_name}.")

        except Exception as e:
            raise Exception(f"Error creating vector DB: {str(e)}.")

    def setup_rag_chain(self):
        if not self.vector_db:
            raise ValueError(f"Vector DB not initialized.")

        try:
            self.llm = ChatOllama(
                model=self.llm_model,
                temperature=0.2,
                top_p=0.8
            )

            self.retriever = self.vector_db.as_retriever(search_kwargs={"k": 5})

            summarize_prompt = ChatPromptTemplate.from_template(
                """You are an AI assistant tasked with summarizing news articles.
                Based *only* on the following context documents, provide a concise overview.
                Focus on the main events, key figures involved, and potential impacts mentioned in the text.
                Combine information from the different documents into a single, coherent summary.
    
                Context:
                {context}
    
                Concise Summary:"""
            )

            qa_prompt = ChatPromptTemplate.from_template(
                """Answer the following question based ONLY on the provided context from news articles.
                If the context does not contain the answer, state that clearly. Do not make up information.
    
                Context:
                {context}
    
                Question: {input}
    
                Answer:"""
            )

            self.summarize_chain = create_stuff_documents_chain(
                # Takes documents you explicitly give it and puts them in the prompt.
                llm=self.llm,
                prompt=summarize_prompt
            )

            self.retrieval_qa_chain = create_retrieval_chain(
                # Takes a query, finds relevant documents using a retriever, and then uses another chain (like create_stuff_documents_chain) to process those retrieved documents.
                retriever=self.retriever,
                combine_docs_chain=create_stuff_documents_chain(self.llm, qa_prompt)
            )

            print("RAG chain setup complete!")

        except Exception as e:
            raise Exception(f"Error setting up RAG chain: {str(e)}")

    def summary(self):
        if not self.summarize_chain:
            print("Summarize chain not initialized!")

        if not self.vector_db:
            raise ValueError("Vector DB not initialized! Cannot fetch documents for summary.")

        try:
            summary = self.summarize_chain.invoke({"context": self._all_chunks})
            return summary

        except Exception as e:
            raise Exception(f"Error processing summary: {str(e)}")

    def query(self, query: str):
        if not self.retrieval_qa_chain:
            print("Retrieval chain not initialized!")

        try:
            result = self.retrieval_qa_chain.invoke({"input": query})
            return result["answer"]

        except Exception as e:
            raise Exception(f"Error processing query: {str(e)}")
