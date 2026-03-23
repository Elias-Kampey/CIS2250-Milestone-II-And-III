#!/usr/bin/env python3

import sys
import csv


def fatal(msg):
    print(f"Error: {msg}", file=sys.stderr)
    sys.exit(1)


def load_csv(path):
    data = []

    try:
        with open(path, newline="", encoding="utf-8-sig") as file:
            reader = csv.DictReader(file)

            for row in reader:
                if row:
                    data.append(row)

    except OSError as err:
        fatal(f"Could not open file '{path}': {err}")

    if len(data) == 0:
        fatal(f"File '{path}' is empty")

    return data


def get_provinces(election_data):
    provinces = []
    headers = list(election_data[0].keys())

    for header in headers:
        if header != "Political affiliation":
            provinces.append(header)

    return provinces


def get_parties(election_data):
    parties = []

    for row in election_data:
        party = row["Political affiliation"].strip()
        if party != "":
            parties.append(party)

    return parties


def process_election_data(data, provinces):
    result = {}

    for province in provinces:
        result[province] = {}

    for row in data:
        party = row["Political affiliation"].strip()

        if party == "":
            continue

        for province in provinces:
            value = row[province].strip()

            if value == "":
                votes = 0
            else:
                try:
                    votes = int(value)
                except ValueError:
                    fatal(f"Invalid vote value '{value}' for party '{party}' in province '{province}'")

            result[province][party] = votes

    return result


def calculate_vote_share(data, provinces, parties):
    result = {}

    for province in provinces:
        result[province] = {}

        total_votes = 0

        for party in parties:
            if party in data[province]:
                total_votes += data[province][party]

        if total_votes == 0:
            fatal(f"Total votes for province '{province}' is 0")

        for party in parties:
            votes = 0
            if party in data[province]:
                votes = data[province][party]

            share = votes / total_votes
            result[province][party] = share

    return result


def load_cpi_files(provinces):
    cpi_data = {}

    for province in provinces:
        cpi_data[province] = {
            "2019": [],
            "2021": []
        }

    years = ["2019", "2020", "2021"]
    months = ["01", "02", "03", "04", "05", "06",
              "07", "08", "09", "10", "11", "12"]

    for year in years:
        for month in months:
            filename = "data/CPI" + year + "-" + month + ".csv"

            try:
                file_data = load_csv(filename)
            except SystemExit:
                continue

            for row in file_data:
                province = row["GEO"].strip()

                if province not in provinces:
                    continue

                value = row["CPI"].strip()

                if value == "":
                    continue

                try:
                    cpi_value = float(value)
                except ValueError:
                    fatal(f"Invalid CPI value '{value}' in file '{filename}'")

                if year == "2019":
                    cpi_data[province]["2019"].append(cpi_value)

                if year == "2021":
                    cpi_data[province]["2021"].append(cpi_value)

    return cpi_data


def calculate_cpi_change(cpi_data, provinces):
    result = {}

    for province in provinces:
        values_2019 = cpi_data[province]["2019"]
        values_2021 = cpi_data[province]["2021"]

        if len(values_2019) == 0:
            fatal(f"No 2019 CPI data found for province '{province}'")

        if len(values_2021) == 0:
            fatal(f"No 2021 CPI data found for province '{province}'")

        avg_2019 = sum(values_2019) / len(values_2019)
        avg_2021 = sum(values_2021) / len(values_2021)
        change = avg_2021 - avg_2019

        result[province] = {
            "AvgCPI2019": avg_2019,
            "AvgCPI2021": avg_2021,
            "CPIChange": change
        }

    return result


def merge_data(vote_2019, vote_2021, cpi_data, provinces, parties):
    final_rows = []

    for province in provinces:
        for party in parties:
            share_2019 = vote_2019[province][party]
            share_2021 = vote_2021[province][party]
            vote_change = share_2021 - share_2019

            avg_cpi_2019 = cpi_data[province]["AvgCPI2019"]
            avg_cpi_2021 = cpi_data[province]["AvgCPI2021"]
            cpi_change = cpi_data[province]["CPIChange"]

            row = [
                province,
                party,
                round(share_2019, 6),
                round(share_2021, 6),
                round(vote_change, 6),
                round(avg_cpi_2019, 3),
                round(avg_cpi_2021, 3),
                round(cpi_change, 3)
            ]

            final_rows.append(row)

    return final_rows


def write_output(filename, rows):
    try:
        with open(filename, "w", newline="", encoding="utf-8-sig") as file:
            writer = csv.writer(file)

            writer.writerow([
                "Province",
                "Party",
                "VoteShare2019",
                "VoteShare2021",
                "VoteShareChange",
                "AvgCPI2019",
                "AvgCPI2021",
                "CPIChange"
            ])

            for row in rows:
                writer.writerow(row)

    except OSError as err:
        fatal(f"Could not write output file '{filename}': {err}")


def main(argv):
    if len(argv) != 1:
        fatal("Usage: python summarize.py")

    election2019 = load_csv("data/43thelection.csv")
    election2021 = load_csv("data/44thelection.csv")

    provinces = get_provinces(election2019)
    parties = get_parties(election2019)

    election_data_2019 = process_election_data(election2019, provinces)
    election_data_2021 = process_election_data(election2021, provinces)

    vote_share_2019 = calculate_vote_share(election_data_2019, provinces, parties)
    vote_share_2021 = calculate_vote_share(election_data_2021, provinces, parties)

    cpi_raw = load_cpi_files(provinces)
    cpi_summary = calculate_cpi_change(cpi_raw, provinces)

    final_rows = merge_data(vote_share_2019, vote_share_2021, cpi_summary, provinces, parties)

    write_output("final_data.csv", final_rows)

    print("final_data.csv created successfully")


if __name__ == "__main__":
    main(sys.argv)
