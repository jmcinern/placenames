# Irish Placename Sentence Synthesis

A Python tool for generating synthetic Irish language sentences containing placenames using Claude AI, with advanced sampling mechanisms to ensure linguistic variation.

# 📊 The Dataset

## Download & Access

**📁 Dataset Repository**: https://github.com/jmcinern/placenames/tree/main/big_data

The complete dataset of 28,017 AI-generated Irish sentences with placenames is available for download as CSV files.

### Dataset Schema

| Column | Type | Description |
|--------|------|-------------|
| `placename` | string | Irish placename (logainm) |
| `sentence` | string | Generated Irish sentence containing the placename |
| `model` | string | AI model used for generation |

### Quick Start

```python
import pandas as pd

# Load the dataset
df = pd.read_csv('path/to/dataset.csv')

# Extract sentences for language processing
sentences = df['sentence'].tolist()

# Filter by specific model
claude_sentences = df[df['model'] == 'claude-3-haiku-20240307']['sentence']

# Get placename-sentence pairs
pairs = df[['placename', 'sentence']].values
```

## Sample Data

| Irish Placename | Generated Sentence | Model |
|----------------|-------------------|--------|
| Cill Riáin | Bíonn ceolchoirmeacha traidisiúnta ar siúl i gCill Riáin gach Samhain. | claude-3-haiku-20240307 |
| Leic Éime | Tá gréasán nua siúlóidí cruthaithe ag muintir Leic Éime le blianta beaga anuas. | claude-3-haiku-20240307 |
| Leitir Beara | Tógadh foirgneamh nua suntasach i Leitir Beara an samhradh seo caite. | claude-3-haiku-20240307 |
| Leitir Ceanainn | Buaileann mé lena chairde i Leitir Ceanainn gach deireadh seachtaine. | claude-3-haiku-20240307 |
| Paiteagó | Eagraítear seisiúin cheoil thraidisiúnta i bPaiteagó go rialta. | claude-3-haiku-20240307 |

## Citation

If you use this tool or dataset in your research, please cite:

```bibtex
@software{irish_placename_synthesis,
  title={Irish Placename Sentence Synthesis},
  author={Joseph McInerney},
  year={2025},
  url={https://github.com/jmcinern/placenames}
}
```
## Overview

This project generates diverse Irish language sentences incorporating Irish placenames (logainmneacha) using Anthropic's Claude language model. The system uses sophisticated sampling techniques to maximize morphological, syntactical, and thematic variation while avoiding repetition.

## Features

### 🎯 **Dual Generation Modes**
- **Simple Sampling Mode**: Generates varied sentences using contextual sampling from previous outputs
- **Feature Matrix Mode**: Uses structured grammatical features (person, verb, preposition, case, tense) for systematic variation

### 🔄 **Advanced Sampling System**
- **Repetition Avoidance**: Randomly samples from previously generated sentences to inform variation
- **Thread-Safe Processing**: Concurrent sentence generation with shared sentence history
- **Progressive Context**: Uses up to 10 previous sentences to guide new generation

### ⚡ **Performance & Scalability**
- **Batch Processing**: Respects API rate limits (40 requests per batch, 65-second delays)
- **Parallel Processing**: Multi-threaded execution for faster generation
- **Rate Limiting**: Built-in safeguards for API usage compliance
- **Progress Tracking**: Real-time batch progress and completion estimates

### 🛡️ **Production Ready**
- **Environment Variable Support**: Secure API key management for deployment
- **HPC/Slurm Compatible**: Ready for high-performance computing environments
- **Intermediate Saves**: Automatic backup after each batch to prevent data loss
- **Error Resilience**: Continues processing despite individual failures

## Installation

### Prerequisites
- Python 3.8+
- Anthropic API key

### Setup
```bash
# Clone the repository
git clone https://github.com/jmcinern/placenames.git
cd placenames

# Install dependencies
pip install -r requirements.txt

# Set up API key (choose one method)
# Method 1: Environment variable (recommended for servers)
export ANTHROPIC_API_KEY="your_anthropic_key_here"

# Method 2: Local secrets file (for development)
echo '[{"anthropic": "your_anthropic_key_here"}]' > secrets.json
```

