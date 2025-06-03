"""Python program to read in Irish place names from PDF and create a data
set with the aims of improving speech recognition and synthesising data
Plan: 
1. get list of file names in placenames filder
2. for each file
    - get region (county/gaeltacht)
    - is_dréacht (draft) 
    - read contents of file PDF -> string NB UTF-8
    - placenames {"region": []} = extract_placenames(file_string, is_dréacht)
    
    # seems to be two main types of file, draft and not draft,
    # most files have columns with en | ga names
    # NB: remove puntuation or anything within it, some like to add info re-parish
    # etc which probably not important for speech recognitio/ data syntesis
    extract_placenames(file_string)
        if is_dréacht:
        else:
              """

import os
import fitz
import re


# function that takes directory path as input and returns a list the files within
def file_names_from_dir(dir_path):
    # get list and return with error handling - code by GPT
    try:
        # List all entries in the directory
        all_entries = os.listdir(dir_path)
        # Filter only files
        file_list = [
            entry
            for entry in all_entries
            if os.path.isfile(os.path.join(dir_path, entry))
        ]
        return file_list
    except FileNotFoundError:
        print(f"The directory {dir_path} does not exist.")
        return []
    except PermissionError:
        print(f"Permission denied to access {dir_path}.")
        return []


def is_valid_name(s):
    if s == "":
        return False
    if re.search(r"[A-Z]{3}", s):
        return False 
    if re.search(r"\d", s):
        return False
    else:
        return True


def clean_name_brackets(s):
    """
    Remove any bracketed text ( […] or (…) ) and strip whitespace.
    E.g. "Adamstown [ED:Garristown]" → "Adamstown"
    """
    # Remove anything in square brackets, including the brackets themselves
    s = re.sub(r"\[.*?\]", "", s)
    # Remove anything in parentheses, including the parentheses themselves
    s = re.sub(r"\(.*?\)", "", s)
    return s.strip()
def handle_or_case(en_name, ga_name):
    # Handle cases with "or" or "nó" (Irish for "or")
    en_names = en_name.split(" or ")
    ga_names = ga_name.split(" nó ")
    # get first name
    en_name = clean_name_brackets(en_names[0])
    ga_name = clean_name_brackets(ga_names[0])

    return en_name, ga_name
def is_number(s):
    return re.fullmatch(r"\d+\.?\s*$", s) is not None

def pdf_to_place_names_list(fn_name_pdf):
    set_of_tuples = set()
    """Extract all English-Irish placename pairs from a PDF."""
    place_name_pairs = []
    try:
        doc = fitz.open(fn_name_pdf)
        print("||||||||||||||||||||")
        print(fn_name_pdf)
        for page in doc:
            lines = page.get_text().split("\n")
            #print(lines)
            i = 0
            while i < len(lines) - 2:
                if (
                    is_number(lines[i])
                    and is_valid_name(lines[i + 1])
                    and is_valid_name(lines[i + 2])
                    and is_number(lines[i+3])
                ):
                    en_name = lines[i + 1].strip()
                    ga_name = lines[i + 2].strip()

                    en_name = clean_name_brackets(en_name)
                    ga_name = clean_name_brackets(ga_name)

                    if re.search(r"\[", en_name) and re.search(r"\]", ga_name):
                        i += 3
                        continue
       
                    # keep it simple and just keep the first name
                    if (" or " in en_name) or (" nó " in ga_name):
                        en_name, ga_name = handle_or_case(en_name, ga_name)
                        if is_valid_name(en_name) and is_valid_name(ga_name) and (en_name, ga_name) not in set_of_tuples:
                            set_of_tuples.add((en_name, ga_name))
                            if not re.search(r"[\[\]\(\)]", en_name) and not re.search(r"[\[\]\(\)]", ga_name):
                                place_name_pairs.append((en_name, ga_name))
                        i += 3
                    else:       
                        if is_valid_name(en_name) and is_valid_name(ga_name) and (en_name, ga_name) not in set_of_tuples:
                            set_of_tuples.add((en_name, ga_name))
                            if not re.search(r"[\[\]\(\)]", en_name) and not re.search(r"[\[\]\(\)]", ga_name):
                                place_name_pairs.append((en_name, ga_name))
                        i += 3
                else:
                    i += 1
    except Exception as e:
        print(f"Error processing {fn_name_pdf}: {e}")
    return place_name_pairs


# between logainmneacha and YYYY and an-tordu-logainmneacha-contae-laoise-2018-dreacht
def get_area_from_f_name(f_name):
    # remove ".pdf"
    f_name = f_name.replace(".pdf", "")
    f_name_split = f_name.split("-")
    try:
        f_name_split = f_name.split("-")
        contae_idx = f_name_split.index("logainmneacha")
        year_idx = next(
            i
            for i in range(contae_idx + 1, len(f_name_split))
            if re.fullmatch(r"\d{4}", f_name_split[i])
        )
        area_parts = f_name_split[contae_idx + 1 : year_idx]
        area = " ".join(area_parts)
        return area
    except:
        return "err"
