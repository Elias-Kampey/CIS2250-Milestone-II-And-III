#!/usr/bin/env python3
"""
Date: March 23rd, 2026

Author: Elias Mahdi (1373400)

Question 1 - CIS*2250 Milestone III
How did the winning political party change between the 43rd and 44th federal
elections in a selected province?

this script extracts the winning party from each riding's elected
candidate field, counts how many ridings each party won in the selected province,
and then identifies the province-level winner as the party with the most riding
wins in that province.
"""

import csv
import re
import sys
import unicodedata

FILE_2019 = "data/election43_table11.csv"
FILE_2021 = "data/election44_table11.csv"


def normalize_text(text):
    """Normalize text so province matching works with accents and punctuation."""
    if text is None:
        return ""

    text = text.strip()
    text = unicodedata.normalize("NFKD", text)
    text = text.encode("ascii", "ignore").decode("ascii")
    text = text.lower()

    text = text.replace("&", "and")
    text = text.replace("-", " ")
    text = text.replace("/", " ")
    text = re.sub(r"[^a-z0-9 ]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()

    return text


def province_aliases():
    """Common aliases and abbreviations for Canadian provinces/territories."""
    return {
        "ab": "Alberta",
        "bc": "British Columbia",
        "mb": "Manitoba",
        "nb": "New Brunswick",
        "nl": "Newfoundland and Labrador",
        "newfoundland": "Newfoundland and Labrador",
        "newfoundland labrador": "Newfoundland and Labrador",
        "nfld": "Newfoundland and Labrador",
        "nt": "Northwest Territories",
        "ns": "Nova Scotia",
        "nu": "Nunavut",
        "on": "Ontario",
        "ont": "Ontario",
        "pe": "Prince Edward Island",
        "pei": "Prince Edward Island",
        "qc": "Quebec",
        "pq": "Quebec",
        "quebec": "Quebec",
        "sk": "Saskatchewan",
        "yt": "Yukon",
    }


def extract_english_province(raw_province):
    """Table 11 stores province names as English/French. Use the English part."""
    return raw_province.split("/")[0].strip()


def extract_party(candidate_field):
    """Extract the winning party from the elected candidate field."""
    if "Bloc Québécois" in candidate_field:
        return "Bloc Quebecois"
    if "NDP-New Democratic Party" in candidate_field or "New Democratic Party" in candidate_field:
        return "New Democratic Party"
    if "Green Party" in candidate_field:
        return "Green Party"
    if "Liberal/" in candidate_field:
        return "Liberal Party"
    if "Conservative/" in candidate_field:
        return "Conservative Party"
    if "Independent/" in candidate_field:
        return "Independent"

    return "Unknown"


def build_province_lookup(filename):
    """Create a lookup so user input can match valid province names."""
    lookup = {}
    with open(filename, newline="", encoding="utf-8-sig") as file:
        reader = csv.DictReader(file)
        for row in reader:
            province = extract_english_province(row["Province"])
            lookup[normalize_text(province)] = province

    for alias, province in province_aliases().items():
        lookup[normalize_text(alias)] = province

    return lookup


def resolve_province(user_input, lookup):
    """Resolve user input to a canonical province name."""
    key = normalize_text(user_input)
    return lookup.get(key)


def load_party_wins_by_province(filename, selected_province):
    """
    Count how many ridings each party won in the selected province.
    Returns a dictionary like:
    {
        "Liberal Party": 35,
        "Bloc Quebecois": 32,
        ...
    }
    """
    party_wins = {}

    with open(filename, newline="", encoding="utf-8-sig") as file:
        reader = csv.DictReader(file)

        for row in reader:
            province = extract_english_province(row["Province"])
            if province != selected_province:
                continue

            party = extract_party(row["Elected Candidate/Candidat élu"])
            party_wins[party] = party_wins.get(party, 0) + 1

    return party_wins


def find_winner(party_wins):
    """Return the party with the most riding wins."""
    if not party_wins:
        return None

    max_wins = max(party_wins.values())
    winners = [party for party, wins in party_wins.items() if wins == max_wins]

    if len(winners) == 1:
        return winners[0]

    return "Tie: " + ", ".join(sorted(winners))


def print_party_table(party_wins_2019, party_wins_2021):
    """Print a clean comparison table."""
    all_parties = sorted(set(party_wins_2019) | set(party_wins_2021))

    header_party = "Party"
    header_2019 = "2019 Seats"
    header_2021 = "2021 Seats"

    party_width = max(len(header_party), max(len(p) for p in all_parties))
    width_2019 = len(header_2019)
    width_2021 = len(header_2021)

    line = (
        f"+-{'-' * party_width}-+-{'-' * width_2019}-+-{'-' * width_2021}-+"
    )

    print(line)
    print(
        f"| {header_party:<{party_width}} | {header_2019:>{width_2019}} | {header_2021:>{width_2021}} |"
    )
    print(line)

    for party in all_parties:
        seats_2019 = party_wins_2019.get(party, 0)
        seats_2021 = party_wins_2021.get(party, 0)
        print(
            f"| {party:<{party_width}} | {seats_2019:>{width_2019}} | {seats_2021:>{width_2021}} |"
        )

    print(line)


def main():
    if len(sys.argv) != 2:
        print("Usage: python election_winner_final.py <province>")
        print("Example: python election_winner_final.py Quebec")
        sys.exit(1)

    province_input = sys.argv[1]
    lookup = build_province_lookup(FILE_2019)
    province = resolve_province(province_input, lookup)

    if province is None:
        valid = sorted({v for v in lookup.values()})
        print(f'Error: "{province_input}" is not a recognized province or territory.')
        print("Valid options are:")
        for name in valid:
            print(f" - {name}")
        sys.exit(1)

    wins_2019 = load_party_wins_by_province(FILE_2019, province)
    wins_2021 = load_party_wins_by_province(FILE_2021, province)

    winner_2019 = find_winner(wins_2019)
    winner_2021 = find_winner(wins_2021)

    print(f"\nProvince: {province}\n")
    print_party_table(wins_2019, wins_2021)

    print(f"\n2019 Winner: {winner_2019}")
    print(f"2021 Winner: {winner_2021}")

    if winner_2019 == winner_2021:
        print("\nResult: The winning party did NOT change.")
    else:
        print("\nResult: The winning party changed.")


if __name__ == "__main__":
    main()