## Usage

### Basic Configuration

Edit the configuration flags in `synthesis.py`:

```python
# Configuration flags
do_sampling = True      # Enable/disable sampling mechanism
just_sample = True      # True = simple mode, False = feature matrix mode
n_generated = 100       # Number of sentences to generate

# Rate limiting
BATCH_SIZE = 40         # Requests per batch (stay under 50 RPM)
BATCH_DELAY = 65        # Seconds between batches
```


## Input Data

### Required Files

1. **`placenames.csv`**: CSV file containing Irish placenames
   ```csv
   Logainm
   Baile Átha Cliath
   Corcaigh
   Gaillimh
   ```

2. **`examples.json`**: Few-shot examples for the model
   ```json
   [
     {
       "placename": "Baile an Dúna",
       "sentence": "Tháinig muid go Baile an Dúna le haghaidh an fhéile."
     },
     {
       "placename": "An Teach Mór", 
       "sentence": "Bhíodh sé ag obair in Teach Mór le blianta."
     },
     {
       "placename": "Caisleán Aircín",
       "sentence": "Tógfar eastáit nua tithíochta i gCaisleán Aircín an bhliain seo chugainn."
     }
   ]
   ```

3. **`simple_system_message.txt`**: System prompt for simple mode
   ```
   You are an Irish language model. Generate 1 Irish sentence containing the given placename.
   Return only the Irish sentence.
   The following sentences are sentences that you have already generated, in order to maximise 
   statistical variation in language. Generate a new sentence that differs from these sentences 
   in terms of VERB, TENSE (past, present, future, habitual, conditional), STRUCTURE, THEME. 
   Remember, 1 sentence per place name and vary verb, avoid using verb from previous sentences.
   ```

## Output

### File Structure
The system generates multiple output files:

```
synthetic_sentences_[model]_[mode]_[sampling]_batch_[N].csv    # Intermediate results
synthetic_sentences_[model]_[mode]_[sampling]_final.csv       # Final results
```

### Output Format
```csv
placename,sentence,model
Baile Átha Cliath,"Rachaidh mé go Baile Átha Cliath amárach.",claude-3-haiku-20240307
Corcaigh,"Tá mo dheartháir ina chónaí i gCorcaigh.",claude-3-haiku-20240307
```

## Generation Modes

### Simple Sampling Mode (`just_sample = True`)
- Uses basic system prompt
- Relies on sampling from previous sentences for variation
- Faster and more cost-effective
- Good for exploratory generation

### Feature Matrix Mode (`just_sample = False`)
- Uses structured grammatical constraints
- Systematic coverage of linguistic features
- More predictable variation patterns
- Requires `feature_matrix.py` and `system_message.txt`

## Performance

### Timing Estimates
- **100 placenames**: ~7 minutes (3 batches)
- **1000 placenames**: ~27 minutes (25 batches)
- **Rate limit compliance**: 40 requests/batch, 65s delays

### Resource Requirements
- **Memory**: 2-4GB recommended
- **CPU**: Scales with available cores (up to 8 threads per batch)
- **Network**: Stable internet for API calls

## API Rate Limiting

The system automatically handles Anthropic's rate limits:
- **50 requests per minute** limit
- **40 requests per batch** (safety margin)
- **65-second delays** between batches
- **Automatic retry logic** for temporary failures

## Monitoring

### Progress Tracking
```
Processing batch 3/25 (40 placenames)
Total processed so far: 80/1000
Progress: 80/1000 completed (8.0%)
Next batch starts in: 65 seconds
```

### Log Files (HPC)
- `synthesis_[jobid].out`: Standard output and progress
- `synthesis_[jobid].err`: Error messages and warnings

## Troubleshooting

### Common Issues

1. **API Key Error**
   ```
   No Anthropic API key found
   ```
   **Solution**: Set `ANTHROPIC_API_KEY` environment variable or create `secrets.json`

2. **Rate Limit Exceeded**
   ```
   Rate limit exceeded
   ```
   **Solution**: Increase `BATCH_DELAY` or decrease `BATCH_SIZE`

3. **Missing Files**
   ```
   FileNotFoundError: placenames.csv
   ```
   **Solution**: Ensure all required input files are present

