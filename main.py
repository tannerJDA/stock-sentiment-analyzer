import tkinter as tk
from tkinter import ttk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import yfinance as yf
import threading
from datetime import date, timedelta

import sent_analysis
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
        self.root.geometry("1100x760")
        self.root.minsize(880, 600)
        self.root.configure(bg=BG)


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
        s = self.style
        s.configure("Background.TFrame", background=BG)
        s.configure("Card.TFrame", background=CARD)
        s.configure("Title.TLabel", background=BG, foreground=TEXT,
                    font=("Helvetica", 30, "bold"))
        s.configure("Description.TLabel", background=BG, foreground=MUTED,
                    font=("Helvetica", 12))
        s.configure("Subtitle.TLabel", background=BG, foreground=MUTED,
                    font=("Helvetica", 10))

        s.configure("PanelTitle.TLabel", background=CARD, foreground=TEXT,
                    font=("Helvetica", 20, "bold"))
        s.configure("PanelSubtitle.TLabel", background=CARD, foreground=MUTED,
                    font=("Helvetica", 11))
        s.configure("Section.TLabel", background=CARD, foreground=TEXT,
                    font=("Helvetica", 12, "bold"))
        s.configure("SmallCard.TLabel", background=CARD, foreground=MUTED,
                    font=("Helvetica", 9))
        s.configure("Toolbar.TLabel", background=CARD, foreground=TEXT,
                    font=("Helvetica", 10, "bold"))
        s.configure("Status.TLabel", background=BG, foreground=MUTED,
                    font=("Helvetica", 9))

        s.configure("Search.TEntry", padding=9, fieldbackground=CARD,
                    foreground=TEXT, bordercolor=BORDER, lightcolor=BORDER,
                    darkcolor=BORDER)
        s.configure("Range.TCombobox", padding=8, fieldbackground=CARD,
                    background=CARD, foreground=TEXT, bordercolor=BORDER,
                    lightcolor=BORDER, darkcolor=BORDER)

        s.configure("Accent.TButton", font=("Helvetica", 10, "bold"),
                    padding=(19, 10), background=ACCENT,
                    foreground="white", borderwidth=0)
        s.map("Accent.TButton", background=[("active", ACCENT_HOVER),
                                           ("pressed", "#8F4C17")])
        s.configure("Secondary.TButton", font=("Helvetica", 10, "bold"),
                    padding=(16, 10), background=CARD, foreground=TEXT,
                    borderwidth=1, bordercolor=BORDER)
        s.map("Secondary.TButton", background=[("active", SOFT)])


class DashboardScreen:
    def __init__(self, root, ticker):
        self.root = root
        self.ticker = ticker
        self.long_name = yf.Ticker(ticker).info.get("longName")

        # get sectory news
        self.sector_news, self.sector_category = get_data.gather_sector_news(self.ticker)
        self.company_news = get_data.gather_headlines(self.ticker, date.today()-timedelta(days=30))


        # overall frame
        self.main_frame = ttk.Frame(self.root, style="Background.TFrame")
        self.main_frame.pack(expand=True, fill='both')

        # set row and col weights
        self.main_frame.columnconfigure(0, weight=1)
        self.main_frame.rowconfigure(0, weight=0)
        self.main_frame.rowconfigure(1, weight=1)

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
        self.ticker_entry = ttk.Entry(self.controls, width=9, style="Search.TEntry", font=("Helvetica", 11))
        #self.ticker_entry.grid(row=0, column=1, padx=5, pady=5, sticky="")
        self.ticker_entry.pack(side="left", padx=(0, 11))

        self.ticker_entry.focus_set() # set focus on text box
        self.ticker_entry.bind("<Return>", lambda e: self.update_dashboard()) # bind to enter button
        self.ticker_entry.insert(0, (self.ticker).upper())

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
        self.content_frame.grid(row=1, column=0, padx=18, pady=(0, 18), sticky='nsew')

        # set up orientation for the two columns to be evenly spaced
        self.content_frame.columnconfigure(0, weight=1, uniform='panels')
        self.content_frame.columnconfigure(1, weight=1, uniform='panels')
        self.content_frame.rowconfigure(0, weight=1)

        # panel for company news
        self.company_news_panel = NewsPanel(self.content_frame, "Company News", self.long_name, self.company_news)
        self.company_news_panel.grid(row=0, column=0, sticky='nsew', padx=(0, 7))
        #self.company_news_panel.set_articles(self.company_news)

        # panel for sector news
        self.sector_news_panel = NewsPanel(self.content_frame, "Sector News", self.sector_category, self.sector_news)
        self.sector_news_panel.grid(row=0, column=1, sticky='nsew', padx=(7, 0))
        #self.sector_news_panel.set_articles(self.sector_news)
    

    def update_dashboard(self):
        print('Update dashboard func')
        #print(f"time span: {self.date_range_but.get()}")


