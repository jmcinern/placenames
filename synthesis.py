import json
import pandas as pd
from tqdm import tqdm
from langchain.prompts import ChatPromptTemplate, FewShotChatMessagePromptTemplate
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
import openai
from feature_matrix import IrishFeatureMatrix

# Load secrets
with open("secrets.json", "r", encoding="utf-8") as f:
    secrets = json.load(f)[0]

openai.api_key = secrets["open_ai"]

# Initialize feature matrix
irish_matrix = IrishFeatureMatrix()

# Load examples from JSON
with open("examples.json", "r", encoding="utf-8") as f:
    examples = json.load(f)

# Load system message
with open("system_message.txt", "r", encoding="utf-8") as f:
    system_message = f.read()

def format_features(feature_row):
    """Format feature combination for the prompt"""
    return f"Person: {feature_row['person']}, Verb: {feature_row['verb']}, Preposition: {feature_row['preposition']}, Case: {feature_row['case']}, Tense: {feature_row['tense']}"

# Create example prompt template
example_prompt = ChatPromptTemplate.from_messages([
    ("human", "Placename: {placename}"),
    ("assistant", "{sentence}")
])

# Create few-shot prompt with examples
few_shot_prompt = FewShotChatMessagePromptTemplate(
    example_prompt=example_prompt,
    examples=examples,
)

# Create the full prompt template
full_prompt = ChatPromptTemplate.from_messages([
    ("system", system_message),
    few_shot_prompt,
    ("human", "Placename: {placename}\nTense: {tense}\nFeatures: {features}")
])

# Initialize model
claude = ChatAnthropic(
    model="claude-sonnet-4-20250514",
    temperature=0.9,
    api_key=secrets["anthropic"]
)

# Create chains
chain_claude = full_prompt | claude

def generate_sentence_with_chain(chain, place_name, model_label):
    """Generate one sentence for a placename with random features"""
    # Sample random features (including tense)
    features = irish_matrix.sample_random_combination()
    features_text = format_features(features)
    
    # Generate sentence
    resp = chain.invoke({
        "placename": place_name,
        "tense": features['tense'],
        "features": features_text
    })
    
    sentence = resp.content.strip()
    
    print(f"{place_name} ({model_label}): {sentence}")
    print(f"Features: {features_text}\n")
    
    return {
        "placename": place_name,
        "sentence": sentence,
        "model": model_label,
        "person": features['person'],
        "verb": features['verb'],
        "preposition": features['preposition'],
        "case": features['case'],
        "tense": features['tense']
    }

# Main execution
if __name__ == "__main__":
    # Load placenames
    csv_path = "./placenames.csv"
    df = pd.read_csv(csv_path, encoding='utf-8')
    
    # Select first 20 placenames
    placenames_list = df['Logainm'].head(100).tolist()
    
    print(f"Generating sentences for {len(placenames_list)} placenames...")
    print(f"Feature matrix has {len(irish_matrix.feature_matrix):,} possible combinations")
    print()
    
    rows = []
    
    # Generate sentences for each placename with both models
    for pn in tqdm(placenames_list, desc="Processing placenames"):
        # Generate with Claude
        try:
            result_claude = generate_sentence_with_chain(chain_claude, pn, claude.model)
            rows.append(result_claude)
        except Exception as e:
            print(f"Error with Claude for {pn}: {e}")
    
    # Create DataFrame
    results_df = pd.DataFrame(rows)
    
    # Save results
    output_csv_path = f"./synthetic_sentences_{claude.model}.csv"
    results_df.to_csv(output_csv_path, index=False, encoding='utf-8-sig')
    
    print(f"\nResults saved to {output_csv_path}")
    print(f"Generated {len(results_df)} sentences total")
    print(f"Models used: {results_df['model'].value_counts().to_dict()}")
    print(f"Tenses used: {results_df['tense'].value_counts().to_dict()}")