#!/usr/bin/env python3

import sys
import csv
import matplotlib.pyplot as plt


def fatal(msg: str) -> None:
    print(f"Error: {msg}", file=sys.stderr)
    sys.exit(1)


def load_data(filename: str) -> list[dict]:
    data = []

    try:
        with open(filename, encoding="utf-8-sig", newline="") as fh:
            reader = csv.DictReader(fh)

            file_has_data = False

            for row in reader:
                file_has_data = True
                data.append(row)

            if not file_has_data:
                fatal(f"Data file '{filename}' is empty")

    except OSError as err:
        fatal(f"Unable to open data file '{filename}': {err}")

    return data


def filter_by_party(data: list[dict], party: str) -> list[dict]:
    filtered = []

    for row in data:
        if row["Party"] == party:
            share_2019 = float(row["VoteShare2019"])
            share_2021 = float(row["VoteShare2021"])

            if share_2019 != 0 or share_2021 != 0:
                filtered.append(row)

    if len(filtered) == 0:
        fatal(f"No data found for party '{party}'")

    return filtered


def extract_plot_data(data: list[dict]) -> tuple[list[float], list[float], list[str]]:
    x_vals = []
    y_vals = []
    labels = []

    for row in data:
        try:
            cpi = float(row["CPIChange"])
            vote = float(row["VoteShareChange"]) * 100
        except ValueError:
            continue

        x_vals.append(cpi)
        y_vals.append(round(vote,2))
        labels.append(row["Province"])

    if len(x_vals) == 0:
        fatal("No valid numeric data found for plotting")

    return x_vals, y_vals, labels


def create_plot(x_vals, y_vals, labels, party):
    plt.figure(figsize=(12, 6))

    colors = []

    for val in y_vals:
        if val >= 0:
            colors.append("green")
        else:
            colors.append("red")

    plt.scatter(x_vals, y_vals, c=colors, s=80)

    plt.scatter(x_vals, y_vals)
    plt.axhline(0)
    plt.axvline(0)


    for i in range(len(labels)):
        plt.text(x_vals[i] + 0.05, y_vals[i] + 0.3, labels[i], fontsize=9)

    

    plt.xlabel("CPI Change (2019–2021)")
    plt.ylabel("Vote Share Change (%)")
    plt.title(f"{party} Vote Share Change vs Inflation (CPI) by Province")

    plt.grid()
    plt.savefig(f"{party}_scatter.png", dpi=300)
    plt.show()


def main(argv: list[str]) -> None:
    if len(argv) != 2:
        fatal("Usage: python visualize.py <PartyName>")

    party = argv[1]

    data = load_data("final_data.csv")

    filtered_data = filter_by_party(data, party)

    x_vals, y_vals, labels = extract_plot_data(filtered_data)

    create_plot(x_vals, y_vals, labels, party)


if __name__ == "__main__":
    main(sys.argv)