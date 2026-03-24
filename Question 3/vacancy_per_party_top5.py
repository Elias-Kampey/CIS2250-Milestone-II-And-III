import csv
import sys

#import library for creating graphs
import matplotlib.pyplot as plt

#map to simplify province titles for argv use
province_map = {
    "NL": "N.L. Valid Votes/Votes valides T.-N.-L.",
    "PE": "P.E.I. Valid Votes/Votes valides Î.-P.-É.",
    "NS": "N.S. Valid Votes/Votes valides N.-É.",
    "NB": "N.B. Valid Votes/Votes valides N.-B.",
    "QC": "Que. Valid Votes/Votes valides Qc",
    "ON": "Ont. Valid Votes/Votes valides Ont.",
    "MB": "Man. Valid Votes/Votes valides Man.",
    "SK": "Sask. Valid Votes/Votes valides Sask.",
    "AB": "Alta. Valid Votes/Votes valides Alb.",
    "BC": "B.C. Valid Votes/Votes valides C.-B.",
    "YT": "Y.T. Valid Votes/Votes valides Yn",
    "NT": "N.W.T. Valid Votes/Votes valides T.N.-O.",
    "NU": "Nun. Valid Votes/Votes valides Nt"
}

# map for vacancy dataset
province_name_map = {
    "NL": "Newfoundland and Labrador",
    "PE": "Prince Edward Island",
    "NS": "Nova Scotia",
    "NB": "New Brunswick",
    "QC": "Quebec",
    "ON": "Ontario",
    "MB": "Manitoba",
    "SK": "Saskatchewan",
    "AB": "Alberta",
    "BC": "British Columbia"
}

# helper func for loading csv
def load_csv(path):
    data = []

    with open(path, newline='', encoding="utf-8-sig") as file:
        reader = csv.DictReader(file)

        # try different delimiters if needed
        if len(reader.fieldnames) == 1:
            file.seek(0)
            reader = csv.DictReader(file, delimiter='\t')

        if len(reader.fieldnames) == 1:
            file.seek(0)
            reader = csv.DictReader(file, delimiter=';')

        for row in reader:
            data.append(row)

    return data

# function to process election data given from csv file
def process_election_data(data, province):
    # province will be called as sys.argv[] in main
    # variables for parties & votes
    parties = []
    votes = []
    
    #convert column to province map used earlier
    column = province_map[province]
    
    for row in data:
        #split the row to keep only the english text
        party = row["Political affiliation/Appartenance politique"].split("/")[0]
        
        # if selected province is found in list
        
        vote_count = int(row[column])
        parties.append(party) # append party name to end
        votes.append(vote_count) # append vote count to end
    
    return parties, votes

def calculate_vote_share(votes, parties):
    shares = []
    total_votes = sum(votes)
    
    # get share percentage by dividing votes per party by total votes * 100
    for i in range(len(parties)):
        share = (votes[i] / total_votes) * 100
        shares.append(share)
        
    return shares

def process_vacancy_data(path, province):
    province_name = province_name_map[province]
    values = []

    with open(path, encoding="utf-8-sig") as f:
        reader = csv.reader(f)
        rows = list(reader)

    # find header row (the one with province names)
    for i, row in enumerate(rows):
        if "Geography" in row:
            header = row
            break

    # find Ontario column indices
    province_indices = []
    for i, col in enumerate(header):
        if province_name in col:
            province_indices.append(i)

    # find the vacancy rate row
    for row in rows:
        if len(row) > 1 and "Job vacancy rate" in row[1]:
            for idx in province_indices:
                val = row[idx]
                if val:
                    num = ''.join(c for c in val if c.isdigit() or c == '.')
                    if num:
                        values.append(float(num))

    if len(values) == 0:
        return 0
    
    print(header)
    return sum(values) / len(values)

#create graph
def plot_results(parties2019, shares2019, parties2021, shares2021, province, vac2019, vac2021):

    # match parties between years
    all_parties = list(set(parties2019) | set(parties2021))

    dict2019 = dict(zip(parties2019, shares2019))
    dict2021 = dict(zip(parties2021, shares2021))

    combined = []

    for party in all_parties:
        s2019 = dict2019.get(party, 0)
        s2021 = dict2021.get(party, 0)
        change = s2021 - s2019
        combined.append((party, change))

    # sort by biggest absolute change
    combined.sort(key=lambda x: abs(x[1]), reverse=True)

    # take top 5 parties
    top_n = 5
    combined = combined[:top_n]

    top_parties = [x[0] for x in combined]
    vote_change = [x[1] for x in combined]

    # vacancy change
    vacancy_change = vac2021 - vac2019

    x = range(len(top_parties))

    plt.figure()

    # bar chart = vote change
    plt.bar(x, vote_change, label="Vote Share Change")

    # horizontal line = vacancy change
    plt.axhline(y=vacancy_change, linestyle='--', label="Vacancy Change")

    plt.xticks(x, top_parties, rotation=45, ha="right")

    plt.title(f"{province}: Vote Change vs Vacancy Change")
    plt.ylabel("Change (%)")

    plt.legend()
    plt.tight_layout()
    plt.show()

def main():
    # gets province inputted into terminal, case insensitive (ex. ON)
    province = sys.argv[1].upper()
    
    # load election files
    election2019 = load_csv("election2019/table_tableau08.csv")
    election2021 = load_csv("election2021/table_tableau08.csv")
    
    # # load vacancy files
    # vacancy2019 = load_csv("2019/job_vacancies2019.csv")
    # vacancy2021 = load_csv("2021/job_vacancies2021.csv")
    print("files loaded successfully")
    
    #process data into two variables for parties and votes
    parties2019, votes2019 = process_election_data(election2019, province)
    parties2021, votes2021 = process_election_data(election2021, province)
    
    # calculates shares into variables
    shares2019 = calculate_vote_share(votes2019, parties2019)
    shares2021 = calculate_vote_share(votes2021, parties2021)
    # vacancy
    vacancy2019 = process_vacancy_data("election2019/job_vacancies2019.csv", province)
    vacancy2021 = process_vacancy_data("election2021/job_vacancies2021.csv", province)

    # print results
    print(f"\nProvince: {province}")

    print("\n2019 Results")
    print("-------------")
    for i in range(len(parties2019)):
        print(f"{parties2019[i]}: {shares2019[i]:.2f}%")

    print("\n2021 Results")
    print("-------------")
    for i in range(len(parties2021)):
        print(f"{parties2021[i]}: {shares2021[i]:.2f}%")

    print("\nVacancy Rates")
    print("-------------")
    print(f"2019: {vacancy2019:.2f}%")
    print(f"2021: {vacancy2021:.2f}%")
    print(f"Change: {vacancy2021 - vacancy2019:.2f}%")

    # graph
    plot_results(parties2019, shares2019, parties2021, shares2021, province, vacancy2019, vacancy2021)

if __name__ == "__main__":
    main()