import json
import pandas as pd
from tqdm import tqdm
from langchain.prompts import ChatPromptTemplate, FewShotChatMessagePromptTemplate
from langchain_anthropic import ChatAnthropic
import random
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading
import os

# Configuration flags
do_sampling = True
just_sample = True  # NEW FLAG: Use simple system message without feature matrix
n_generated = 100

# Rate limiting configuration
BATCH_SIZE = 40  # Stay safely under 50 RPM
BATCH_DELAY = 65  # Seconds between batches

# openai.api_key = secrets["open_ai"]

"""
# Initialize feature matrix (only if not using just_sample)
if not just_sample:
    irish_matrix = IrishFeatureMatrix()
  """

# Load examples from JSON
with open("examples.json", "r", encoding="utf-8") as f:
    examples = json.load(f)

# Load appropriate system message based on mode
if just_sample:
    with open("simple_system_message.txt", "r", encoding="utf-8") as f:
        system_message = f.read()
else:
    with open("system_message.txt", "r", encoding="utf-8") as f:
        system_message = f.read()

# Global list to store previously generated sentences (thread-safe)
previous_sentences = []
sentence_lock = threading.Lock()


def add_to_sentence_history(sentence):
    """Add a sentence to the history of previously generated sentences (thread-safe)"""
    global previous_sentences
    with sentence_lock:
        previous_sentences.append(sentence)


def sample_previous_sentences(n=10):
    """Sample n sentences from previously generated sentences (thread-safe)"""
    global previous_sentences
    with sentence_lock:
        if len(previous_sentences) == 0:
            return []
        elif len(previous_sentences) <= n:
            return previous_sentences.copy()
        else:
            return random.sample(previous_sentences, n)


def format_features(feature_row):
    """Format feature combination for the prompt (only used when not just_sample)"""
    return f"Person: {feature_row['person']}, Verb: {feature_row['verb']}, Preposition: {feature_row['preposition']}, Case: {feature_row['case']}, Tense: {feature_row['tense']}"


def format_previous_sentences(sentences):
    """Format previous sentences for inclusion in prompt"""
    if not sentences:
        return ""

    formatted = "\n\nPREVIOUSLY GENERATED SENTENCES:\n"
    for i, sentence in enumerate(sentences, 1):
        formatted += f"{i}. {sentence}\n"
    return formatted


# Create example prompt template
example_prompt = ChatPromptTemplate.from_messages(
    [("human", "Placename: {placename}"), ("assistant", "{sentence}")]
)

# Create few-shot prompt with examples
few_shot_prompt = FewShotChatMessagePromptTemplate(
    example_prompt=example_prompt,
    examples=examples,
)


# Create the full prompt template (with conditional previous sentences)
def create_prompt_template(include_previous=False, simple_mode=False):
    if simple_mode:
        # Simple mode without features
        if include_previous:
            return ChatPromptTemplate.from_messages(
                [
                    ("system", system_message),
                    few_shot_prompt,
                    (
                        "human",
                        "Placename: {placename}\n sample of previous sentences: {previous_sentences}",
                    ),
                ]
            )
        else:
            return ChatPromptTemplate.from_messages(
                [
                    ("system", system_message),
                    few_shot_prompt,
                    ("human", "Placename: {placename}"),
                ]
            )
    else:
        # Full mode with features
        if include_previous:
            return ChatPromptTemplate.from_messages(
                [
                    ("system", system_message),
                    few_shot_prompt,
                    (
                        "human",
                        "Placename: {placename}\nTense: {tense}\nFeatures: {features}{previous_sentences}",
                    ),
                ]
            )
        else:
            return ChatPromptTemplate.from_messages(
                [
                    ("system", system_message),
                    few_shot_prompt,
                    (
                        "human",
                        "Placename: {placename}\nTense: {tense}\nFeatures: {features}",
                    ),
                ]
            )


def get_anthropic_api_key():
    """Get Anthropic API key from environment or secrets file"""
    # Try environment variable first
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if api_key:
        return api_key

    # Try secrets file as fallback
    try:
        with open("secrets.json", "r", encoding="utf-8") as f:
            secrets = json.load(f)[0]
            return secrets["anthropic"]
    except FileNotFoundError:
        raise FileNotFoundError(
            "No Anthropic API key found. Either:\n"
            "1. Set ANTHROPIC_API_KEY environment variable, or\n"
            "2. Create secrets.json file"
        )


