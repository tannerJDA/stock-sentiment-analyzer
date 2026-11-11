import tkinter as tk
from tkinter import ttk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import yfinance as yf
import threading

import get_data

# colors
BG = "#F3F5F8"
CARD = "#FFFFFF"
TEXT = "#253247"
MUTED = "#64748B"
ACCENT = "#C7752B"
ACCENT_HOVER = "#A85E20"
BORDER = "#DDE4EB"
SOFT = "#F8FAFC"
POSITIVE = "#2C9A6B"
NEGATIVE = "#D65B63"
NEUTRAL = "#A8B3C1"

# ======
# Overall application container, holds the welcome screen and then the main program screen
# ======
class Application:
    def __init__(self, root):
        self.root = root
        self.root.geometry("700x200")
        self.root.minsize(800, 500)

        self.root.configure(bg="#F3F5F8")
        # Configure ttk styles
        self.style = ttk.Style()
        self.style.theme_use("clam")

        self.configure_styles()

        # welcome screen
        self.welcome_screen = WelcomeScreen(self.root, on_submit=self.open_dashboard)

    def open_dashboard(self, ticker):
        print("open dashboard")

        # delete window containing welcome screen
        self.welcome_screen.main_frame.destroy()

        # instantiate dashboard with chosen ticker
        self.dashboard_screen = DashboardScreen(self.root, ticker=ticker)

    def configure_styles(self):

        self.style.configure("Card.TFrame", background=CARD)

        # Main background
        self.style.configure(
            "Background.TFrame",
            background="#F3F5F8"
        )

        # Main title
        self.style.configure(
            "Title.TLabel",
            background="#F3F5F8",
            foreground="#253247",
            font=("Segoe UI", 30, "bold")
        )

        # Description
        self.style.configure(
            "Description.TLabel",
            background="#F3F5F8",
            foreground="#64748B",
            font=("Segoe UI", 12)
        )

        # Example tickers
        self.style.configure(
            "Subtitle.TLabel",
            background="#F3F5F8",
            foreground="#64748B",
            font=("Segoe UI", 10)
        )

        # Search entry
        self.style.configure(
            "Search.TEntry",
            padding=12,
            font=("Segoe UI", 13)
        )

        # Orange action button
        self.style.configure(
            "Accent.TButton",
            font=("Segoe UI", 12, "bold"),
            padding=(22, 12),
            background="#C7752B",
            foreground="#FFFFFF",
            borderwidth=0
        )

        # Hover and pressed button colors
        self.style.map(
            "Accent.TButton",
            background=[
                ("active", "#A85E20"),
                ("pressed", "#8F4C17")
            ]
        )


