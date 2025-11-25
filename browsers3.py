# Import required libraries
import json  
import argparse  
import re  # regualar expressions to extract browser name
import pandas as pd  
import matplotlib.pyplot as plt  
from collections import Counter  


class BrowserAnalyzer:
    
    def __init__(self, file_path):
        self.file_path = file_path  # Store the file path
        
        # define browser patterns for simplification
        self.browser_patterns = [
            (r'Firefox', 'Firefox'),     # Mozilla Firefox
            (r'Chrome', 'Chrome'),       # Google Chrome
            (r'Safari', 'Safari'),       # Apple Safari
            (r'Edge', 'Edge'),          # Microsoft Edge
            (r'Opera', 'Opera'),        # Opera browser
            (r'MSIE', 'Internet Explorer'),  # Old IE
            (r'Trident', 'Internet Explorer'),  
        ]
    
    def read_all_events(self): # generator to read all events from the file. Memory efficient approach for large files.
        try:
            
            with open(self.file_path, 'r') as file: # Open and read the JSON file

                # Process each line to remove white spaces and empty lines
                for line_number, line in enumerate(file, 1):
                    line = line.strip()
                    
                    if not line:
                        continue
                    
                    try:             
                        event = json.loads(line) # Parse JSON line
                        yield event
                        
                    # Skip invalid JSON lines
                    except json.JSONDecodeError:
                        print(f"Warning: Invalid JSON on line {line_number}")
                        continue
                        
        except FileNotFoundError:
            raise FileNotFoundError(f"Data file not found: {self.file_path}")
    
    def analyze_full_user_agents(self): # Task 3a: Count distinct full user-agent strings
        
        user_agent_counter = Counter() # counter for user-agent strings
        
        total_events = 0   # total events processed
        
        for event in self.read_all_events(): # Process each event in the file and count total events
            total_events += 1  
            
            user_agent = event.get('visitor_useragent') # get user-agent string
            
            # Only count non-empty user agents
            if user_agent:
                user_agent_counter[user_agent] += 1 # Increment count for this exact user-agent string
        
        # Print summary statistics
        print(f"\nProcessed {total_events} total events")
        print(f"Found {len(user_agent_counter)} distinct user-agent strings")
        
        return user_agent_counter
    
    def simplify_browser_name(self, user_agent): # Extract simplified browser name from user-agent string.
        
        # Return Unknown for empty/None user agents
        if not user_agent:
            return 'Unknown'
        
        for pattern, browser_name in self.browser_patterns: # Check each browser pattern

            if re.search(pattern, user_agent, re.IGNORECASE): # Use regex to search for pattern in user-agent
                return browser_name
        
        # If no pattern matches, return 'Other'
        return 'Other'
    
    def analyze_simplified_browsers(self): # Task 3b: Count browsers by simplified names.
        
        browser_counter = Counter() # counter for simplified browser names
        
        # Track statistics
        total_events = 0
        events_with_useragent = 0
        
        # Process each event
        for event in self.read_all_events():
            total_events += 1
            
            # Get user-agent string
            user_agent = event.get('visitor_useragent')
            
            if user_agent:
                events_with_useragent += 1
                
                # Simplify the browser name
                browser_name = self.simplify_browser_name(user_agent)
                
                # Increment counter for this browser
                browser_counter[browser_name] += 1
        
        # Print summary
        print(f"\nProcessed {total_events} total events")
        print(f"Events with user-agent data: {events_with_useragent}")
        print(f"Found {len(browser_counter)} distinct browser types")
        
        return browser_counter
    
    
    def create_histogram(self, data_counter, title, xlabel):
    
        if not data_counter:
            print("No data to visualize")
            return

        # Sort items by count descending
        items = data_counter.most_common(10)

        labels = [item[0] for item in items]
        values = [item[1] for item in items]

        plt.figure(figsize=(12, 6))

        # Bar histogram
        plt.bar(range(len(values)), values, color='skyblue', edgecolor='black')

        # X-axis labels
        plt.xticks(range(len(labels)), labels, rotation=45, ha='right', fontsize=9)

        plt.title(title, fontsize=14, fontweight='bold')
        plt.xlabel(xlabel, fontsize=12)
        plt.ylabel("Count", fontsize=12)

        plt.grid(axis='y', linestyle='--', alpha=0.4)

        plt.tight_layout()
        plt.show()

    
    def print_results(self, counter, task_type):
    
        print(f"Task 3{task_type}: Browser Analysis Results")

        # Check for data
        if not counter:
            print("No data found")
            return
        
        # Calculate total
        total = sum(counter.values())
        
        # Determine how many items to show
        if task_type == 'a':
            # For full user agents, show top 10
            items_to_show = counter.most_common(10)
            print(f"\nTop 10 User-Agent Strings (out of {len(counter)} total):")
        else:
            # For simplified browsers, show all
            items_to_show = counter.most_common()
            print(f"\nBrowser Distribution:")
        
        # Print header row
        print(f"\n{'Browser/User-Agent':<40} {'Count':<10} ")
        
        # Print each item
        for item, count in items_to_show:
            display_name = item[:37] + "..." if len(item) > 40 else item # Truncate long strings for display
            
            print(f"{display_name:<40} {count:<10}")
        
        # Print summary
        print(f"{'TOTAL':<40} {total:<10} ")
        
        # Additional stats for task 3a
        if task_type == 'a' and len(counter) > 10:
            print(f"\n(Showing top 10 out of {len(counter)} unique user-agents)")


def main():

    parser = argparse.ArgumentParser(
        description='Analyze browser usage from event data',
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    
    # Add arguments
    parser.add_argument('-f', '--file',
                       required=True,
                       help='Path to JSON data file')
    
    parser.add_argument('-t', '--task',
                       choices=['3a', '3b'],
                       required=True,
                       help='Task: 3a (full user-agents) or 3b (simplified browsers)')
    
   
    args = parser.parse_args()  # Parse arguments
    
    try:
        # Create analyzer instance
        analyzer = BrowserAnalyzer(args.file)
        
        # Execute requested task
        if args.task == '3a':
            print("Executing Task 3a: Full User-Agent Analysis...")
            
            # Analyze user agents
            user_agent_data = analyzer.analyze_full_user_agents()
            
            # Print results
            analyzer.print_results(user_agent_data, 'a')
            
            analyzer.create_histogram(
            user_agent_data,
            title='Full User-Agent Histogram',
            xlabel='User-Agent String'
            )
            
        else:  
            # Task 3b: Simplified browser analysis
            print("Executing Task 3b: Simplified Browser Analysis...")
            
            # Analyze browsers
            browser_data = analyzer.analyze_simplified_browsers()
            
            # Print results
            analyzer.print_results(browser_data, 'b')
            
            analyzer.create_histogram(
                browser_data,
                title='Browser Distribution (Simplified) - Histogram',
                xlabel='Browser Name'
            )

    
    except FileNotFoundError as e:
        # Handle missing file
        print(f"Error: {e}")
        print("Please check the file path and try again.")
        
    except Exception as e:
        # Handle unexpected errors
        print(f"Unexpected error: {e}")
        print("Please check your input and try again.")


# Run main function if script is executed directly
if __name__ == '__main__':
    main()