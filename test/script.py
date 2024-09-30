import os
import pandas as pd
import tiktoken

domain = "openai.com"
texts=[]

###############################################################################
#    remove_newlines
#    줄바꿈, 공백 정리
###############################################################################
def remove_newlines(serie):
  serie = serie.str.replace('\n', ' ')
  serie = serie.str.replace('\\n', ' ')
  serie = serie.str.replace('  ', ' ')
  serie = serie.str.replace('  ', ' ')
  return serie


# 원본 텍스트 > csv 변환
for file in os.listdir(f"text/{domain}/"):
  with open(f"text/{domain}/{file}", "r", encoding="utf-8") as f:
    text = f.read()
    # 처음 11줄과 마지막 4줄을 생략하고, -, _, #update를 공백으로 바꿉니다.
    texts.append((file[11:-4].replace('-',' ').replace('_', ' ').replace('#update',''), text))

df = pd.DataFrame(texts, columns = ['fname', 'text'])
df['text'] = f"{df.fname}. {remove_newlines(df.text)}"
df.to_csv('processed/scraped.csv')
df.head()

# 임베딩 Load the cl100k_base tokenizer which is designed to work with the ada-002 model
tokenizer = tiktoken.get_encoding('cl100k_base')
df 