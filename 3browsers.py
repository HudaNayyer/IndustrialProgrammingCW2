import argparse, json, re
from collections import Counter
import matplotlib.pyplot as plt

# similar libraries, but also imports re: regular expression to extract the browser names


# cli: python 3browsers.py --file data\issuu_sample.json --task 3a
# change 3a or 3b and change the data to issuu_cw2 to test out the other file


# reads the json-lines file one at a time, each line within the json file is treated as a json obj and NOT as a giant array,
# this way mem usage is low
# (open the file -> read line -> strip whitespace -> skip if empty -> parse json -> yield the json obj
def readEvents(path):
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            yield json.loads(line)


# counts all the full 'visitor_useragent' strings and iterates over each json record, gets the browser id string
# increments it's counter and returns the counter
def histogram_useragents(file_path):
    counts = Counter()
    
    for ev in readEvents(file_path):
        ua = ev.get("visitor_useragent")
        
        if ua:
            counts[ua] += 1
            
    return counts

# a reg exp pattern that helps match the main browser's name
BROWSER_PAT = re.compile(r"(Firefox|Chrome|Chromium|Safari|Edge|IE|Opera|OPR)", re.I)



# help func for 3b: looks for the browser names in the text, 
# if not, classify it as 'other' and take the matched part and capitalize the title and returns it
def simplify_browser(ua):
    """Extract just the main browser name."""
    if not ua:
        return "Unknown"
    m = BROWSER_PAT.search(ua)
    if not m:
        return "Other"
    name = m.group(1)
    # this normalizes opera's OPR token
    if name.lower() == "opr":
        name = "Opera"
    return name.title()


# 3b: counts the browser using simplified names only, iterates, if it matches increment the counter and return it.
def histogram_browsers_simple(file_path):
    counts = Counter()
    
    for ev in readEvents(file_path):
        ua = ev.get("visitor_useragent")
        
        if ua:
            counts[simplify_browser(ua)] += 1
    return counts

# plots a bar chart from the counter dict using matplotlib
def plot_hist(counter, title, max_labels=20):
    if not counter:
        print("No data for", title)
        return
    labels, values = zip(*counter.most_common(max_labels))
    plt.figure()
    plt.bar(labels, values)
    plt.title(title)
    plt.xticks(rotation=60, ha="right")
    plt.tight_layout()
    plt.show()


# CLI
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--file", "-f", required=True, help="Path to JSON-lines dataset")
    ap.add_argument("--task", "-t", choices=["3a", "3b"], default="3a")
    args = ap.parse_args()


# 3a: gives the full user-agent histo, prints the top 10 examples and truncates the long strings
    if args.task == "3a":
        hist = histogram_useragents(args.file)
        print(f"Found {len(hist)} distinct user-agent strings.")
        
        for ua, n in hist.most_common(10):
            print(f"{n:4d}  {ua[:70]}")
        
        plot_hist(hist, "Full User-Agent Strings (3a)")

# 3b: prints all the simplified browser names
    else:
        hist = histogram_browsers_simple(args.file)
        print("Simplified browser counts:")
        
        for name, n in hist.most_common():
            print(f"{name:10s} {n}")
        
        plot_hist(hist, "Main Browsers (3b)")

if __name__ == "__main__":
    main()
