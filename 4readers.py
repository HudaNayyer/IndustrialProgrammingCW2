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

# returns the top -k readers who are ranked by total time in sec
# maps the reader uuid -> total seconds read
# accumulate the total time per reader
# Sorts (reader, total_time) pairs descending by total_time and returns only the top k

def top_readers(file_path, top_k=10):
    reader_time = defaultdict(float)
    
    for ev in readEvents(file_path):
        reader = ev.get("visitor_uuid")
        t = ev.get("event_readtime")

        if reader and isinstance(t, (int, float)):
            reader_time[reader] += t
            

    sorted_readers = sorted(reader_time.items(), key=lambda kv: kv[1], reverse=True)
    return sorted_readers[:top_k]



# CLI
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
    print("-"*32)
    
    
# this prints each reader's uuid and their respective total reading time (rounded off)
    for uuid, secs in readers:
        print(f"{uuid:20s} {secs:8.0f}")

if __name__ == "__main__":
    main()
