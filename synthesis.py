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
from tqdm import tqdm

csv_path = "./placenames.csv"
df = pd.read_csv(csv_path,encoding='utf-8')
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
placenames = df['Logainm'].head(2).tolist()
print(placenames)

# 3. Set up promp template for sentence generation, Langchain etc
example_prompt = ChatPromptTemplate.from_messages([
    ("human", "Placename: {placename}?"),
    ("assistant", "{sentences}")
])

#read ./examples.json with "placename" and "sentences" keys
import json
with open("./examples.json", "r") as f:
    examples = json.load(f)

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

with open("./secrets.json", "r") as f:
    secrets = json.load(f)

openai.api_key = secrets[0]["open_ai"]

# mini = bigger than nano
gpt_nano = ChatOpenAI(
    model_name="gpt-4.1-mini",
    temperature=0.9,
    openai_api_key=openai.api_key)

chain_nano = full_prompt | gpt_nano

# 4. generate 20 X 5 sentences
def generate_sentences(place_name):
    response = chain_nano.invoke({"question": f"Placename: {place_name}"})
    return response.content

# store resulting sentences in a DataFrame
results_df = pd.DataFrame(columns=['placename', 'model', 'Aimsir Cháite', 'Aimsire Láithreach', 'Aimsir Fháistineach', 'Aimsir Gnáth Cháite', "Aimsir Gnáth Láithreach"])

placenames_list = []
model_list = []
aimsir_chaite_list = []
aimsir_laithreach_list = []
aimsir_fhastineach_list = []
aimsir_gnath_chaite_list = []
aimsir_gnath_laithreach_list = []

for pn in tqdm(placenames):
    placenames_list.append(pn)
    model_list.append("gpt-4.1-mini")

    # generate synthetic sentences
    response = generate_sentences(pn)

    sentences = response.split('\n')
    aimsir_chaite_list.append(sentences[0])
    aimsir_laithreach_list.append(sentences[1])
    aimsir_fhastineach_list.append(sentences[2])
    aimsir_gnath_chaite_list.append(sentences[3])
    aimsir_gnath_laithreach_list.append(sentences[4])

# add the results to the DataFrame
results_df['placename'] = placenames_list
results_df['model'] = model_list
results_df['Aimsir Cháite'] = aimsir_chaite_list
results_df['Aimsire Láithreach'] = aimsir_laithreach_list
results_df['Aimsir Fháistineach'] = aimsir_fhastineach_list
results_df['Aimsir Gnáth Cháite'] = aimsir_gnath_chaite_list
results_df['Aimsir Gnáth Láithreach'] = aimsir_gnath_laithreach_list

# write the DataFrame to a CSV file
output_csv_path = "./synthetic_sentences.csv"
results_df.to_csv(output_csv_path, index=False, encoding='utf-8-sig')
print(f"Results saved to {output_csv_path}")




