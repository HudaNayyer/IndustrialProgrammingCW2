# Import required libraries
import argparse  
import sys 
import os 
import subprocess  


def run_task(task_script, args_list): # helper function to help run a task script with arguments
    
    try:
        # Build the full command
        cmd = [sys.executable, task_script] + args_list
        
        # Run the command
        result = subprocess.run(cmd)
        
        # Return the exit code
        return result.returncode
        
    except FileNotFoundError:
        print(f"Error: Script '{task_script}' not found")
        print("Make sure all task scripts are in the same directory")
        return 1
        
    except Exception as e:
        print(f"Error running task: {str(e)}")
        return 1


def main(): # main function that parses arguments and calls appropriate task scripts
    
    # Create argument parser with description
    parser = argparse.ArgumentParser(
        description='Unified interface for Document Tracker Analysis (MH,HM,SM)',
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    
    # Add arguments
    parser.add_argument(
        '-t', '--task',
        required=True,
        choices=['2a', '2b', '3a', '3b', '4', '5d', '6', '7'],
        help='Task to execute'
    )
    
    parser.add_argument(
        '-f', '--file',
        help='Path to JSON data file (required for tasks 2-6)'
    )
    
    parser.add_argument(
        '-d', '--doc',
        help='Document UUID (required for tasks 2a, 2b, 5d, 6)'
    )
    
    parser.add_argument(
        '-u', '--user',
        help='User UUID (optional for tasks 5d and 6)'
    )
    
    args = parser.parse_args()     # Parse arguments
    
    # Print header
    print(f"Document Tracker Analysis - Task {args.task}")
    print("-" * 50)
    
    # Validate inputs based on task
    # task 7 which is the GUI doesn't need any file arguments
    if args.task == '7':
        print("Launching GUI application...")
        return run_task('gui.py', [])
    
    # all other tasks need a file
    if not args.file:
        print("Error: File path is required for this task")
        print("Use -f or --file to specify the data file")
        return 1
    
    # Check if file exists
    if not os.path.exists(args.file):
        print(f"Error: File '{args.file}' not found")
        return 1
    
    # Handle each task
    if args.task == '2a':   # Task 2a: Country views
        if not args.doc:
            print("Error: Document UUID is required for task 2a")
            print("Use -d or --doc to specify the document")
            return 1
        
        print(f"Running Task 2a: Country Views Analysis")
        print(f"File: {args.file}")
        print(f"Document: {args.doc}")
        print()
        
        # Run views2.py with task 2a
        return run_task('views2.py', [
            '-f', args.file,
            '-d', args.doc,
            '-t', '2a'
        ])
    
    elif args.task == '2b':   # Task 2b: Continent views
        if not args.doc:
            print("Error: Document UUID is required for task 2b")
            print("Use -d or --doc to specify the document")
            return 1
        
        print(f"Running Task 2b: Continent Views Analysis")
        print(f"File: {args.file}")
        print(f"Document: {args.doc}")
        print()
        
        # Run views2.py with task 2b
        return run_task('views2.py', [
            '-f', args.file,
            '-d', args.doc,
            '-t', '2b'
        ])
    
    elif args.task == '3a':
        # Task 3a: User agents
        print(f"Running Task 3a: Browser Identification")
        print(f"File: {args.file}")
        print()
        
        # Run browsers3.py with task 3a
        return run_task('browsers3.py', [
            '-f', args.file,
            '-t', '3a'
        ])
    
    elif args.task == '3b':   # Task 3b 
        print(f"Running Task 3b: Short Browser Identification")
        print(f"File: {args.file}")
        print()
        
        # Run browsers3.py with task 3b
        return run_task('browsers3.py', [
            '-f', args.file,
            '-t', '3b'
        ])
    
    elif args.task == '4':  # Task 4: Top readers
        print(f"Running Task 4: Top Readers")
        print(f"File: {args.file}")
        print()
        
        # Run readers4.py
        return run_task('readers4.py', [
            '-f', args.file
        ])
    
    elif args.task == '5d':  # Task 5d: Also likes
        if not args.doc:
            print("Error: Document UUID is required for task 5d")
            print("Use -d or --doc to specify the document")
            return 1
        
        print(f"Running Task 5d: Also Likes Recommendations")
        print(f"File: {args.file}")
        print(f"Document: {args.doc}")
        
        if args.user:
            print(f"User: {args.user}")
        print()
        
        cmd_args = ['-f', args.file, '-d', args.doc]  # Build arguments for likes5.py
        
        # Then add user if inputed by user
        if args.user:
            cmd_args.extend(['-u', args.user])
        
        # Run likes5.py
        return run_task('likes5.py', cmd_args)
    
    elif args.task == '6': # Task 6: Graph visualization
        if not args.doc:
            print("Error: Document UUID is required for task 6")
            print("Use -d or --doc to specify the document")
            return 1
        
        print(f"Running Task 6: Graph Visualization")
        print(f"File: {args.file}")
        print(f"Document: {args.doc}")
        
        if args.user:
            print(f"User: {args.user}")
        print()
        
        cmd_args = ['-f', args.file, '-d', args.doc] # Build arguments for graph6.py
        
        # Add user if inputed 
        if args.user:
            cmd_args.extend(['-u', args.user])
        
        # Run graph6.py
        return run_task('graph6.py', cmd_args)
    
    else:
        print(f"Error: Unknown task '{args.task}'")
        return 1


# Run main if executed directly
if __name__ == '__main__':
    sys.exit(main())