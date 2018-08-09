import pytest
from rondan.utils import *


# test cap_first_letters
@pytest.mark.parametrize(
    "test_input, expected_output",
    [
        ("mario PARTY", "Mario Party"),
        ("asada akira", "Asada Akira"),
        ("SUDA51", "Suda51")
    ]
    )
def test_cap_first_letters(test_input, expected_output):
    assert cap_first_letters(test_input) == expected_output


# test remove years
@pytest.mark.parametrize(
    "test_input, expected_output",
    [
        ("YX, 1953", "YX"),
        ("Yada Klorf", "Yada Klorf")
    ]
    )
def test_remove_years(test_input, expected_output):
    assert remove_years(test_input) == expected_output


# test kana to romaji
def test_kana_to_romaji():
    #assert kana_to_romaji(test_input) == expected_output
    assert kana_to_romaji("あさだ あきら") == "asada akira"
    assert kana_to_romaji("だいじょうぶ？") == "daijōbu?"
    assert kana_to_romaji("yada klorf") == "yada klorf"