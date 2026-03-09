import csv
import sys


def load_election_results(filename, province):

    party_wins = {}

    with open(filename, newline='', encoding="utf-8-sig") as file:
        reader = csv.DictReader(file)

        for row in reader:

            if row["Province"] == province:

                party = row["Elected Candidate/Candidat élu"]

                if party not in party_wins:
                    party_wins[party] = 0

                party_wins[party] += 1

    return party_wins


def find_winner(party_wins):

    winner = max(party_wins, key=party_wins.get)
    return winner


def main():

    if len(sys.argv) != 2:
        print("Usage: python election_winner.py <Province>")
        sys.exit(1)

    province = sys.argv[1]

    # Note: Using "Quebec" as a parameter doesn't work due the accent
    wins_2019 = load_election_results("data/election43_table11.csv", province)
    wins_2021 = load_election_results("data/election44_table11.csv", province)

    winner_2019 = find_winner(wins_2019)
    winner_2021 = find_winner(wins_2021)

    print(f"\nProvince: {province}\n")

    print(f"2019 Winner: {winner_2019}")
    print(f"2021 Winner: {winner_2021}")

    if winner_2019 == winner_2021:
        print("\nResult: The winning party did NOT change.")
    else:
        print("\nResult: The winning party changed.")


if __name__ == "__main__":
    main()