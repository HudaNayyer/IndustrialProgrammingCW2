import argparse, json
from collections import Counter, defaultdict
import matplotlib.pyplot as plt
import csv

# huda, since they ask the reason for the use of certain libraries:
# - argparse: for parsing command-line argument
# - json: for reading json-lines
# - collections.Counter and defaultdict: for counting and grouping data efficiently
# - matplotlib.pyplot: for plotting histograms


# cli: python 2views.py --file data\issuu_sample.json --doc 140228202800-6ef39a241f35301a9a42cd0ed21e5fb0
# change the id and json file as you wish



# reads the json-lines file one at a time, each line within the json file is treated as a json obj and NOT as a giant array,
# this way mem usage is low
# (open the file -> read line -> strip whitespace -> skip if empty -> parse json -> yield the json obj
def readEvents(path):
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line=line.strip()
            if not line: 
                continue
            yield json.loads(line)


# the name should be self-explanatory
# uses the dict subclass to count and iterates over each json object
# extracts the doc uuid from the record, skips the events that doesn't concern the current doc
#  then extracts the viewer's country code (check country_continent.csv)
# increments the count for that country code
# returns something like a counter {'MX':2, 'AR' :1}
def histogram_countries(file_path, doc_uuid):
    counts = Counter()
    
    for ev in readEvents(file_path):
        doc = ev.get("subject_doc_id")
        
        if doc != doc_uuid:
            continue
        country = ev.get("visitor_country")
        
        if country:
            counts[country] += 1
            
    return counts


# loads the country-continent mapping from a csv file into a dict
def load_country_continent(csv_path):
    m = {}
    with open(csv_path, newline='', encoding="utf-8") as f:
        
        for row in csv.DictReader(f):
            m[row["country"].strip()] = row["continent"].strip()
    return m


# converts the country hist -> continent hist using the mapping dict
# summs up the counts for each continent
# iterates over each country and its count, if it doesnt find it it matches it to Unknown(check the csv)
# adds the country's view count to the respective continent and converts to Counter
def histogram_continents(country_hist, ccmap):
    agg = defaultdict(int)
    
    for country, n in country_hist.items():
        agg[ccmap.get(country, "Unknown")] += n
    
    return Counter(agg)


# self explanatory, but uses matplotlib to plot, splits keys and counts and is sirted by freq
def plot_hist(counter, title):
    
    if not counter:
        print("No data for:", title)
        return
    
    labels, values = zip(*counter.most_common())
    plt.figure()
    plt.bar(labels, values)
    plt.xticks(rotation=60, ha="right")
    plt.title(title)
    plt.tight_layout()
    plt.show()


# The CLI args, if needed you can move these all later to a seperate file and name it cli for 8. Command Line Usage
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--file", "-f", required=True, help="Path to JSON-lines file")
    ap.add_argument("--doc", "-d", required=True, help="Document UUID")
    ap.add_argument("--ccmap", default="country_continent.csv", help="Country→Continent CSV")
    args = ap.parse_args()

# this is 2a: takes a string an input, uniquely specifies the doc UUID, 
# returns a histo of countries by viewers, displayed using matplotlib
    c_hist = histogram_countries(args.file, args.doc)
    print("Top countries:")
    
    for k,v in c_hist.most_common(10):
        print(f"{k:20s} {v}")
        
    plot_hist(c_hist, f"Views by Country for {args.doc}")



# this is 2b: this builds on top of the prev part and just groups counts into continents
    try:
        cc = load_country_continent(args.ccmap)
    except FileNotFoundError:
        print("WARNING: country_continent.csv not found; continents will be Unknown")
        cc = {}
    cont_hist = histogram_continents(c_hist, cc)
    print("\nContinents:")
    
    for k,v in cont_hist.most_common():
        print(f"{k:12s} {v}")
        
    plot_hist(cont_hist, f"Views by Continent for {args.doc}")

if __name__ == "__main__":
    main()
