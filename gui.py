import customtkinter as ctk
import tkinter.filedialog as fd
from tkinter import messagebox
import matplotlib.pyplot as plt

# TASK MODULES
from views2 import DocumentViewAnalyzer
from browsers3 import BrowserAnalyzer
from readers4 import top_readers
from likes5 import also_like, build_indices
from graph6 import DocumentGraphVisualizer


# colour 
COLORS = {
    'dark_gray': '#3A3A3A',
    'sage_green': '#6B8E6B',
    'light_gray': '#C4C1BA',
    'off_white': '#F5F5F0',
    'white': '#FFFFFF',
    'accent': '#8B9F8B'
}

ctk.set_appearance_mode("dark")     # Make the user interface to be dark
ctk.set_default_color_theme("green") # decided on a colour scheme (green)


class CW2GUI(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("CW2 Data Analytics")
        self.state("zoomed")  # Fullscreen window

        # main layout has two columns
        self.grid_columnconfigure(0, weight=0)   # left panel fixed
        self.grid_columnconfigure(1, weight=1)   # right panel which expands
        self.grid_rowconfigure(0, weight=1)

        # left panel
        self.left_panel = ctk.CTkFrame(
            self,
            width=320,
            fg_color=COLORS['dark_gray'],
            corner_radius=0
        )
        self.left_panel.grid(row=0, column=0, sticky="nsw") # Position left sidebar in top-left and stick it to north, south, and west edges
        self.left_panel.grid_propagate(False) # keeping the set width and height fixed

        title = ctk.CTkLabel(
            self.left_panel, text="IP CW2 Group 18",
            font=("Helvetica", 20, "bold"),
            text_color=COLORS["off_white"]
        )
        title.pack(pady=(20, 15))

        # input fields
        # File input
        self.file_label = ctk.CTkLabel(
            self.left_panel, text="Data File:",
            text_color=COLORS['white']
        )
        self.file_label.pack(anchor="w", padx=20)

        file_frame = ctk.CTkFrame(self.left_panel, fg_color="transparent")
        file_frame.pack(fill="x", pady=5, padx=20)

        self.file_entry = ctk.CTkEntry(file_frame, placeholder_text="Select JSON file")
        self.file_entry.pack(side="left", fill="x", expand=True)

        browse_btn = ctk.CTkButton(
            file_frame, text="Browse", fg_color=COLORS['sage_green'],
            hover_color=COLORS['accent'], command=self.browse_file
        )
        browse_btn.pack(side="left", padx=(10, 0))

        # document UUID
        self.doc_label = ctk.CTkLabel(
            self.left_panel, text="Document UUID:",
            text_color=COLORS['white']
        )
        self.doc_label.pack(anchor="w", padx=20, pady=(15, 0))

        self.doc_entry = ctk.CTkEntry(self.left_panel, placeholder_text="Enter document UUID")
        self.doc_entry.pack(fill="x", padx=20, pady=5)

        # user UUID
        self.user_label = ctk.CTkLabel(
            self.left_panel, text="User UUID (optional):",
            text_color=COLORS['white']
        )
        self.user_label.pack(anchor="w", padx=20)

        self.user_entry = ctk.CTkEntry(self.left_panel, placeholder_text="Enter user UUID")
        self.user_entry.pack(fill="x", padx=20, pady=5)

        # button panel
        btn_title = ctk.CTkLabel(
            self.left_panel, text="Analysis Tasks",
            font=("Helvetica", 15, "bold"),
            text_color=COLORS['off_white']
        )
        btn_title.pack(anchor="w", padx=20, pady=(20, 10))

        # Helper to generate rounded buttons
        def add_button(label, command):
            btn = ctk.CTkButton(
                self.left_panel,
                text=label,
                fg_color=COLORS['sage_green'],
                hover_color=COLORS['accent'],
                corner_radius=12,
                command=command
            )
            btn.pack(fill="x", padx=20, pady=4)

        add_button("2a – Country Views", self.run_task_2a)
        add_button("2b – Continent Views", self.run_task_2b)
        add_button("3a – Browser Analysis (Full UA)", self.run_task_3a)
        add_button("3c – Browser Types", self.run_task_3b)
        add_button("4 – Top Readers", self.run_task_4)
        add_button("5d – Recommendations (List)", self.run_task_5)
        add_button("6 – Recommendations Graph", self.run_task_6)

        # Clear Output
        clear_btn = ctk.CTkButton(
            self.left_panel,
            text="Clear Output",
            fg_color=COLORS['light_gray'],
            text_color="black",
            hover_color=COLORS['accent'],
            corner_radius=12,
            command=self.clear_output
        )
        clear_btn.pack(fill="x", padx=20, pady=(15, 0))

        # -------------------------------

        # right panel : contains the output and logs of tasks aswell
        self.right_panel = ctk.CTkFrame(self, fg_color=COLORS['off_white'])
        self.right_panel.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)
        self.right_panel.grid_rowconfigure(1, weight=1)
        self.right_panel.grid_columnconfigure(0, weight=1)

        log_label = ctk.CTkLabel(
            self.right_panel,
            text="Output",
            text_color=COLORS['dark_gray'],
            font=("Helvetica", 15, "bold")
        )
        log_label.grid(row=0, column=0, sticky="w", padx=10, pady=10)

        self.output_box = ctk.CTkTextbox(
            self.right_panel,
            fg_color=COLORS['white'],
            text_color=COLORS['dark_gray'],
            corner_radius=8
        )
        self.output_box.grid(row=1, column=0, sticky="nsew", padx=10, pady=(0, 10))

    # Logic functions for individual tasks 

    def browse_file(self):
        file_path = fd.askopenfilename(
            title="Select Data File",
            filetypes=[("JSON files", "*.json")]
        )
        if file_path:
            self.file_entry.delete(0, "end")
            self.file_entry.insert(0, file_path)

    def clear_output(self):
        self.output_box.delete("1.0", "end")

    #  task 2a 
    def run_task_2a(self):
        file = self.file_entry.get()
        doc = self.doc_entry.get()
        if not file or not doc:
            messagebox.showerror("Error", "Missing file or document UUID.")
            return

        analyzer = DocumentViewAnalyzer(file, doc)
        hist = analyzer.analyze_by_country()
        analyzer.create_histogram(hist, f"Views by Country for document : {doc}", "Country")
        self.output_box.insert("end", f"\n(2a) Country views histogram generated.\n")

    #  task 2b 
    def run_task_2b(self):
        file = self.file_entry.get()
        doc = self.doc_entry.get()
        if not file or not doc:
            messagebox.showerror("Error", "Missing file or document UUID.")
            return

        analyzer = DocumentViewAnalyzer(file, doc)
        hist = analyzer.analyze_by_continent()
        analyzer.create_histogram(hist, f"Views by Continent for document : {doc}", "Continent")
        self.output_box.insert("end", f"\n(2b) Continent views histogram generated.\n")

    #  task 3a 
    def run_task_3a(self):
        file = self.file_entry.get()
        analyzer = BrowserAnalyzer(file)
        data = analyzer.analyze_full_user_agents()
        analyzer.create_histogram(data, "Full User-Agent Histogram", "User-Agent")
        self.output_box.insert("end", "\n(3a) Full UA Browser Analysis completed.\n")

    #  task 3c 
    def run_task_3b(self):
        file = self.file_entry.get()
        analyzer = BrowserAnalyzer(file)
        data = analyzer.analyze_simplified_browsers()
        analyzer.create_histogram(data, "Browser Types Histogram", "Browser")
        self.output_box.insert("end", "\n(3c) Browser types histogram generated.\n")

    #  task 4 
    def run_task_4(self):
        file = self.file_entry.get()
        data = top_readers(file)
        self.output_box.insert("end", "\n(4) Top Readers:\n")
        self.output_box.insert("end", "UUID                                Seconds\n")
        self.output_box.insert("end", "----------------------------------------------\n")

        for uuid, t in data:
            self.output_box.insert(
                "end", 
                f"{uuid:<35} {t}\n"
            ) #140206010823-b14c9d966be950314215c17923a04af7

    #  task 5d 
    def run_task_5(self):
        file = self.file_entry.get()
        doc = self.doc_entry.get()
        user = self.user_entry.get() or None

        if not file or not doc:
            messagebox.showerror("Error", "Enter file path and document UUID.")
            return

        # Build indices exactly like we did in 5likes.py
        doc_to_readers, reader_to_docs = build_indices(file)

        # Get also liked documents 
        results = also_like(doc_to_readers, reader_to_docs, doc, user)

        self.output_box.insert("end", f"\n(5d) Top 10 'Also Liked' Documents for: {doc}:\n")

        if not results:
            self.output_box.insert("end", "no shared readers\n")
            return

        self.output_box.insert("end", "Document UUID                          Shared Readers\n")
        self.output_box.insert("end", "-----------------------------------------------------\n")

        for d, count in results[:10]:
            self.output_box.insert("end", f"{d:<40} : {count}\n")


    #  task 6 
    def run_task_6(self):
        file = self.file_entry.get()
        doc = self.doc_entry.get()
        user = self.user_entry.get() or None

        if not file or not doc:
            messagebox.showerror("Error", "Enter file path and document UUID.")
            return

        visualizer = DocumentGraphVisualizer(file)
        visualizer.create_graph(
            doc_uuid=doc,
            user_uuid=user,
            output_name="also_likes_gui"
        )

        self.output_box.insert(
            "end",
            f"\n(6) Recommendation graph generated for document: {doc}\n"
            f"     User highlighted: {user if user else 'None'}\n"
            f"     The files have been saved as: also_likes_gui.pdf/.png/.ps\n"
        )

        messagebox.showinfo("Success", "Graph saved as also_likes.png, check folder for results")


# main to run the program
if __name__ == "__main__":
    app = CW2GUI()
    app.mainloop()