class WelcomeScreen:
    def __init__(self, root, on_submit):
        self.root = root
        self.on_submit = on_submit

        self.main_frame = ttk.Frame(self.root, style="Background.TFrame")
        self.main_frame.pack(expand=True, fill='both')

        self.content_frame = ttk.Frame(self.main_frame, style="Background.TFrame")
        self.content_frame.place(relx=0.5, rely=0.46, anchor='center')
        '''
        self.upper_frame = ttk.Frame(self.main_frame, style="Background.TFrame")
        self.upper_frame.pack(fill='x')
        '''
        self.top_lbl = ttk.Label(self.content_frame, text="Stock Sentiment Analyzer", style="Title.TLabel")
        self.top_lbl.pack(pady=(0, 14))

        self.desc_lbl = ttk.Label(self.content_frame, style="Description.TLabel", justify="center", text="Enter a stock ticker to analyze recent headlines, sentiment distribution, and price performance")
        self.desc_lbl.pack()

        self.input_frame = ttk.Frame(self.content_frame, style="Background.TFrame")
        self.input_frame.pack()

        self.user_in = ttk.Entry(self.input_frame, style="Search.TEntry", font=("Helvetica", 11))
        self.user_in.grid(row=0, column=0, padx=(0, 9))

        self.user_in.focus_set()

        self.enter_but = ttk.Button(self.input_frame, text="Enter!", command=self.run_main_prog, style="Accent.TButton")
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


class NewsPanel(ttk.Frame):
    def __init__(self, parent, title, subtitle, articles):
        super().__init__(parent, style="Card.TFrame", padding=(22, 20))

        self.articles = articles

        # title label
        self.title = ttk.Label(self, text=title, style="PanelTitle.TLabel")
        self.title.pack(anchor='w')

        # accent line
        tk.Frame(self, bg=ACCENT, width=62, height=3).pack(anchor='w', pady=(10, 10))

        # subtitle
        self.subtitle = ttk.Label(self, text=subtitle, style="PanelSubtitle.TLabel", wraplength=420)
        self.subtitle.pack(anchor='w', pady=(0, 10))

        # pie chart 
        self.figure = Figure(figsize=(3.2, 2.1), # set the figures initial size, in inches
                             dpi=100, 
                             facecolor=CARD)
        self.ax = self.figure.add_subplot(111) # create space for 1 plot

        # position the plot within a few units of each edge so it occupies all of its given space
        self.figure.subplots_adjust(left=0.03,
                                    right=0.97,
                                    bottom=0.02,
                                    top=0.98)

        self.canvas = FigureCanvasTkAgg(self.figure, master=self)
        self.canvas.get_tk_widget().configure(bg=CARD, highlightthickness=0)
        self.canvas.get_tk_widget().pack(fill="x", pady=(0, 5))

        ttk.Label(self, text="RECENT HEADLINES", style="Section.TLabel").pack(
                fill='x', anchor="w", pady=(5, 8)
        )

        self.textbox_frame = HeadlinesTextBox(parent=self)
        self.textbox_frame.pack(
            fill="both",
            expand=True,
            pady=(10, 0)
        )

        self.update_newsfeed()



    def set_articles(self, articles):
        self.articles = articles

    def update_newsfeed(self):

        #print('update newsfeed')
        #print(f'Articles: {self.articles}')
        
        # run sent scan and update pie chart based on articles that have been set
        res, pos, neg, neu = self.run_sent_scan(self.articles)

        self.textbox_frame.update_text(res)

        self.ax.pie(
            [pos, neg, neu],
            labels=['Positive', 'Negative', 'Neutral'],
            explode=(0, 0, 0),
            shadow=True,
            colors=["#19A514", "#e70b0b", "#757171"],
            wedgeprops={"width": 0.45, "edgecolor": CARD,
                        "linewidth": 3}
        )

        self.canvas.draw()

    
    def run_sent_scan(self, articles):

        #news_results = get_data.gather_headlines.gather(ticker, date.today()-timedelta(days=30))
        results = []
        positives = 0
        negatives = 0
        neutrals = 0


        # step 2 - parse through all news results and analyze sentiment
        for res in articles:
            #print(res["headline"])

            sent = sent_analysis.sent(res['headline'])

            if sent == 'Positive':
                positives += 1
            elif sent == 'Negative':
                negatives += 1
            elif sent == 'Neutral':
                neutrals += 1

            results.append({
                'Headline': res['headline'],
                'Sentiment': sent
            })


        #pie_chart.update([positives, negatives, neutrals])
        return results, positives, negatives, neutrals


