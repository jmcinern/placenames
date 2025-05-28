from pdf_to_data_set import file_names_from_dir, pdf_to_place_names_list, get_area_from_f_name
def main():
    # get list of files
    directory = "./placenames/placenames"
    files = file_names_from_dir(directory)
    #print("Files found:", files)

    #{"area": [(en, ga).....]}
    list_of_place_names_en_ga = dict()
    # for each file
    for f_name in files:
        # between logainmneacha and YYYY and an-tordu-logainmneacha-contae-laoise-2018-dreacht
        area = get_area_from_f_name(f_name)
        f_path_PDF = directory+"/"+f_name
        #{"area": [(en, ga).....]}
        list_of_place_names_en_ga[area] =  pdf_to_place_names_list(f_path_PDF)
    
    
    print(list_of_place_names_en_ga)

if __name__ == "__main__":
    main()
