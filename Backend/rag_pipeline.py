# backend/rag_pipeline.py
from langchain_community.vectorstores import Chroma
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.llms import HuggingFacePipeline
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnablePassthrough
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM, pipeline

class RAGPipeline:
    def __init__(self, persist_dir="D:\Shana\chroma_db"):
        self.persist_dir = persist_dir

        # Initialize embedding and vector DB
        self.embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
        self.db = Chroma(
            collection_name="rag_docs", 
            persist_directory=self.persist_dir, 
            embedding_function=self.embeddings
        )

        # Initialize FLAN-T5 small model as LLM
        tokenizer = AutoTokenizer.from_pretrained("google/flan-t5-small")
        model = AutoModelForSeq2SeqLM.from_pretrained("google/flan-t5-small")
        pipe = pipeline(
            "text2text-generation", 
            model=model, 
            tokenizer=tokenizer, 
            max_new_tokens=200
        )
        self.llm = HuggingFacePipeline(pipeline=pipe)

        # Create retriever
        self.retriever = self.db.as_retriever(search_kwargs={"k": 4})

        # Create the RAG chain using LCEL
        template = """Answer the question based only on the following context:

Context: {context}

Question: {question}

Answer:"""

        prompt = PromptTemplate.from_template(template)

        def format_docs(docs):
            return "\n\n".join(doc.page_content for doc in docs)

        self.qa_chain = (
            {"context": self.retriever | format_docs, "question": RunnablePassthrough()}
            | prompt
            | self.llm
            | StrOutputParser()
        )

    def ingest_pdf(self, pdf_path: str):
        """Ingest a PDF file into the vector database"""
        loader = PyPDFLoader(pdf_path)
        documents = loader.load()
        splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        chunks = splitter.split_documents(documents)
        self.db.add_documents(chunks)
        # Note: Chroma auto-persists in newer versions
        return len(chunks)

    def ask(self, query: str):
        """Ask a question and get an answer based on ingested documents"""
        answer = self.qa_chain.invoke(query)
        return answer