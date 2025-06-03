import csv
from pdf_to_data_set import (
    file_names_from_dir,
    pdf_to_place_names_list,
    get_area_from_f_name,
)


def main():
    directory = "./placenames/placenames"
    files = file_names_from_dir(directory)

    rows = []
    place_names = {}
    for f_name in files:
        area = get_area_from_f_name(f_name)
        # print(area)
        f_path_PDF = directory + "/" + f_name
        place_names[area] = pdf_to_place_names_list(
            f_path_PDF
        )  # List of (en, ga) tuples
    rows = []
    for area in place_names:
        for en, ga in place_names[area]:
            rows.append((area, ga))

    # Write to CSV
    with open("placenames.csv", "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["Ceantar", "Logainm"])
        for row in rows:
            writer.writerow(row)


if __name__ == "__main__":
    main()
