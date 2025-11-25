import argparse, json
from collections import defaultdict

# same function
def readEvents(path):
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            yield json.loads(line)

def top_readers(file_path, top_k=10): # returns the top -k readers who are ranked by total time in sec
    reader_time = defaultdict(float) # dictionary mapping visitor (uuid) to their total reading time 
    
    for ev in readEvents(file_path):
        reader = ev.get("visitor_uuid") # store each user id as reader 
        t = ev.get("event_readtime") # extracts the unique events reading time

        if reader and isinstance(t, (int, float)): # process events that have valid reader id and a valid numeric read time 
            reader_time[reader] += t # total reading time for this reader
            
    # convert dictionary into a list of (reader_uuid, total_time) pairs
    sorted_readers = sorted(reader_time.items(), key=lambda kv: kv[1], reverse=True) # sort in descending order by total reading time.
    return sorted_readers[:top_k] # return readers with the highest total reading time 

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--file", "-f", required=True, help="Path to JSON-lines dataset")
    ap.add_argument("--top", "-k", type=int, default=10, help="Number of top readers to display")
    args = ap.parse_args()

    readers = top_readers(args.file, args.top)
    if not readers:
        print("No read-time data found.")
        return

    print(f"Top {len(readers)} readers by total read time:")
    print("UUID".ljust(20), "Seconds")
    print("-" * 32)
    
# prints each reader's uuid and their respective total reading time (rounded off)
    for uuid, secs in readers:
        print(f"{uuid:20s} {secs:8.0f}")

if __name__ == "__main__":
    main()
