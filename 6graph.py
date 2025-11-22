import argparse
import json
from collections import defaultdict, Counter
import subprocess


# Utility: Read JSON-lines file
def read_events(path): #Yield parsed JSON objects from a JSON-lines file.
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                yield json.loads(line)


# also likes implemention from task 5 
def build_indices(file_path):
    doc_to_readers = defaultdict(set)
    reader_to_docs = defaultdict(set)

    for ev in read_events(file_path):
        doc = ev.get("subject_doc_id")
        reader = ev.get("visitor_uuid")

        if doc and reader:
            doc_to_readers[doc].add(reader)
            reader_to_docs[reader].add(doc)

    return doc_to_readers, reader_to_docs


# DOT helper formatting
def short(u):
    return u[-4:] if len(u) > 4 else u     #Return last 4 characters of a UUID.

def dot_reader_node(uuid, highlight=False):
    color = 'fillcolor=lightgreen,style=filled' if highlight else ''
    return f'        "{short(uuid)}" [shape=box {"," + color if color else ""}];'

def dot_doc_node(uuid, highlight=False):
    color = 'fillcolor=lightgreen,style=filled' if highlight else ''
    return f'        "{short(uuid)}" [shape=circle {"," + color if color else ""}];'

# ------------------------------------------------------------
# Main graph builder
def generate_graph(doc_to_readers, reader_to_docs, doc_uuid, visitor_uuid=None):
    seed_readers = set(doc_to_readers.get(doc_uuid, set()))     # Return DOT graph (string) and list of top 10 also-like documents.

    # If visitor supplied but hasn't read doc, still include & highlight it
    if visitor_uuid:
        seed_readers.add(visitor_uuid)

    # Count also-liked documents
    counts = Counter()
    reader_connections = defaultdict(set)

    for reader in seed_readers:
        for d in reader_to_docs.get(reader, []):
            if d != doc_uuid:
                counts[d] += 1
                reader_connections[d].add(reader)

    top_docs = [doc for doc, _ in counts.most_common(10)]

    # Collect all readers involved
    all_readers = set(seed_readers)
    for d in top_docs:
        all_readers.update(reader_connections[d])

    # DOT construction
    dot = []
    dot.append('digraph AlsoLikes {')
    dot.append('    rankdir=LR;')
    dot.append('    splines=true;')
    dot.append('    nodesep=0.5;')
    dot.append('    ranksep=1;')
    dot.append('')

    # Readers cluster (left)
    dot.append('    subgraph cluster_readers {')
    dot.append('        label="Readers";')
    dot.append('        style=filled;')
    dot.append('        fillcolor=lightgray;')
    dot.append('        node [shape=box];')
    dot.append('')

    # Keep readers pretty much in consistent order
    for r in sorted(all_readers):
        dot.append(dot_reader_node(r, highlight=(r == visitor_uuid)))

    dot.append('    }')
    dot.append('')

    # Documents cluster (right)
    dot.append('    subgraph cluster_documents {')
    dot.append('        label="Documents";')
    dot.append('        style=filled;')
    dot.append('        fillcolor=lightyellow;')
    dot.append('        node [shape=circle];')
    dot.append('')

    # Highlight the input document
    dot.append(dot_doc_node(doc_uuid, highlight=True))

    # Other documents
    for d in top_docs:
        dot.append(dot_doc_node(d))

    dot.append('    }')
    dot.append('')

    # Edges: reader → input document
    for r in seed_readers:
        dot.append(f'    "{short(r)}" -> "{short(doc_uuid)}";')

    # Edges: reader → top also-liked docs
    for d in top_docs:
        for r in reader_connections[d]:
            dot.append(f'    "{short(r)}" -> "{short(d)}";')

    dot.append('}')
    return "\n".join(dot), top_docs


# Rendering (dot to ps/pdf)
def save_and_render(dot_src, name):
    dot_file = f"{name}.dot"
    with open(dot_file, "w") as f:
        f.write(dot_src)
    print(f"DOT saved → {dot_file}")

    try:
        subprocess.run(["dot", "-Tps", "-o", f"{name}.ps", dot_file], check=True)
        print(f"PS generated → {name}.ps")
        subprocess.run(["dot", "-Tpdf", "-o", f"{name}.pdf", dot_file], check=True)
        print(f"PDF generated → {name}.pdf")
    except Exception:
        print("Graphviz not found. Install it to generate PS/PDF.")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("-f", "--file", required=True)
    ap.add_argument("-d", "--doc", required=True)
    ap.add_argument("-u", "--user")
    ap.add_argument("-o", "--output", default="also_likes")
    args = ap.parse_args()

    doc_to_readers, reader_to_docs = build_indices(args.file)

    dot_src, top_docs = generate_graph(
        doc_to_readers, reader_to_docs, args.doc, args.user
    )

    save_and_render(dot_src, args.output)

    print("\nTop also-liked documents:")
    for i, d in enumerate(top_docs[:10], 1):
        print(f"{i}. {d}")

if __name__ == "__main__":
    main()