CLAUDE_MODEL = (
    "claude-3-haiku-20240307"  # "claude-3-5-haiku-20241022" # "claude-3-haiku-20240307"
)


def create_claude_instance():
    """Create a new Claude instance for each thread"""
    return ChatAnthropic(
        model=CLAUDE_MODEL,  # "claude-3-5-haiku-20241022",
        temperature=0.9,
        api_key=get_anthropic_api_key(),
    )


def generate_sentence_for_placename(args):
    """Generate sentence for a single placename (designed for parallel execution)"""
    placename, use_sampling, simple_mode = args

    # Create a new Claude instance for this thread
    claude = create_claude_instance()

    # Create chain
    if use_sampling:
        chain = (
            create_prompt_template(include_previous=True, simple_mode=simple_mode)
            | claude
        )
    else:
        chain = (
            create_prompt_template(include_previous=False, simple_mode=simple_mode)
            | claude
        )

    try:
        # Prepare the invoke parameters
        invoke_params = {"placename": placename}

        # Add features only if not in simple mode
        """
        if not simple_mode:
            features = irish_matrix.sample_random_combination()
            features_text = format_features(features)
            invoke_params["tense"] = features['tense']
            invoke_params["features"] = features_text
        """
        # Add previous sentences if sampling is enabled
        if use_sampling:
            previous = sample_previous_sentences(10)
            invoke_params["previous_sentences"] = format_previous_sentences(previous)

        # Generate sentence
        resp = chain.invoke(invoke_params)
        sentence = resp.content.strip()
        # Deal with case where Claude returns multiple sentences
        if "\n" in sentence:
            sentence = sentence.split("\n")[0].strip()
            sentence = " ".join(sentence.split())

        # Add to sentence history if sampling is enabled
        if use_sampling:
            add_to_sentence_history(sentence)

        print(f"{placename} ({claude.model}): {sentence}")
        """
        if not simple_mode:
            print(f"Features: {format_features(features)}")
        """
        print()

        # Return appropriate dictionary based on mode
        base_result = {
            "placename": placename,
            "sentence": sentence,
            "model": claude.model,
        }
        """
        if not simple_mode:
            base_result.update({
                "person": features['person'],
                "verb": features['verb'],
                "preposition": features['preposition'],
                "case": features['case'],
                "tense": features['tense']
            })
            """

        return base_result

    except Exception as e:
        print(f"Error with {placename}: {e}")
        return None


def process_in_batches(placenames_list, batch_size=BATCH_SIZE, batch_delay=BATCH_DELAY):
    """Process placenames in batches to respect rate limits"""

    batches = [
        placenames_list[i : i + batch_size]
        for i in range(0, len(placenames_list), batch_size)
    ]

    all_results = []

    for batch_num, batch in enumerate(batches):
        print(f"\n{'='*60}")
        print(
            f"Processing batch {batch_num + 1}/{len(batches)} ({len(batch)} placenames)"
        )
        print(f"Total processed so far: {len(all_results)}/{len(placenames_list)}")
        print(f"{'='*60}")

        # Process this batch
        args_list = [(pn, do_sampling, just_sample) for pn in batch]
        batch_results = []

        # Use limited number of workers for each batch
        max_workers = min(len(batch), 8)

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_placename = {
                executor.submit(generate_sentence_for_placename, args): args[0]
                for args in args_list
            }

            for future in tqdm(
                as_completed(future_to_placename),
                total=len(batch),
                desc=f"Batch {batch_num + 1}",
            ):
                result = future.result()
                if result is not None:
                    batch_results.append(result)

        all_results.extend(batch_results)

        # Save intermediate results after each batch
        if batch_results:
            intermediate_df = pd.DataFrame(all_results)
            mode_suffix = "_simple" if just_sample else "_features"
            sampling_suffix = "_sampling" if do_sampling else ""
            intermediate_csv = f"./synthesis/synthetic_sentences_{CLAUDE_MODEL}{mode_suffix}{sampling_suffix}_batch_{batch_num + 1}.csv"
            intermediate_df.to_csv(intermediate_csv, index=False, encoding="utf-8-sig")
            print(f"Intermediate results saved to {intermediate_csv}")

        # Wait between batches (except for the last one)
        if batch_num < len(batches) - 1:
            print(f"\nWaiting {batch_delay} seconds before next batch...")
            print(
                f"Progress: {len(all_results)}/{len(placenames_list)} completed ({len(all_results)/len(placenames_list)*100:.1f}%)"
            )

            # Countdown timer
            for remaining in range(batch_delay, 0, -1):
                print(
                    f"\rNext batch starts in: {remaining:02d} seconds",
                    end="",
                    flush=True,
                )
                time.sleep(1)
            print()  # New line after countdown

    return all_results


