'''
1. Read in CSV with place names
2. get first 20 placenames
3. Set up promp template for sentence generation, Langchain etc
4. generate 20 X 5 sentences 
    a. Claude 4 vs Nano
    b. Sampling method: top_p, temperature, previous examples.
5. examine the sentences
6. save the sentences to a CSV file
'''

# 1. Read in CSV with place names
import pandas as pd
from langchain.prompts import ChatPromptTemplate, FewShotChatMessagePromptTemplate
from langchain_openai import ChatOpenAI
import openai

csv_path = "./placenames.csv"
df = pd.read_csv(csv_path)
# print(df.head())

'''
                Ceantar               Logainm
0  ceantair ghaeltachta  Sruthán Áth na Circe
1  ceantair ghaeltachta           An Eatharla
2  ceantair ghaeltachta     Aill an Bhlácaigh
3  ceantair ghaeltachta         Aill an Phúca
4  ceantair ghaeltachta      Aill an Chlogáis
'''

# 2. get first 20 placenames
placenames = df['Logainm'].head(20).tolist()
print(placenames)

# 3. Set up promp template for sentence generation, Langchain etc
example_prompt = ChatPromptTemplate.from_messages(
[('human', '{question}?'), ('ai', '{answer}\n')]
)

few_shot_prompt = FewShotChatMessagePromptTemplate(
    examples=examples,
    example_prompt=example_prompt,
)

with open ("./system_message.txt", "r") as f:
    system_message = f.read()

full_prompt = ChatPromptTemplate.from_messages([
  ("system", system_message),
  few_shot_prompt,
  ("human", "{question}"),
])

# mini = bigger than nano
gpt_mini = ChatOpenAI(
    model_name="gpt-4.1-mini",
    temperature=0.9,
    openai_api_key=openai.api_key)

chain_mini = full_prompt | gpt_mini