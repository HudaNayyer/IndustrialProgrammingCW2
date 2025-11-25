# Import required libraries
import json  
import argparse  
import pandas as pd  
import matplotlib.pyplot as plt  
from collections import Counter  

class InvalidDocumentException(Exception): # Custom exception for invalid document IDs 
    pass

class DocumentViewAnalyzer: # Main class for analyzing document views by location.
    
    def __init__(self, file_path, doc_uuid): # Initialize the analyzer with file path and document ID.
        
        self.file_path = file_path  # Store the path to data file
        self.doc_uuid = doc_uuid    # Store the document ID to analyze
        self.country_to_continent = {}  # mapping dictionary for country to continent
        self._load_country_continent_mapping()  # Load the mapping data
    
    def _load_country_continent_mapping(self): # private methid to load the country to continent mapping from CSV file
        
        try:
            df = pd.read_csv('country_continent.csv') # Read the CSV file using pandas     
            df.columns = [col.strip() for col in df.columns] # create clean column names 
            
            self.country_to_continent = dict(zip(df['country'], df['continent']))  # Create a dictionary mapping (country to continent)
            
        # catch errors    
        except FileNotFoundError:
            print("Warning: country_continent.csv not found.")
        except Exception as e:
            print(f"Error loading country mapping: {e}")
    
    def read_events(self): # Generator function to read events line by line, it is memory efficient for large files (streaming approach).
        
        try: 
            with open(self.file_path, 'r') as file: # Open the file for reading    
                # Process each line one by one and remove whitespace from beginning and end

                for line_number, line in enumerate(file, 1): 
                    line = line.strip() 
                    
                    if not line: # Skip empty lines
                        continue
                    try:
                        event = json.loads(line) # Parse the JSON line into a Python dictionary
                        
                        # Check if this event is for our document
                        if event.get('subject_doc_id') == self.doc_uuid:
                            yield event # Yield returns the value and pauses until next call

                    # Handle invalid and malformed JSON  
                    except json.JSONDecodeError:
                        print(f"Warning: Invalid JSON on line {line_number}")
                        continue
                        
        except FileNotFoundError:
            raise FileNotFoundError(f"Data file not found: {self.file_path}") # Handle missing data file
    
    def analyze_by_country(self): #Task 2a: Analyze views by country.
       
        country_counter = Counter()  # empty Counter to track country views
    
        found_any_data = False # Track if we found any data
        
        
        for event in self.read_events(): # Process each event for this document
            found_any_data = True  # if we found at least one event
            
            # Getting the visitors country 
            country = event.get('visitor_country', 'Unknown')
            
            # Skip if country is missing or None
            if country and country != 'Unknown':
                country_counter[country] += 1 # increase the count for this country
        
        if not found_any_data: # Check if document exists in the data
            raise InvalidDocumentException(f"No data found for document: {self.doc_uuid}")
        
        return country_counter
    
    def analyze_by_continent(self): #  Task 2b: Analyze views by continent.
        
        country_counter = self.analyze_by_country() # getting country data
        
        continent_counter = Counter() # counter for continents
        
        # Group countries by continent
        for country, count in country_counter.items():
            continent = self.country_to_continent.get(country, 'Unknown') # Look up the continent for this country
            
            continent_counter[continent] += count # Adding the countrys count to its continent
        
        return continent_counter
    
    def create_histogram(self, data_counter, title, xlabel): # Create and display a histogram using matplotlib
        
        if not data_counter: # Check if there's data to plot
            print("No data to visualize")
            return
        
        sorted_items = data_counter.most_common() # sort data by count that is descending order for better visualization
        
        # Separate labels and values for plotting
        labels = [item[0] for item in sorted_items]  # Extract country and continent names
        values = [item[1] for item in sorted_items]  # Extract counts
        
        # Create a new figure 
        plt.figure(figsize=(12, 6))
        
        # Create bar chart
        bars = plt.bar(labels, values, color='skyblue', edgecolor='navy', alpha=0.7)
        
        # Add value labels on top of each bar
        for bar, value in zip(bars, values):
            height = bar.get_height()
            plt.text(bar.get_x() + bar.get_width()/2., height,
                    f'{value}',  # Display the count
                    ha='center', va='bottom')  
        
        # Set labels and title
        plt.xlabel(xlabel, fontsize=12)
        plt.ylabel('Number of Views', fontsize=12)
        plt.title(title, fontsize=14, fontweight='bold')
        
        # Rotate x-axis labels if there are many items
        if len(labels) > 10:
            plt.xticks(rotation=45, ha='right')
        
        plt.grid(axis='y', alpha=0.3, linestyle='--') # added grid for better readability
        
        # Adjust layout to prevent label cutoff
        plt.tight_layout()
        
        # Display the plot
        plt.show()
    
    def print_results(self, counter, analysis_type): # Print formatted results to console
        
        # Print header
        print(f"{analysis_type} Analysis Results")
        print(f"Document UUID: {self.doc_uuid}")
        
        if not counter:
            print("No data found for this document")
            return
        
        sorted_items = counter.most_common()  # we sort by count
        
        total_views = sum(counter.values())
        
        # Print each item with formatting
        print("-" * 27)
        print(f"{'Location':<20} {'Views':<10} ")
        print("-" * 27)
        
        for location, count in sorted_items:
            # Print formatted row
            print(f"{location:<20} {count:<10} ")
        
        # Print summary
        print("-" * 27)
        print(f"{'TOTAL':<20} {total_views:<10} ")
        print(f"Unique {analysis_type}s: {len(counter)}")


def main(): # main to handle command-line execution, follows structure from labs
    
    # Set up command-line argument parser
    parser = argparse.ArgumentParser(
        description='Analyze document views by country and continent',
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    
    # Add required arguments
    parser.add_argument('-f', '--file',
                       required=True,
                       help='Path to the JSON data file')
    
    parser.add_argument('-d', '--doc',
                       required=True,
                       help='Document UUID to analyze')
    
    parser.add_argument('-t', '--task',
                       choices=['2a', '2b'],
                       default='2a',
                       help='Task to execute: 2a (country) or 2b (continent)')
    
    args = parser.parse_args() # Parse the command-line arguments
    
    try:
        analyzer = DocumentViewAnalyzer(args.file, args.doc) # Create analyzer instance
        
        # Execute the requested task
        if args.task == '2a':
            # Task 2a: Country analysis
            print("Executing Task 2a: Country Analysis...")
            
            country_data = analyzer.analyze_by_country() # Get country data
            analyzer.print_results(country_data, "Country")
            
            # Create visualization
            analyzer.create_histogram(
                country_data,
                f'Document Views by Country\n(Document: {args.doc[:8]}...)',
                'Country Code'
            )
            
        else:  
            # Task 2b: Continent analysis
            print("Executing Task 2b: Continent Analysis...")
            
            continent_data = analyzer.analyze_by_continent() # Get continent data
            analyzer.print_results(continent_data, "Continent")
            
            # Create visualization for continent
            analyzer.create_histogram(
                continent_data,
                f'Document Views by Continent\n(Document: {args.doc[:8]}...)',
                'Continent'
            )
    
    except InvalidDocumentException as e:
        # Handle custom exception for invalid documents
        print(f"Error: {e}")
        print("Please check that the document UUID is correct.")
        
    except FileNotFoundError as e:
        # Handle missing files
        print(f"Error: {e}")
        print("Please check that the file path is correct.")
        
    except Exception as e:
        # Handle any unexpected errors
        print(f"Unexpected error: {e}")
        print("Please check your input and try again.")


# Standard Python idiom: only run main() if this script is executed directly
if __name__ == '__main__':
    main()