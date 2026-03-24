#!/usr/bin/env python3
'''
  Author(s): Rushi Patel 1374939

  Project: CIS2250 Term Project Milestone III 
  Question:How does the change in the Consumer Price Index (CPI) in each province between 
  2019 and 2021 relate to changes in federal election vote share for major political parties?
  
  Date of Last Update: March 23, 2026.
  
  Functional Summary
      Reads the processed CSV file created by summarize.py.
      Filters the data by a selected political party passed in as a command-line
      argument.
      Creates a scatter plot showing CPI change from 2019 to 2021 on the x-axis
      and vote share change on the y-axis for each province.
      Labels each point with the province name to help visualize the relationship
      between inflation and election vote share change.
'''

import sys
import csv
import matplotlib.pyplot as plt


# Prints an error message and exits the program
def fatal(msg: str) -> None:
    print(f"Error: {msg}", file=sys.stderr)
    sys.exit(1)


# Loads processed data (final_data.csv)
def load_data(filename: str) -> list[dict]:
    data = []

    try:
        # Open CSV file
        with open(filename, encoding="utf-8-sig", newline="") as fh:
            reader = csv.DictReader(fh)

            file_has_data = False

            # Read each row
            for row in reader:
                file_has_data = True
                data.append(row)

            # Ensure file is not empty
            if not file_has_data:
                fatal(f"Data file '{filename}' is empty")

    except OSError as err:
        fatal(f"Unable to open data file '{filename}': {err}")

    return data


# Filters dataset to only include rows for the selected party
def filter_by_party(data: list[dict], party: str) -> list[dict]:
    filtered = []

    for row in data:
        if row["Party"] == party:
            # Convert vote shares to float
            share_2019 = float(row["VoteShare2019"])
            share_2021 = float(row["VoteShare2021"])

            # Ignore rows where both values are zero
            if share_2019 != 0 or share_2021 != 0:
                filtered.append(row)

    # Ensure party exists in dataset
    if len(filtered) == 0:
        fatal(f"No data found for party '{party}'")

    return filtered


# Extracts X (CPI), Y (vote change), and labels (province names)
def extract_plot_data(data: list[dict]) -> tuple[list[float], list[float], list[str]]:
    x_vals = []
    y_vals = []
    labels = []

    for row in data:
        try:
            # X-axis: CPI change
            cpi = float(row["CPIChange"])

            # Y-axis: Vote share change converted to percentage
            vote = float(row["VoteShareChange"]) * 100
        except ValueError:
            # Skip invalid data
            continue

        x_vals.append(cpi)
        y_vals.append(round(vote, 2))
        labels.append(row["Province"])

    # Ensure valid data exists
    if len(x_vals) == 0:
        fatal("No valid numeric data found for plotting")

    return x_vals, y_vals, labels


# Creates scatter plot of CPI vs Vote Share Change
def create_plot(x_vals, y_vals, labels, party):
    # Create figure
    plt.figure(figsize=(12, 6))

    colors = []

    # Assign colours: green = gain, red = loss
    for val in y_vals:
        if val >= 0:
            colors.append("green")
        else:
            colors.append("red")

    # Plot points
    plt.scatter(x_vals, y_vals, c=colors, s=80)

    # Add reference lines at 0
    plt.axhline(0)
    plt.axvline(0)

    # Label each point with province name
    for i in range(len(labels)):
        plt.text(x_vals[i] + 0.05, y_vals[i] + 0.3, labels[i], fontsize=9)

    # Axis labels and title
    plt.xlabel("CPI Change (2019–2021)")
    plt.ylabel("Vote Share Change (%)")
    plt.title(f"{party} Vote Share Change vs Inflation (CPI) by Province")

    # Grid for readability
    plt.grid()

    plt.savefig(f"{party}_scatter.png", dpi=300)

    # Display plot
    plt.show()


# Main function controlling program execution
def main(argv: list[str]) -> None:
    # Ensure correct number of arguments
    if len(argv) != 2:
        fatal("Usage: python3 cpi_vote_visualization.py <PartyName>")

    party = argv[1]

    # Load processed dataset
    data = load_data("final_data.csv")

    # Filter for selected party
    filtered_data = filter_by_party(data, party)

    # Extract plotting values
    x_vals, y_vals, labels = extract_plot_data(filtered_data)

    # Create visualization
    create_plot(x_vals, y_vals, labels, party)


if __name__ == "__main__":
    main(sys.argv)
