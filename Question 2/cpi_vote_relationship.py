#!/usr/bin/env python3
'''
  Author(s): Rushi Patel 1374939

  Project: CIS2250 Term Project Milestone III 
  Question:How does the change in the Consumer Price Index (CPI) in each province between 
  2019 and 2021 relate to changes in federal election vote share for major political parties?
  
  Date of Last Update: March 23, 2026.

  Functional Summary
      Reads election CSV files for the 2019 and 2021 Canadian federal elections
      and monthly CPI CSV files for 2019 to 2021.
      Calculates vote share for each political party in each province for both elections,
      computes vote share change between 2019 and 2021, calculates average CPI for
      each province in 2019 and 2021, and computes CPI change.
      Merges the election and CPI results into one final CSV file for later analysis
      and visualization.
'''

import sys
import csv


# Prints an error message and exits the program
def fatal(msg):
    print(f"Error: {msg}", file=sys.stderr)
    sys.exit(1)


# Loads a CSV file and returns a list of dictionaries (rows)
def load_csv(path):
    data = []

    try:
        # Open file with UTF-8 encoding (handles Excel files properly)
        with open(path, newline="", encoding="utf-8-sig") as file:
            reader = csv.DictReader(file)

            # Read each row into a dictionary
            for row in reader:
                if row:
                    data.append(row)

    except OSError as err:
        fatal(f"Could not open file '{path}': {err}")

    # Ensure file is not empty
    if len(data) == 0:
        fatal(f"File '{path}' is empty")

    return data


# Extracts province names from the election dataset (column headers)
def get_provinces(election_data):
    provinces = []
    headers = list(election_data[0].keys())

    # All columns except "Political affiliation" are provinces
    for header in headers:
        if header != "Political affiliation":
            provinces.append(header)

    return provinces


# Extracts all party names from the dataset
def get_parties(election_data):
    parties = []

    for row in election_data:
        party = row["Political affiliation"].strip()

        # Ignore empty rows
        if party != "":
            parties.append(party)

    return parties


# Converts raw election CSV data into structured dictionary:
# { province: { party: votes } }
def process_election_data(data, provinces):
    result = {}

    # Initialize dictionary for each province
    for province in provinces:
        result[province] = {}

    # Loop through each row (each party)
    for row in data:
        party = row["Political affiliation"].strip()

        if party == "":
            continue

        # Extract votes for each province
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


# Calculates vote share (percentage) for each party in each province
def calculate_vote_share(data, provinces, parties):
    result = {}

    for province in provinces:
        result[province] = {}
        total_votes = 0

        # Calculate total votes in province
        for party in parties:
            if party in data[province]:
                total_votes += data[province][party]

        if total_votes == 0:
            fatal(f"Total votes for province '{province}' is 0")

        # Calculate vote share for each party
        for party in parties:
            votes = 0
            if party in data[province]:
                votes = data[province][party]

            share = votes / total_votes
            result[province][party] = share

    return result


# Loads CPI data from monthly files and groups by province
def load_cpi_files(provinces):
    cpi_data = {}

    # Initialize structure
    for province in provinces:
        cpi_data[province] = {
            "2019": [],
            "2021": []
        }

    years = ["2019", "2020", "2021"]
    months = ["01", "02", "03", "04", "05", "06",
              "07", "08", "09", "10", "11", "12"]

    # Loop through all CPI files
    for year in years:
        for month in months:
            filename = "data/CPI" + year + "-" + month + ".csv"

            try:
                file_data = load_csv(filename)
            except SystemExit:
                # Skip missing files
                continue

            for row in file_data:
                province = row["GEO"].strip()

                # Ignore non-province data
                if province not in provinces:
                    continue

                value = row["CPI"].strip()

                if value == "":
                    continue

                try:
                    cpi_value = float(value)
                except ValueError:
                    fatal(f"Invalid CPI value '{value}' in file '{filename}'")

                # Store CPI values for 2019 and 2021
                if year == "2019":
                    cpi_data[province]["2019"].append(cpi_value)

                if year == "2021":
                    cpi_data[province]["2021"].append(cpi_value)

    return cpi_data


# Calculates average CPI and CPI change for each province
def calculate_cpi_change(cpi_data, provinces):
    result = {}

    for province in provinces:
        values_2019 = cpi_data[province]["2019"]
        values_2021 = cpi_data[province]["2021"]

        if len(values_2019) == 0:
            fatal(f"No 2019 CPI data found for province '{province}'")

        if len(values_2021) == 0:
            fatal(f"No 2021 CPI data found for province '{province}'")

        # Compute averages
        avg_2019 = sum(values_2019) / len(values_2019)
        avg_2021 = sum(values_2021) / len(values_2021)

        # Compute CPI change
        change = avg_2021 - avg_2019

        result[province] = {
            "AvgCPI2019": avg_2019,
            "AvgCPI2021": avg_2021,
            "CPIChange": change
        }

    return result


# Merges vote share data and CPI data into final dataset
def merge_data(vote_2019, vote_2021, cpi_data, provinces, parties):
    final_rows = []

    for province in provinces:
        for party in parties:
            # Calculate vote share change
            share_2019 = vote_2019[province][party]
            share_2021 = vote_2021[province][party]
            vote_change = share_2021 - share_2019

            # Get CPI values
            avg_cpi_2019 = cpi_data[province]["AvgCPI2019"]
            avg_cpi_2021 = cpi_data[province]["AvgCPI2021"]
            cpi_change = cpi_data[province]["CPIChange"]

            # Create row
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


# Writes final processed data to CSV file
def write_output(filename, rows):
    try:
        with open(filename, "w", newline="", encoding="utf-8-sig") as file:
            writer = csv.writer(file)

            # Write header row
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

            # Write data rows
            for row in rows:
                writer.writerow(row)

    except OSError as err:
        fatal(f"Could not write output file '{filename}': {err}")


# Main function controlling program execution
def main(argv):
    if len(argv) != 1:
        fatal("Usage: python summarize.py")

    # Load election datasets
    election2019 = load_csv("data/43thelection.csv")
    election2021 = load_csv("data/44thelection.csv")

    # Extract provinces and parties
    provinces = get_provinces(election2019)
    parties = get_parties(election2019)

    # Process election data into structured format
    election_data_2019 = process_election_data(election2019, provinces)
    election_data_2021 = process_election_data(election2021, provinces)

    # Calculate vote shares
    vote_share_2019 = calculate_vote_share(election_data_2019, provinces, parties)
    vote_share_2021 = calculate_vote_share(election_data_2021, provinces, parties)

    # Load and process CPI data
    cpi_raw = load_cpi_files(provinces)
    cpi_summary = calculate_cpi_change(cpi_raw, provinces)

    # Merge all data
    final_rows = merge_data(vote_share_2019, vote_share_2021, cpi_summary, provinces, parties)

    # Output final dataset
    write_output("final_data.csv", final_rows)

    print("final_data.csv created successfully")


if __name__ == "__main__":
    main(sys.argv)