# Main execution
if __name__ == "__main__":
    print("=== DEBUG START ===")
    
    # Test API key
    try:
        api_key = get_anthropic_api_key()
        print(f"✅ API key found: {api_key[:10]}...{api_key[-4:]}")
    except Exception as e:
        print(f"❌ API key error: {e}")
        exit(1)
    
    # Test file loading
    try:
        with open("examples.json", "r", encoding="utf-8") as f:
            examples = json.load(f)
        print(f"✅ Examples loaded: {len(examples)} examples")
    except Exception as e:
        print(f"❌ Examples error: {e}")
        exit(1)
    
    # Test single API call
    try:
        claude = create_claude_instance()
        print(f"✅ Claude instance: {claude.model}")
        
        # Test simple prompt
        test_resp = claude.invoke("Say 'test successful' in Irish")
        print(f"✅ Test response: {test_resp.content}")
    except Exception as e:
        print(f"❌ API call error: {e}")
        exit(1)
    
    print("=== DEBUG END ===")
    
    # Test API key first
    try:
        test_key = get_anthropic_api_key()
        print(f"API key found: {test_key[:10]}...{test_key[-4:]}")

        # Test a single API call
        test_claude = create_claude_instance()
        print(f"Claude instance created successfully: {test_claude.model}")
    except Exception as e:
        print(f"SETUP ERROR: {e}")
        exit(1)

    # ... rest of your code
    # Load placenames
    csv_path = "./placenames.csv"
    df = pd.read_csv(csv_path, encoding="utf-8")

    # Select first n_generated placenames
    placenames_list = df["Logainm"].tolist()

    print(f"Generating sentences for {len(placenames_list)} placenames...")
    print(f"Batch size: {BATCH_SIZE} placenames per batch")
    print(f"Batch delay: {BATCH_DELAY} seconds between batches")
    print(
        f"Estimated total time: {len(placenames_list)//BATCH_SIZE * BATCH_DELAY / 60:.1f} minutes"
    )
    """if not just_sample:
        print(f"Feature matrix has {len(irish_matrix.feature_matrix):,} possible combinations")
        """
    print(f"Mode: {'SIMPLE SAMPLING' if just_sample else 'FEATURE MATRIX'}")
    print(f"Sentence sampling: {'ENABLED' if do_sampling else 'DISABLED'}")
    print()

    # Process in rate-limited batches
    rows = process_in_batches(
        placenames_list, batch_size=BATCH_SIZE, batch_delay=BATCH_DELAY
    )

    # Create final DataFrame
    results_df = pd.DataFrame(rows)

    # Create output filename based on flags
    mode_suffix = "_simple" if just_sample else "_features"
    sampling_suffix = "_sampling" if do_sampling else ""
    output_csv_path = f"./synthesis/synthetic_sentences_claude_{CLAUDE_MODEL}_{mode_suffix}{sampling_suffix}_final.csv"
    results_df.to_csv(output_csv_path, index=False, encoding="utf-8-sig")

    print(f"\n{'='*60}")
    print("FINAL RESULTS")
    print(f"{'='*60}")
    print(f"Final results saved to {output_csv_path}")
    print(f"Generated {len(results_df)} sentences total")
    print(
        f"Success rate: {len(results_df)}/{len(placenames_list)} ({len(results_df)/len(placenames_list)*100:.1f}%)"
    )
    print(f"Models used: {results_df['model'].value_counts().to_dict()}")

    if not just_sample:
        print(f"Tenses used: {results_df['tense'].value_counts().to_dict()}")

    if do_sampling:
        print(f"Total sentences in history: {len(previous_sentences)}")
