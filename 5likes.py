import argparse, json
from collections import defaultdict, Counter

# cli:  python 5likes.py --file data\issuu_cw2.json --doc 140228202800-6ef39a241f35301a9a42cd0ed21e5fb0 --user 745409913574d4c6
# user is optional so try w/o and try using another doc and also try w issuu_sample.json

def readEvents(path):
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            yield json.loads(line)


# build the indices for also likes by mapping:
# - doc_to_readers[doc] -> set of visitor_uuids/ readers who read the doc
# - reader_to_docs[user] -> set of doc_uuids read by the user
# and returns both mappings
def build_indices(file_path):
    """Build mappings: doc_to_readers and reader_to_docs."""
    doc_to_readers = defaultdict(set)
    reader_to_docs = defaultdict(set)


    for ev in readEvents(file_path):
        doc = ev.get("subject_doc_id")
        reader = ev.get("visitor_uuid")
        
        if doc and reader:
            doc_to_readers[doc].add(reader)
            reader_to_docs[reader].add(doc)

    return doc_to_readers, reader_to_docs

# 5a: when given a doc, returns all its readers
def readers_of(doc_to_readers, doc_uuid):
    return set(doc_to_readers.get(doc_uuid, set()))


# 5b: when given a user, returns all docs they read
def docs_of(reader_to_docs, visitor_uuid):
    return set(reader_to_docs.get(visitor_uuid, set()))


# 5c: starts from the set of readers who read the input doc
# optionally can add the visitor_uuid if inputed 
# and for each reader, it looks at all other docs they read
# then it counts how many times each other doc appears(shared readers)
# then it sorts using a sort_key (default is by count descending)
# finally it returns a LIST of (doc_uuid, score/count)
def also_like(doc_to_readers, reader_to_docs, doc_uuid, visitor_uuid=None, sort_key=None):
    seed_readers = readers_of(doc_to_readers, doc_uuid)
    
    if visitor_uuid and visitor_uuid not in seed_readers:
        seed_readers.add(visitor_uuid)

    counts = Counter()
    for reader in seed_readers:
        for doc in docs_of(reader_to_docs, reader):
            if doc != doc_uuid:
                counts[doc] += 1

    items = list(counts.items())
    
    if sort_key is None:
        sort_key = lambda item: item[1]  
        
    items.sort(key=sort_key, reverse=True)
    return items


# CLI
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--file", "-f", required=True, help="Path to JSON-lines dataset")
    ap.add_argument("--doc", "-d", required=True, help="Document UUID")
    ap.add_argument("--user", "-u", help="Optional Visitor UUID")
    args = ap.parse_args()

    doc_to_readers, reader_to_docs = build_indices(args.file)
    liked = also_like(doc_to_readers, reader_to_docs, args.doc, args.user)
    if not liked:
        print("No related documents found.")
        return

#  uses the default sort(using shared-reader count) to satisfy 5d
#  and prints the top 10 'also liked' documents.

    print("Top 10 'Also Liked' Documents for:", args.doc)
    print("-------------------------------------")
    for doc, count in liked[:10]:
        print(f"{doc:40s}  {count}")

if __name__ == "__main__":
    main()
