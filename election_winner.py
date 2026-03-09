import csv
import sys


def load_election_results(filename, province):
    party_votes = {}

    with open(filename, newline='', encoding="utf-8-sig") as file:
        reader = csv.DictReader(file)

        for row in reader:

            if row["Province"] == province:

                party = row["Political affiliation"]
                votes = int(row["Valid votes"])

                if party not in party_votes:
                    party_votes[party] = 0

                party_votes[party] += votes

    return party_votes


def find_winner(party_votes):
    winner = max(party_votes, key=party_votes.get)
    return winner


def main():

    if len(sys.argv) != 2:
        print("Usage: python election_winner.py <Province>")
        sys.exit(1)

    province = sys.argv[1]

    votes_2019 = load_election_results("election43_table11.csv", province)
    votes_2021 = load_election_results("election44_table11.csv", province)

    winner_2019 = find_winner(votes_2019)
    winner_2021 = find_winner(votes_2021)

    print(f"\nProvince: {province}\n")

    print(f"2019 Winner: {winner_2019}")
    print(f"2021 Winner: {winner_2021}")

    if winner_2019 == winner_2021:
        print("\nResult: The winning party did NOT change.")
    else:
        print("\nResult: The winning party changed.")


if __name__ == "__main__":
    main()