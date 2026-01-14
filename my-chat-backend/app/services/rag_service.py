# app/services/rag_service.py
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_ollama import OllamaEmbeddings, OllamaLLM
from langchain_chroma import Chroma
from langchain_core.prompts import ChatPromptTemplate
from langchain_classic.chains import create_retrieval_chain
from langchain_classic.chains.combine_documents import create_stuff_documents_chain
import os
from langchain_community.document_loaders import PyMuPDFLoader
import requests

class RAGService:
    def __init__(self, windows_ip):
        self.windows_ip = f"http://{windows_ip}:11434"
        
# [추가] 연결 테스트 로직
        try:
            response = requests.get(self.windows_ip)
            if response.status_code == 200:
                print(f"✅ Ollama 서버 연결 성공: {self.windows_ip}")
        except:
            print(f"❌ Ollama 서버 연결 실패! IP와 윈도우 방화벽을 확인하세요.")

        self.embeddings = OllamaEmbeddings(
            model="mxbai-embed-large",
            base_url=self.windows_ip
        )
        
        self.llm = OllamaLLM(
            model="gemma3:12b",
            base_url=self.windows_ip,
            num_ctx=16384
        )
        self.vector_store = None

    def ingest_multiple_pdfs(self, file_paths: list):
        all_docs = []
        
        for file_path in file_paths:
            current_dir = os.path.dirname(os.path.abspath(__file__))
            project_root = os.path.dirname(os.path.dirname(current_dir))
            full_path = os.path.join(project_root, file_path)
            
            if os.path.exists(full_path):
                loader = PyMuPDFLoader(full_path)
                
                data = loader.load()

                total_chars = sum(len(page.page_content) for page in data)
                print(f"{file_path}: {len(data)} page, total text length  : {total_chars}")
                print(f"📄 {file_path} 로드 완료")
                all_docs.extend(loader.load())
            else:
                print(f"⚠️ 파일을 찾을 수 없음: {full_path}")

        # 모든 문서 합쳐서 한 번에 분할
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=400,
            chunk_overlap=100,
            separators=["\n제", "\n\n", "\n", " "]
        )
        splits = text_splitter.split_documents(all_docs)
        print(f"✂️ 총 {len(splits)} 개의 조각으로 분할되었습니다.")

        # [중요] 기존 DB가 있다면 삭제하거나 초기화 후 생성
        if os.path.exists("./chroma_db"):
            import shutil
            shutil.rmtree("./chroma_db") # 깨끗하게 새로 시작

        # 단 한 번의 호출로 모든 벡터 생성
        self.vector_store = Chroma.from_documents(
            documents=splits, 
            embedding=self.embeddings,
            persist_directory="./chroma_db"
        )
        return "학습 완료"

    async def get_rag_response_stream(self, question: str, systemPrompt: str):
        """질문에 대해 내규를 검색하고 답변을 생성합니다."""
        if not self.vector_store:
            yield "먼저 문서를 학습시켜주세요."

        fullSystemPrompt = f"""{systemPrompt}
        [문맥]
        {{context}}
        """

        prompt = ChatPromptTemplate.from_messages([
            ("system", fullSystemPrompt),
            ("human", "{input}") # create_stuff_documents_chain은 기본적으로 'input'을 사용합니다.
        ])
        # 2. RAG 체인 구성
        question_answer_chain = create_stuff_documents_chain(self.llm, prompt)
        retriever = self.vector_store.as_retriever(search_kwargs={"k": 15}) # 관련 조항 3개 검색
        rag_chain = create_retrieval_chain(retriever, question_answer_chain)

        # 3. 답변 생성
        # response = await rag_chain.ainvoke({"input": question})
        async for chunk in rag_chain.astream({"input": question}):
            if "answer" in chunk:
                yield chunk['answer']

        # return response["answer"]