class DashboardScreen:
    def __init__(self, root, ticker):
        self.root = root
        self.ticker = ticker
        self.long_name = yf.Ticker(ticker).info.get("longName")

        # get sectory news
        self.sector_news, self.sector_category = get_data.gather_sector_news(self.ticker)

        # overall frame
        self.main_frame = ttk.Frame(self.root, style="Background.TFrame")
        self.main_frame.pack(expand=True, fill='both')

        # input frame for labels
        self.input_frame = ttk.Frame(self.main_frame, style="Card.TFrame", padding=(22, 16))
        #self.input_frame.pack(side='top', fill='x')
        self.input_frame.grid(row=0, column=0, padx=24, pady=(22, 16), sticky="ew")
        self.controls = ttk.Frame(self.input_frame, style="Card.TFrame")
        self.controls.pack(anchor='center')

        self.input_frame.grid_rowconfigure(0, weight=1)
        self.input_frame.grid_columnconfigure(0, weight=1) # for centering elements

        # ======
        # Input Widgets
        # ======

        # date range button
        self.date_range_but = ttk.Combobox(
            self.controls,
            values=['30d', '60d', '90d'],
            state="readonly",
            width=5
        )

        self.date_range_but.set('30d')
        #self.date_range_but.grid(row=0, column=0, padx=5, pady=5, sticky="")
        self.date_range_but.pack(side='left', padx=(0, 22))

        # ticker entry box
        self.ticker_entry = ttk.Entry(self.controls, width=9, style="Search.TEntry", font=("Segoe UI", 11))
        #self.ticker_entry.grid(row=0, column=1, padx=5, pady=5, sticky="")
        self.ticker_entry.pack(side="left", padx=(0, 11))

        self.ticker_entry.focus_set() # set focus on text box
        self.ticker_entry.bind("<Return>", lambda e: self.update_dashboard()) # bind to enter button

        # enter button
        self.enter_but = ttk.Button(
            self.controls,
            text ="Enter!",
            command = self.update_dashboard,
            style="Accent.TButton"
        )

        #self.enter_but.grid(row=0, column=2, padx=5, pady=5, sticky="")
        self.enter_but.pack(side='left', padx=(0, 11))

        # ========

        # content frame will be split in two -> company frame, sector frame
        self.content_frame = ttk.Frame(self.main_frame, style="Background.TFrame")
        #self.content_frame.pack(fill='x')
        self.content_frame.grid(row=1, column=0, padx=24, pady=(0, 7), sticky='nsew')

        # set up orientation for the two columns to be evenly spaced
        self.content_frame.columnconfigure(0, weight=1, uniform='panels')
        self.content_frame.columnconfigure(1, weight=1, uniform='panels')
        self.content_frame.rowconfigure(0, weight=1)
        '''

        # frame for company info and sentiments
        self.company_info_frame = ttk.Frame(self.content_frame, style="Background.TFrame")
        self.company_info_frame.grid(row=0, column=0)

        # frame for sector info and sentiments
        self.sector_info_frame = ttk.Frame(self.content_frame, style="Background.TFrame")
        self.sector_info_frame.grid(row=0, column=1)

        self.company_top_lbl = ttk.Label(self.company_info_frame, text="Company News")
        self.company_top_lbl.pack(side='top')

        self.company_sub_lbl = ttk.Label(self.company_info_frame, text=self.long_name)
        self.company_sub_lbl.pack(side='top')

        self.sector_top_lbl = ttk.Label(self.sector_info_frame, text="Sector News")
        self.sector_top_lbl.pack(side='top')

        self.sector_sub_lbl = ttk.Label(self.sector_info_frame, text=self.sector_category)
        self.sector_sub_lbl.pack(side='top')'''



    def update_dashboard(self):
        print('Update dashboard func')
        #print(f"time span: {self.date_range_but.get()}")


class WelcomeScreen:
    def __init__(self, root, on_submit):
        self.root = root
        self.on_submit = on_submit

        self.main_frame = ttk.Frame(self.root, style="Background.TFrame")
        self.main_frame.pack(expand=True, fill='both')

        self.upper_frame = ttk.Frame(self.main_frame, style="Background.TFrame")
        self.upper_frame.pack(fill='x')

        self.top_lbl = ttk.Label(self.upper_frame, text="Stock Sentiment Analyzer", style="Title.TLabel")
        self.top_lbl.pack()

        self.desc_lbl = ttk.Label(self.upper_frame, style="Description.TLabel", justify="center", text="Enter a stock ticker to analyze recent headlines, sentiment distribution, and price performance")
        self.desc_lbl.pack()

        self.input_frame = ttk.Frame(self.main_frame, style="Background.TFrame")
        self.input_frame.pack(side="top")

        self.user_in = ttk.Entry(self.input_frame, style="Search.TEntry")
        self.user_in.grid(row=0, column=0, padx=5, pady=5)

        self.user_in.focus_set()

        self.enter_but = ttk.Button(self.input_frame, text="Enter!", command=self.run_main_prog)
        self.enter_but.grid(row=0, column=1, padx=5, pady=5)

        # bind button to enter
        self.user_in.bind(
            "<Return>",
            lambda event: self.run_main_prog()
        )

    def run_main_prog(self):
        ticker = self.user_in.get().strip().upper()
        print(f'Running main program with: {ticker}')

        if not ticker:
            return

        self.on_submit(ticker)


class NewsFeed:
    def __init__(self, parent, title, subtitle):
        super().__init__(parent, style="Card.TFrame", padding=(22, 20))

        self.articles = []

        # title label
        self.title = ttk.Label(self, text=title, style="PanelTitle.TLabel")
        self.title.pack(anchor='w')

        # accent line
        tk.Frame(self, bg=ACCENT, width=62, height=3).pack(anchor='w', pady=(10, 10))

        # subtitle
        self.subtitle = ttk.Label(self, text=subtitle, style="PanelSubtitle.TLabel", wraplength=420)
        self.subtitle.pack(anchor='w', pady=(0, 10))


if __name__ == "__main__":

    root = tk.Tk()
    app = Application(root)
    root.mainloop()