'''Python program to read in Irish place names from PDF and create a data
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
              '''