# textbox object that inherits from ttk Frame
class HeadlinesTextBox(ttk.Frame):

    def __init__ (self, parent, **kwargs):
        super().__init__(parent)

        # Allow the textbox's grid cell to expand
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

        # actual text box
        self.textbox = tk.Text(
            self,
            wrap='word',
            width=1,
            height=8,
            yscrollcommand=lambda first, last: self.scrollbar.set(first, last),
            bg=SOFT,
            fg=TEXT,
            font=("Helvetica", 10),
            relief='flat',
            #borderwidth=0,
            highlightthickness=1,
            highlightbackground=BORDER,
            highlightcolor=BORDER,
            #padx=13, pady=11, spacing1=1, spacing2=3, spacing3=0,
            cursor="arrow",
            takefocus=0,
            **kwargs
        )

        '''
        self.textbox = tk.Text(
                            self,
                            yscrollcommand=lambda first, last: self.scrollbar.set(first, last),
                            bg="white",
                            fg="black",
                            font=("Helvetica", 11),
                            wrap="word",
                            height=12,
                            width=50
                        )
        '''
        
        #self.textbox.grid(row=0, column=0, sticky="nsew")
        self.textbox.grid(
            row=0,
            column=0,
            sticky="nsew"
        )

        # create scrollbar
        
        self.scrollbar = ttk.Scrollbar(self, 
                                        orient='vertical',
                                        command=self.textbox.yview)
        
        self.scrollbar.grid(row=0, column=1, sticky="ns")

        
        # === text style configurations
        self.textbox.tag_configure("positive", foreground=POSITIVE,
                                    font=("Helvetica", 9, "bold"))
        
        self.textbox.tag_configure("negative", foreground=NEGATIVE,
                                    font=("Helvetica", 9, "bold"))
        
        self.textbox.tag_configure("neutral", foreground=MUTED,
                                    font=("Helvetica", 9, "bold"))
        
        self.textbox.tag_configure("headline", foreground=TEXT,
                                    font=("Helvetica", 10),
                                    lmargin1=0, lmargin2=0)
        
        
        self.textbox.tag_configure("divider", foreground=BORDER,
                                    font=("Helvetica", 8))
        

        # connect scrollbar
        self.scrollbar.config(command=self.textbox.yview)

    def clear(self):
        # remove all text
        self.textbox.config(state='normal') # enable textbox so it can be editted
        self.textbox.delete("1.0", tk.END) # delete everything from start to finish

    def update_text(self, data):

        self.clear()

        # if no data is returned
        if not data:
            self.textbox.insert("end",
                                "No headlines found for this selection",
                                "headline")

        else:
            for idx, itm in enumerate(data):
                sent = itm.get("Sentiment", "Neutral") # get sent, return neutral as default if none

                self.textbox.insert("end", f"{sent.upper()}\n", sent.lower())
                self.textbox.insert("end", f'{itm.get("Headline", "")}\n')

                # not at end
                if idx < len(data) - 1:
                    self.textbox.insert("end", "--------------------------------\n\n", "divider")

        '''
        for d in data:


            # write sentiment label
            if d['Sentiment'] == 'Positive':

                self.textbox.insert(
                    tk.END,
                    '[Positive]',
                    'positive'
                )

            elif d['Sentiment'] == 'Negative':

                self.textbox.insert(
                    tk.END,
                    '[Negative]',
                    'negative'
                )

            else:

                self.textbox.insert(
                    tk.END,
                    '[Neutral]'
                )

            # write headline text
            self.textbox.insert(
                tk.END,
                f'{d['Headline']}\n\n'
            )
        '''
        self.textbox.config(state='disabled')
        self.textbox.yview_moveto(0) # reset scrollbar position

        # Schedule a redraw after the current event finishes
        self.textbox.after_idle(self.refresh_textbox)

    def refresh_textbox(self):
        if not self.textbox.winfo_exists():
            return

        self.textbox.update_idletasks()

        # Temporarily adjust the widget's dimensions
        # to trigger a layout/redraw.
        width = self.textbox.cget("width")

        self.textbox.configure(width=width + 1)
        self.textbox.update_idletasks()
        self.textbox.configure(width=width)

if __name__ == "__main__":

    root = tk.Tk()
    app = Application(root)
    root.mainloop()