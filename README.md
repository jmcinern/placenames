# Irish Placenames Extractor

This project reads Irish place names from PDF files and creates a structured dataset with the aim of improving speech recognition and data synthesis. The overview was created with the help of copilot.

## Overview

- **PDF Extraction & Processing:**  
  The script reads PDFs from a designated folder, extracting raw text containing placenames.

- **Text Cleaning & Parsing:**  
  Utilizes regular expressions to remove unwanted punctuation and extraneous text, isolating the valid Irish placename pairs.

- **Dataset Creation:**  
  Aggregates cleaned placename pairs into a structured CSV format for further processing or analysis.

## Project Structure

- **main.py:**  
  Entry point for scanning the PDF directory, extracting placename pairs, and generating the CSV dataset.

- **pdf_to_data_set.py:**  
  Contains core functions for:
  - Listing PDF file names,
  - Parsing each PDF to extract placename data,
  - Handling region-specific extraction and formatting.

  - **test_placenames.py**
    - Different PDF formats identified and analysed
    - Manually exctracted sample placenames for each PDF type
    - Edge cases identified:
      
        - With " or " indicating multple names
        - Line breaks
        - Multiline
        - Standard and square brackets
          
## Getting Started

1. **Setup:**  
   Place your source PDF files with Irish placenames in the `./placenames/placenames` folder.

2. **Installation:**  
   Install the required libraries as listed in the [requirements.txt](./requirements.txt).

3. **Run the Script:**  
   Execute the main script to generate the dataset:
   ```bash
   python main.py

4. Output:
The output CSV file will contain the cleaned and structured placename pairs ready for further use. 
