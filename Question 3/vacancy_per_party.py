import csv
import sys

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

# helper func for loading csv
def load_csv(path):
    data = []

    with open(path, newline='', encoding="utf-8-sig") as file:
        reader = csv.DictReader(file)
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
    
    print(f"Province: {province}")
    print("2019 Results")
    print("-------------")
    for i in range(len(parties2019)):
        print(f"{parties2019[i]}: {shares2019[i]:.2f}%")
        
    print("2021 Results")
    print("-------------")
    for i in range(len(parties2021)):
        print(f"{parties2021[i]}: {shares2021[i]:.2f}%")
    
   

if __name__ == "__main__":
    main()