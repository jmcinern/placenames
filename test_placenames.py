# tests/test_placenames.py
import os
import pytest

from pdf_to_data_set import pdf_to_place_names_list

# 1) First, build a flat list of (pdf_filename, single_pair) for all expected pairs:
raw_tests = [
    (
        "an-tordu-logainmneacha-ceantair-ghaeltachta-2004.pdf",
        [
            ("Addergoole",   "Eadargúil"),
            ("Attyshonock",  "Áit Tí Seonac"),
            ("Carn",         "An Carn"),
            ("Glebe",        "An Seantóir"),
        ],
    ),
    (
        "an-tordu-logainmneacha-contae-an-longfoirt-2014-dreacht.pdf",
        [
            ("Abbey Land",      "Fearann na Mainistreach"),
            ("Aghamore",        "Achadh Mór"),
            ("Cleggill",        "An Chlagchoill"),
            ("Clooneen",        "An Cluainín"),
            ("Crancam",         "An Crann Cam"),
            ("Goat’s Island",   "Inse an Ghabhair"),
            ("Abbeylara",       "Mainistir Leathrátha"),
            ("Lissawly", "Lios Amhlaoibh"),
            ("Garryconnell", "Garraí Chonaill"),
            ("Garrynagh", "Garraí an Átha"),
            ("Garrycam", "An Garraí Cam")
        ],
    ),
    (
        "an-tordu-logainmneacha-contae-bhaile-atha-cliath-2011.pdf",
        [
            ("Adamstown",    "Baile Adaim"),
            ("Balgaddy",     "Baile Gadaí"),
            ("Castleknock",  "Caisleán Cnucha"),
            ("Crumlin",      "Cromghlinn"),
        ],
    ),
    (
        "an-tordu-logainmneacha-ceantair-ghaeltachta-2011.pdf",
        [
            ("Aharla",             "An Eatharla"),
            ("Annaghdown Islands", "Oileáin Eanach Dhúin"),
            ("Fiddaunacushnane",   "Feadán an Chuisneáin"),
            ("Owenwee River",      "An Abhainn Bhuí"),
        ],
    ),
]

flat_tests = []
ids = []
for pdf_filename, pair_list in raw_tests:
    for en, ga in pair_list:
        flat_tests.append((pdf_filename, en, ga))
        # Build an ID like "ghaeltachta-2004.pdf:Addergoole/Eadargúil"
        base = os.path.basename(pdf_filename)
        ids.append(f"{base}:{en}/{ga}")


@pytest.mark.parametrize(
    "pdf_filename, expected_en, expected_ga",
    flat_tests,
    ids=ids,
)
def test_each_place_name_is_extracted(pdf_filename, expected_en, expected_ga):
    """
    For each PDF in tests/fixtures/, check that (expected_en, expected_ga) appears
    in the output of pdf_to_place_names_list().
    """
    this_dir     = os.path.dirname(__file__)
    fixtures_dir = os.path.join(this_dir, "fixtures")
    pdf_path     = os.path.join(fixtures_dir, pdf_filename)

    assert os.path.isfile(pdf_path), f"Could not find {pdf_path}"

    extracted = pdf_to_place_names_list(pdf_path)

    pair = (expected_en, expected_ga)
    assert pair in extracted, (
        f"Expected to find {pair} in {pdf_filename}, but did not."
    )
