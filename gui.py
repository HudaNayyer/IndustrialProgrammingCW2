# Import required libraries
import tkinter as tk  # For GUI creation (as in lab)
from tkinter import ttk  # For improved widgets
from tkinter import filedialog  # For file selection dialog
from tkinter import messagebox  # For popup messages
from tkinter import scrolledtext  # For scrollable text output
import matplotlib.pyplot as plt  
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg  # embedding plots
import subprocess  
import os  
import sys  


class DocumentTrackerGUI: # main gui application for document trackign analysis 
    
    def __init__(self, window): # initialize gui window 
       
        # Store window reference
        self.window = window
        
        # Set window properties
        self.window.title("Document Tracker Analysis (MH,HM,SM)")  # Window title
        self.window.geometry("800x600")  # Window size
        
        # Variables for user input 
        self.file_path = tk.StringVar()  # Selected file path
        self.doc_uuid = tk.StringVar()  # Document UUID
        self.user_uuid = tk.StringVar()  # User UUID (optional)
        
        self.setup_gui()  # Create all widgets
    
    def setup_gui(self): # settign up gui by creating and arranging all gui elements 
        
        # File Selection Row 
        # Label for file selection
        tk.Label(self.window, text="Data File:", font=('Arial', 10)).grid(
            row=0, column=0, padx=10, pady=10, sticky='w'
        )
        
        # Entry field for file path
        file_entry = tk.Entry(self.window, textvariable=self.file_path, width=40)
        file_entry.grid(row=0, column=1, padx=5, pady=10)
        
        # Browse button
        browse_btn = tk.Button(self.window, text="Browse", command=self.browse_file)
        browse_btn.grid(row=0, column=2, padx=5, pady=10)
        
        # document UUID Row 
        # Label for document UUID
        tk.Label(self.window, text="Document UUID:", font=('Arial', 10)).grid(
            row=1, column=0, padx=10, pady=5, sticky='w'
        )
        
        # Entry field for document UUID
        doc_entry = tk.Entry(self.window, textvariable=self.doc_uuid, width=40)
        doc_entry.grid(row=1, column=1, padx=5, pady=5)
        
        # User UUID Row (Optional) 
        # Label for user UUID
        tk.Label(self.window, text="User UUID (optional):", font=('Arial', 10)).grid(
            row=2, column=0, padx=10, pady=5, sticky='w'
        )
        
        # entry field for user UUID
        user_entry = tk.Entry(self.window, textvariable=self.user_uuid, width=40)
        user_entry.grid(row=2, column=1, padx=5, pady=5)
        
        # Task Buttons Frame
        # Create frame for buttons
        button_frame = tk.Frame(self.window)
        button_frame.grid(row=3, column=0, columnspan=3, padx=10, pady=20)
        
        # Task 2 buttons
        tk.Button(button_frame, text="Task 2a: Country Views", 
                 command=self.run_task_2a, width=20, bg='lightblue').grid(
            row=0, column=0, padx=5, pady=5
        )
        
        tk.Button(button_frame, text="Task 2b: Continent Views", 
                 command=self.run_task_2b, width=20, bg='lightblue').grid(
            row=0, column=1, padx=5, pady=5
        )
        
        # Task 3 buttons
        tk.Button(button_frame, text="Task 3a: User Agents", 
                 command=self.run_task_3a, width=20, bg='lightgreen').grid(
            row=1, column=0, padx=5, pady=5
        )
        
        tk.Button(button_frame, text="Task 3b: Browsers", 
                 command=self.run_task_3b, width=20, bg='lightgreen').grid(
            row=1, column=1, padx=5, pady=5
        )
        
        # Task 4 and 5 buttons
        tk.Button(button_frame, text="Task 4: Top Readers", 
                 command=self.run_task_4, width=20, bg='lightyellow').grid(
            row=2, column=0, padx=5, pady=5
        )
        
        tk.Button(button_frame, text="Task 5: Also Likes", 
                 command=self.run_task_5, width=20, bg='lightyellow').grid(
            row=2, column=1, padx=5, pady=5
        )
        
        # Task 6 button
        tk.Button(button_frame, text="Task 6: Generate Graph", 
                 command=self.run_task_6, width=20, bg='lightcoral').grid(
            row=3, column=0, padx=5, pady=5
        )
        
        # Clear button
        tk.Button(button_frame, text="Clear Output", 
                 command=self.clear_output, width=20, bg='gray').grid(
            row=3, column=1, padx=5, pady=5
        )
        
        # Text box for output 
        # Label for output
        tk.Label(self.window, text="Output:", font=('Arial', 10, 'bold')).grid(
            row=4, column=0, padx=10, pady=(10, 5), sticky='w'
        )
        
        # Scrolled text widget for output 
        self.output_text = scrolledtext.ScrolledText(
            self.window, 
            width=90, 
            height=15,
            wrap=tk.WORD,
            font=('Courier', 9)  
        )
        self.output_text.grid(row=5, column=0, columnspan=3, padx=10, pady=5)
        
        # status bar for extra user experience
        self.status_label = tk.Label(self.window, text="Ready", 
                                    bd=1, relief=tk.SUNKEN, anchor=tk.W)
        self.status_label.grid(row=6, column=0, columnspan=3, 
                              sticky=tk.W+tk.E, padx=10, pady=5)
    
    def browse_file(self): # allowing user to open file browser to select JSON file
        
        # Open file dialog
        filename = filedialog.askopenfilename(
            title="Select JSON Data File",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        
        # Set the file path if selected
        if filename:
            self.file_path.set(filename)
            self.update_status(f"File selected: {os.path.basename(filename)}")
    
    def update_status(self, message): # update status bar with a message 
        self.status_label.config(text=message)
        self.window.update()  # Force update
    
    def clear_output(self): # clearning output area
        self.output_text.delete('1.0', tk.END)
        self.update_status("Output cleared")
    
    def append_output(self, text): # adding text output area
        self.output_text.insert(tk.END, text + "\n")
        self.output_text.see(tk.END)  # Auto-scroll
        self.window.update()
    
    def validate_inputs(self, need_doc=True): # checking if input is valid before running
        
        # Check if file is selected
        if not self.file_path.get():
            messagebox.showerror("Error", "Please select a data file")
            return False
        
        # Check if file exists
        if not os.path.exists(self.file_path.get()):
            messagebox.showerror("Error", "File not found")
            return False
        
        # Check document UUID if needed
        if need_doc and not self.doc_uuid.get():
            messagebox.showerror("Error", "Please enter a document UUID")
            return False
        
        return True
    
    def run_command(self, script_name, args_list): # Run a Python script with arguments and capture output
        
        try:
            # Build command
            cmd = [sys.executable, script_name] + args_list
            
            # Run command and capture the output
            result = subprocess.run(
                cmd, 
                capture_output=True, 
                text=True,
                cwd=os.path.dirname(os.path.abspath(__file__))  # Run in the script directory
            )
            
            # Display output
            if result.stdout:
                self.append_output(result.stdout)
            
            if result.stderr:
                self.append_output(f"Errors: {result.stderr}")
            
            return result.returncode == 0
            
        except Exception as e:
            self.append_output(f"Error running command: {str(e)}")
            return False
    
    def run_task_2a(self): # runs task 2a by calling views2.py
    
        # Validate inputs
        if not self.validate_inputs():
            return
        
        # Clear output and update status
        self.clear_output()
        self.update_status("Running Task 2a: Country Analysis...")
        
        # Display header
        self.append_output("="*50)
        self.append_output("Task 2a: Country Views Analysis")
        self.append_output("="*50)
        
        # Run the command and set the file path and doc uuid to the user input 
        success = self.run_command(
            "views2.py",
            ["-f", self.file_path.get(), 
             "-d", self.doc_uuid.get(),
             "-t", "2a"]
        )
        
        # Update the status
        if success:
            self.update_status("Task 2a completed")
        else:
            self.update_status("Task 2a failed")
    
    def run_task_2b(self): # run task 2b (continents) by cahnging the task parameters to "2b"
        
        if not self.validate_inputs():
            return
        
        self.clear_output()
        self.update_status("Running Task 2b: Continent Analysis...")
        
        self.append_output("="*50)
        self.append_output("Task 2b: Continent Views Analysis")
        self.append_output("="*50)
        success = self.run_command(
            "views2.py",
            ["-f", self.file_path.get(),
             "-d", self.doc_uuid.get(),
             "-t", "2b"]
        )
        
        if success:
            self.update_status("Task 2b completed")
        else:
            self.update_status("Task 2b failed")
    
    def run_task_3a(self): # run task 3a which is the user agent analysis
        
        if not self.validate_inputs(need_doc=False):
            return
        
        self.clear_output()
        self.update_status("Running Task 3a: User Agent Analysis...")
        
        self.append_output("="*50)
        self.append_output("Task 3a: User Agent Analysis")
        self.append_output("="*50)

        success = self.run_command(
            "browsers3.py",
            ["-f", self.file_path.get(), "-t", "3a"]
        )
        
        if success:
            self.update_status("Task 3a completed")
        else:
            self.update_status("Task 3a failed")
    
    def run_task_3b(self): # 3b follows the same format but with changed task parameters 
        
        if not self.validate_inputs(need_doc=False):
            return
        
        self.clear_output()
        self.update_status("Running Task 3b: Browser Analysis...")
        
        self.append_output("="*50)
        self.append_output("Task 3b: Browser Analysis")
        self.append_output("="*50)
        
        # Run command
        success = self.run_command(
            "browsers3.py",
            ["-f", self.file_path.get(), "-t", "3b"]
        )
        
        if success:
            self.update_status("Task 3b completed")
        else:
            self.update_status("Task 3b failed")
    
    def run_task_4(self): # task 4 (gettign the top readers)
        
        if not self.validate_inputs(need_doc=False):
            return
        
        self.clear_output()
        self.update_status("Running Task 4: Top Readers...")
        
        self.append_output("="*50)
        self.append_output("Task 4: Top Readers by Reading Time")
        self.append_output("="*50)
        
        # Run command
        success = self.run_command(
            "readers4.py",
            ["-f", self.file_path.get()]
        )
        
        if success:
            self.update_status("Task 4 completed")
        else:
            self.update_status("Task 4 failed")
    
    def run_task_5(self): # task 5, the we call the also liked implementation
        
        if not self.validate_inputs():
            return
        
        self.clear_output()
        self.update_status("Running Task 5: Also Likes...")
        
        self.append_output("="*50)
        self.append_output("Task 5: Also Likes Recommendations")
        self.append_output("="*50)
        
        # Build arguments
        args = ["-f", self.file_path.get(), "-d", self.doc_uuid.get()]
        
        # Add user UUID if provided
        if self.user_uuid.get():
            args.extend(["-u", self.user_uuid.get()])
        
        # Run command
        success = self.run_command("likes5.py", args)
        
        if success:
            self.update_status("Task 5 completed")
        else:
            self.update_status("Task 5 failed")
    
    def run_task_6(self): # task 6 
        
        if not self.validate_inputs():
            return
        
        self.clear_output()
        self.update_status("Running Task 6: Graph Generation...") # update status with message
        
        self.append_output("="*50)
        self.append_output("Task 6: Graph Visualization")
        self.append_output("="*50)
        
        # Build arguments
        args = ["-f", self.file_path.get(), "-d", self.doc_uuid.get()]
        
        # Add user UUID if inputed by the user
        if self.user_uuid.get():
            args.extend(["-u", self.user_uuid.get()])
        
        # Run the command
        success = self.run_command("graph6.py", args)
        
        if success:
            self.update_status("Task 6 completed, check the output files in project folder")
            # Show info message
            messagebox.showinfo("Graph Created", 
                              "Graph files have been created:\n" +
                              "- also_likes.dot\n" +
                              "- also_likes.pdf\n" +
                              "- also_likes.png")
        else:
            self.update_status("Task 6 failed")


def main():  # main function to run the gui

    window = tk.Tk() # creating the main window 
    app = DocumentTrackerGUI(window) # create GUI application
    window.mainloop() # start the GUI event loop

# Run main if executed directly
if __name__ == '__main__':
    main()