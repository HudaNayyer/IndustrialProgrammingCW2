# Import required libraries
import json  
import argparse  
from graphviz import Digraph  
from collections import defaultdict  
import os  


class DocumentGraphVisualizer:
    def __init__(self, file_path): # Initializing the graph visualizer.
        
        self.file_path = file_path  # Store file path
        
        self.reader_to_docs = defaultdict(set) # maps readers to documents that theyve read
        
       
        self.doc_to_readers = defaultdict(set)  # maps documents to readers who read them
        
        # Build the data structures
        self._load_data()
    
    def _load_data(self): # Load data from JSON file and build relationships
        
        print("Loading data for graph visualization...")
        
        # Statistics counters
        events_processed = 0
        valid_relationships = 0
        
        try:
        
            with open(self.file_path, 'r') as file: # Open the data file
        
                for line_number, line in enumerate(file, 1): # Process each line
                    
                    line = line.strip() # clean the line
                    
                    
                    if not line: # skip empty lines
                        continue
                    
                    events_processed += 1
                    
                    try:
                        # Parse JSON
                        event = json.loads(line)
                        
                        # Extract reader and document IDs
                        reader_uuid = event.get('visitor_uuid')
                        doc_uuid = event.get('subject_doc_id')
                        
                        # Build relationships if both IDs exist
                        if reader_uuid and doc_uuid:
                            valid_relationships += 1
                            
                            # Add to mappings
                            self.reader_to_docs[reader_uuid].add(doc_uuid)
                            self.doc_to_readers[doc_uuid].add(reader_uuid)
                            
                    except json.JSONDecodeError:
                        print(f"  Warning: invalid JSON on line {line_number}")
                        continue
                        
        except FileNotFoundError:
            raise FileNotFoundError(f"Data file not found: {self.file_path}")
        
        # Print loading statistics
        print(f"  Events processed: {events_processed}")
        print(f"  Valid relationships: {valid_relationships}")
        print(f"  Unique readers: {len(self.reader_to_docs)}")
        print(f"  Unique documents: {len(self.doc_to_readers)}")
    
    def shorten_uuid(self, uuid): # shorten the id's as per task 6 specification
        
        # Return last 4 characters if UUID is long enough
        if len(uuid) > 4:
            return uuid[-4:]
        return uuid
    
    def create_graph(self, doc_uuid, user_uuid=None, output_name='also_likes'):
        
        print(f"\nCreating graph visualization...")
        
        # Check if document exists in data
        if doc_uuid not in self.doc_to_readers:
            print(f"Warning: Document {doc_uuid} not found in data")
            print("Creating graph with available data...")
        
        dot = Digraph(comment='Document-Reader Relationships') # Create Digraph object 
        
        # Set graph attributes 
        dot.attr(rankdir='LR', size='12,8')  # Left to right layout
        dot.attr('graph', bgcolor='white')
        dot.attr('node', fontname='Helvetica')
        dot.attr('edge', fontname='Helvetica')
        
        # Find readers of the target document
        target_readers = self.doc_to_readers.get(doc_uuid, set())
        
        # If user specified, check if they read the document
        if user_uuid and user_uuid not in target_readers:
            print(f"Warning: User {user_uuid} has not read document {doc_uuid}")
        
        # Find all documents read by these readers (also-likes)
        related_docs = set()
        for reader in target_readers:
            related_docs.update(self.reader_to_docs[reader])
        
        # Create subgraph for readers (left side)
        with dot.subgraph(name='cluster_readers') as readers_graph:
            readers_graph.attr(label='Readers', style='filled', 
                              color='lightgray', fillcolor='lightgray')
            
            # Add reader nodes
            for reader in target_readers:
                short_id = self.shorten_uuid(reader)
                
                # Highlight specified user
                if user_uuid and reader == user_uuid:
                    readers_graph.node(
                        reader,  # Full ID as node name
                        short_id,  # Short ID as label
                        shape='ellipse',
                        style='filled',
                        fillcolor='lightgreen',
                        color='darkgreen',
                        penwidth='2'
                    )
                else:
                    readers_graph.node(
                        reader,
                        short_id,
                        shape='ellipse',
                        style='filled',
                        fillcolor='lightblue',
                        color='darkblue'
                    )
        
        # Create subgraph for documents (right side)
        with dot.subgraph(name='cluster_documents') as docs_graph:
            docs_graph.attr(label='Documents', style='filled',
                           color='lightyellow', fillcolor='lightyellow')
            
            # Add document nodes
            for doc in related_docs:
                short_id = self.shorten_uuid(doc)
                
                # Highlight the target document
                if doc == doc_uuid:
                    docs_graph.node(
                        doc,  # Full ID as node name
                        short_id,  # Short ID as label
                        shape='box',
                        style='filled',
                        fillcolor='lightgreen',
                        color='darkgreen',
                        penwidth='3'
                    )
                else:
                    docs_graph.node(
                        doc,
                        short_id,
                        shape='box',
                        style='filled',
                        fillcolor='lightyellow',
                        color='orange'
                    )
        
        # Add edges (reader to document relationships)
        edge_count = 0
        for reader in target_readers:
            for doc in self.reader_to_docs[reader]:
                if doc in related_docs:  # Only show relevant documents
                    # Different edge style for main document
                    if doc == doc_uuid:
                        dot.edge(
                            reader,
                            doc,
                            color='darkgreen',
                            penwidth='2',
                            arrowsize='1.2'
                        )
                    else:
                        dot.edge(
                            reader,
                            doc,
                            color='gray',
                            style='dashed',
                            arrowsize='0.8'
                        )
                    edge_count += 1
        
        # Add title and legend
        dot.attr(label=f'\\nDocument Recommendation Graph\\n' +
                      f'Target Document: {self.shorten_uuid(doc_uuid)}\\n' +
                      f'Readers: {len(target_readers)}, Documents: {len(related_docs)}\\n',
                labelLoc='t',
                fontsize='16',
                fontweight='bold')
        
        # Save the graph (multiple formats as done in the lab session)
        try:
            # Save .dot file (source)
            dot_filename = f'{output_name}.dot'
            dot.save(dot_filename)
            print(f"  Created DOT file: {dot_filename}")
            
            # Render to PDF (primary output)
            pdf_filename = dot.render(output_name, format='pdf', cleanup=False)
            print(f"  Created PDF file: {pdf_filename}")
            
            # Also create PNG for easy viewing
            png_filename = dot.render(output_name, format='png', cleanup=False)
            print(f"  Created PNG file: {png_filename}")
            
            # Create PostScript if needed
            ps_filename = dot.render(output_name, format='ps', cleanup=False)
            print(f"  Created PS file: {ps_filename}")
            
            # Print summary
            print(f"\nGraph Statistics:")
            print(f"  Readers shown: {len(target_readers)}")
            print(f"  Documents shown: {len(related_docs)}")
            print(f"  Edges (relationships): {edge_count}")
            
            # Print viewing instructions
            print(f"\nTo view the graph:")
            print(f"  Open PDF: {pdf_filename}")
            print(f"  Open PNG: {png_filename}")
            print(f"  DOT source: {dot_filename}")
            
        except Exception as e:
            print(f"Error rendering graph: {e}")
    
    def create_simple_graph(self, output_name='simple_graph'): # simple overview graph of the entire dataset
        
        print("\nCreating simple overview graph...")
        
        # Create new Digraph
        dot = Digraph(comment='Dataset Overview')
        dot.attr(rankdir='TB', size='8,6')
        
        # Add summary node
        dot.node('summary', 
                f'Dataset Overview\\n' +
                f'Readers: {len(self.reader_to_docs)}\\n' +
                f'Documents: {len(self.doc_to_readers)}',
                shape='box',
                style='filled',
                fillcolor='lightgray')
        
        # Add sample readers and documents (top 5 of each)
        top_readers = list(self.reader_to_docs.keys())[:5]
        top_docs = list(self.doc_to_readers.keys())[:5]
        
        # Add reader nodes
        for reader in top_readers:
            short_id = self.shorten_uuid(reader)
            dot.node(f'r_{reader}', f'R: {short_id}',
                    shape='ellipse', color='blue')
            dot.edge('summary', f'r_{reader}')
        
        # Add document nodes
        for doc in top_docs:
            short_id = self.shorten_uuid(doc)
            dot.node(f'd_{doc}', f'D: {short_id}',
                    shape='box', color='orange')
            dot.edge('summary', f'd_{doc}')
        
        # Save the graph
        dot.render(output_name, format='png', cleanup=True)
        print(f"  Created overview graph: {output_name}.png")


