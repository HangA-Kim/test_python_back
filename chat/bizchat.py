import os  # 파일 경로 설정 등에 사용
import sys  # 한글 출력 인코딩에 사용
import io   # 한글 출력 인코딩에 사용
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain_community.document_loaders import TextLoader
from langchain_community.document_loaders import DirectoryLoader
from langchain_openai.embeddings import OpenAIEmbeddings
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
from langchain_core.prompts import PromptTemplate
from langchain_teddynote.messages import stream_response

load_dotenv()
os.getenv("OPENAI_API_KEY")

# 경로 추적을 위한 설정
os.environ["PWD"] = os.getcwd()

#출력의 인코딩을 utf-8로 설정한다
sys.stdout = io.TextIOWrapper(sys.stdout.detach(), encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.detach(), encoding='utf-8')

# TextLoader에 인코딩을 명시적으로 지정
class UTF8TextLoader(TextLoader):
    def __init__(self, file_path: str):
        super().__init__(file_path, encoding="utf-8")

# 기본적으로 Python은 Windows에서 cp949 인코딩을 사용하지만, 한글 텍스트 파일이 UTF-8로 인코딩된 경우 이 문제가 발생할 수 있습니다.
# python.exe bizchat.py reqQuestion path ( 위 index.ts 에서 spawn 으로 호출된 값 )
# sys.argv[0] : bizchat.py
# sys.argv[1] : reqQuestion
# sys.argv[2] : path
loader = DirectoryLoader(sys.argv[2], glob="*.txt", loader_cls=UTF8TextLoader)
documents = loader.load()
# print(len(documents))

text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200) # 분할 토큰수(chunk), 오버랩 정도
texts = text_splitter.split_documents(documents)
# print(f"분할된 텍스트 뭉치의 갯수: {len(texts)}")

# source_list = []
# for i in range(0, len(texts)):
#   source_list.append(texts[i].metadata["source"])


# element_counts = Counter(source_list)
# filtered_counts = {key: value for key, value in element_counts.items() if value >= 2}

# print("2개 이상으로 분할된 문서: ", filtered_counts)
# print("분할된 텍스트의 개수: ", len(documents) + len(filtered_counts))

# 구글코랩은 Chroma 를 쓰는데 여기서는 FAISS 로 바꿨다. 
# Chroma 는 Visual C++ 빌드 도구 > MSVC v142 - VS 2019 C++ x64/x86 build tools (최소한의 필수 컴파일러)
# 를 해줘야는데 설치하려니 2GB 라서 FAISS 로 바꿈. 같은 벡터 데이터 베이스임. 사용 함수도 비슷..

db = FAISS.from_documents(texts, embedding=OpenAIEmbeddings())
retriever = db.as_retriever()
# docs = retriever.get_relevant_documents("청년 장학금 정책을 알려주세요")
# print(f"유사도 높은 텍스트 개수 : {len(docs)}")
# print("-" * 50)
# print(f"유사도 높은 텍스트 중 첫번째 텍스트 출력 : {docs[0]}")
# print("-" * 50)
# print("<출처>")
# for doc in docs:
#   print(doc.metadata["source"])


prompt = PromptTemplate.from_template(
    """당신은 질문-답변(Question-Answering)을 수행하는 친절한 AI 어시스턴트입니다. 당신의 임무는 주어진 문맥(context) 에서 주어진 질문(question) 에 답하는 것입니다.
검색된 다음 문맥(context) 을 사용하여 질문(question) 에 답하세요. 만약, 주어진 문맥(context) 에서 답을 찾을 수 없다면, 답을 모른다면 `주어진 정보에서 질문에 대한 정보를 찾을 수 없습니다` 라고 답하세요.
한글로 답변해 주세요. 단, 기술적인 용어나 이름은 번역하지 않고 그대로 사용해 주세요. 답변은 3줄 이내로 요약해 주세요.


#Question:
{question}


#Context:
{context}


#Answer:"""
)

llm=ChatOpenAI(model_name="gpt-4o-mini", temperature=0)
# 체인을 생성합니다.
# RunnablePassthrough() : 데이터를 그대로 전달하는 역할. invoke 메서드를 통해 입력된 데이터를 그대로 반환. (평문화 안됨)
# StrOutputParser() : LLM 이나 ChatModel에서 나오는 언어 모델의 출력을 문자열 형식으로 변환
rag_chain = (
    {"context": retriever, "question": RunnablePassthrough()}
    | prompt
    | llm
    | StrOutputParser()
)

# print("질문 : ", sys.argv[1])
# answer = rag_chain.stream("신혼부부를 위한 정책을 알려주세요")
answer = rag_chain.stream(sys.argv[1])
stream_response(answer)

# print("응답 : ",answer)