def main():

    # Set up argument parser
    parser = argparse.ArgumentParser(
        description='Create graph visualization of document-reader relationships',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 6graph.py -f data.json -d doc123
  python3 6graph.py -f data.json -d doc123 -u user456
        """
    )
    
    # Add arguments
    parser.add_argument('-f', '--file',
                       required=True,
                       help='Path to JSON data file')
    
    parser.add_argument('-d', '--doc',
                       help='Document UUID to highlight')
    
    parser.add_argument('-u', '--user',
                       help='User UUID to highlight (optional)')
    
    parser.add_argument('-o', '--output',
                      default='also_likes',
                       help='Output filename (without extension)')

    
    # Parse arguments
    args = parser.parse_args()
    
    
    
    try:
        # Create visualizer instance
        print(f"Loading data from: {args.file}")
        visualizer = DocumentGraphVisualizer(args.file)
        
        
            # Create document-focused graph
        visualizer.create_graph(
                doc_uuid=args.doc,
                user_uuid=args.user,
                output_name=args.output
            )
        
    except FileNotFoundError as e:
        # Handle missing file
        print(f"Error: {e}")

        
    except Exception as e:
        # Handle other errors
        print(f"Error: {e}")
        print("\nTroubleshooting:")
        print("make sure graphviz is installed:")
        print("   pip install graphviz")
        print("   apt-get install graphviz (or brew install graphviz)")
        print("Check that the file path is correct")
        print("Verify document UUID exists in the data")


# Run main if executed directly
if __name__ == '__main__':
    main()