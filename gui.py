import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import threading
import time
from utils import spin_text
from automation import post_review

class ReviewBotApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Google Review Bot")
        self.root.geometry("1200x800")
        self.root.configure(bg="#2c3e50")
        self.scheduled_reviews = []
        self.accounts = []
        self.proxies = []
        self.current_account_index = 0
        self.current_proxy_index = 0
        self.is_posting = False
        self._create_widgets()

    def _create_widgets(self):
        main_frame = ttk.Frame(self.root, padding="20", style="TFrame")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Style configuration
        self.style = ttk.Style()
        self.style.theme_use("clam")
        self.style.configure("TFrame", background="#2c3e50")
        self.style.configure("TLabel", background="#2c3e50", foreground="#ecf0f1", font=("Helvetica", 12))
        self.style.configure("TEntry", fieldbackground="#34495e", foreground="#ecf0f1", borderwidth=0)
        self.style.configure("TButton", background="#3498db", foreground="#ffffff", font=("Helvetica", 12, "bold"), borderwidth=0)
        self.style.map("TButton", background=[("active", "#2980b9")])
        self.style.configure("Treeview", background="#34495e", foreground="#ecf0f1", fieldbackground="#34495e", rowheight=25)
        self.style.map("Treeview", background=[("selected", "#3498db")])
        self.style.configure("Treeview.Heading", background="#3498db", foreground="#ffffff", font=("Helvetica", 12, "bold"))
        self.style.configure("TSpinbox", fieldbackground="#34495e", foreground="#ecf0f1", borderwidth=0)

        # --- Top Frame for Inputs and Management ---
        top_frame = ttk.Frame(main_frame)
        top_frame.pack(fill=tk.X, pady=10, expand=False)

        # --- Input Section ---
        input_frame = ttk.LabelFrame(top_frame, text="Create a Review", padding="15", style="TFrame")
        input_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)

        ttk.Label(input_frame, text="Business URL:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.business_url_entry = ttk.Entry(input_frame, width=40)
        self.business_url_entry.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        self.business_url_entry.insert(0, "Enter Google Maps URL here")
        self.business_url_entry.bind("<FocusIn>", self._clear_placeholder)

        ttk.Label(input_frame, text="Star Rating:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.star_rating = tk.IntVar(value=5)
        star_frame = ttk.Frame(input_frame)
        star_frame.grid(row=1, column=1, padx=5, pady=5, sticky="w")
        for i in range(1, 6):
            ttk.Radiobutton(star_frame, text=f"{i} ★", variable=self.star_rating, value=i).pack(side=tk.LEFT)

        ttk.Label(input_frame, text="Review Text:").grid(row=2, column=0, padx=5, pady=5, sticky="nw")
        self.review_text = tk.Text(input_frame, height=5, width=50, bg="#34495e", fg="#ecf0f1", insertbackground="#ecf0f1", relief="flat")
        self.review_text.grid(row=2, column=1, padx=5, pady=5, sticky="ew")

        action_frame = ttk.Frame(input_frame)
        action_frame.grid(row=3, column=1, pady=10, sticky="e")
        self.spin_button = ttk.Button(action_frame, text="Spin Content", command=self.spin_content)
        self.spin_button.pack(side=tk.LEFT, padx=5)
        self.schedule_button = ttk.Button(action_frame, text="Schedule Review", command=self.schedule_review)
        self.schedule_button.pack(side=tk.LEFT)

        # --- Management Sections Frame ---
        management_frame = ttk.Frame(top_frame)
        management_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(20, 0))

        account_frame = ttk.LabelFrame(management_frame, text="Account Management", padding="15", style="TFrame")
        account_frame.pack(fill=tk.Y)
        load_accounts_button = ttk.Button(account_frame, text="Load Accounts", command=self.load_accounts)
        load_accounts_button.pack(pady=5, fill=tk.X)
        self.account_tree = ttk.Treeview(account_frame, columns=("Username", "Status"), show="headings", height=5)
        self.account_tree.heading("Username", text="Username")
        self.account_tree.heading("Status", text="Status")
        self.account_tree.column("Username", width=150)
        self.account_tree.column("Status", width=80, anchor="center")
        self.account_tree.pack(fill=tk.BOTH, expand=True)

        proxy_frame = ttk.LabelFrame(management_frame, text="Proxy Management", padding="15", style="TFrame")
        proxy_frame.pack(fill=tk.Y, pady=(10,0))
        load_proxies_button = ttk.Button(proxy_frame, text="Load Proxies", command=self.load_proxies)
        load_proxies_button.pack(pady=5, fill=tk.X)
        self.proxy_tree = ttk.Treeview(proxy_frame, columns=("Proxy", "Status"), show="headings", height=5)
        self.proxy_tree.heading("Proxy", text="Proxy (IP:Port)")
        self.proxy_tree.heading("Status", text="Status")
        self.proxy_tree.column("Proxy", width=150)
        self.proxy_tree.column("Status", width=80, anchor="center")
        self.proxy_tree.pack(fill=tk.BOTH, expand=True)

        # --- Scheduled Reviews Section ---
        schedule_frame = ttk.LabelFrame(main_frame, text="Scheduled Reviews", padding="15", style="TFrame")
        schedule_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        self.tree = ttk.Treeview(schedule_frame, columns=("URL", "Rating", "Account", "Proxy", "Review", "Status"), show="headings")
        self.tree.heading("URL", text="Business URL")
        self.tree.heading("Rating", text="Rating")
        self.tree.heading("Account", text="Account")
        self.tree.heading("Proxy", text="Proxy")
        self.tree.heading("Review", text="Review")
        self.tree.heading("Status", text="Status")
        self.tree.column("URL", width=150)
        self.tree.column("Rating", width=60, anchor="center")
        self.tree.column("Account", width=120)
        self.tree.column("Proxy", width=120)
        self.tree.column("Review", width=300)
        self.tree.column("Status", width=100, anchor="center")
        self.tree.pack(fill=tk.BOTH, expand=True)

        # --- Control Section ---
        control_frame = ttk.Frame(main_frame)
        control_frame.pack(fill=tk.X, pady=10)
        self.start_button = ttk.Button(control_frame, text="Start Posting", command=self.start_posting)
        self.start_button.pack(side=tk.LEFT, padx=5)
        self.stop_button = ttk.Button(control_frame, text="Stop Posting", command=self.stop_posting, state=tk.DISABLED)
        self.stop_button.pack(side=tk.LEFT)
        pause_frame = ttk.LabelFrame(control_frame, text="Pause Settings", padding="10", style="TFrame")
        pause_frame.pack(side=tk.LEFT, padx=20)
        ttk.Label(pause_frame, text="Pause after").pack(side=tk.LEFT, padx=5)
        self.reviews_before_pause = tk.IntVar(value=5)
        ttk.Spinbox(pause_frame, from_=1, to=100, textvariable=self.reviews_before_pause, width=5).pack(side=tk.LEFT)
        ttk.Label(pause_frame, text="reviews for").pack(side=tk.LEFT, padx=5)
        self.pause_duration = tk.StringVar(value="30 Minutes")
        ttk.Combobox(pause_frame, textvariable=self.pause_duration, values=["15 Minutes", "30 Minutes", "1 Hour", "2 Hours"], width=12).pack(side=tk.LEFT)
        self.status_label = ttk.Label(control_frame, text="Status: Idle", font=("Helvetica", 10))
        self.status_label.pack(side=tk.RIGHT, padx=10)

    def _clear_placeholder(self, event):
        if self.business_url_entry.get() == "Enter Google Maps URL here":
            self.business_url_entry.delete(0, tk.END)

    def load_accounts(self):
        filepath = filedialog.askopenfilename(filetypes=(("Text Files", "*.txt"), ("All files", "*.*")))
        if not filepath:
            return
        try:
            with open(filepath, 'r') as f:
                self.accounts = [{"username": u.strip(), "password": p.strip(), "status": "Ready"} 
                                 for u, p in (line.split(',', 1) for line in f if ',' in line)]
            self.update_account_list()
            messagebox.showinfo("Success", f"Successfully loaded {len(self.accounts)} accounts.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load accounts file: {e}")

    def load_proxies(self):
        filepath = filedialog.askopenfilename(filetypes=(("Text Files", "*.txt"), ("All files", "*.*")))
        if not filepath:
            return
        try:
            with open(filepath, 'r') as f:
                self.proxies = [{"proxy": line.strip(), "status": "Ready"} for line in f if line.strip()]
            self.update_proxy_list()
            messagebox.showinfo("Success", f"Successfully loaded {len(self.proxies)} proxies.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load proxies file: {e}")

    def update_account_list(self):
        self.account_tree.delete(*self.account_tree.get_children())
        for acc in self.accounts:
            self.account_tree.insert("", "end", values=(acc["username"], acc.get("status", "Ready")))

    def update_proxy_list(self):
        self.proxy_tree.delete(*self.proxy_tree.get_children())
        for proxy in self.proxies:
            self.proxy_tree.insert("", "end", values=(proxy["proxy"], proxy.get("status", "Ready")))

    def spin_content(self):
        text = self.review_text.get("1.0", tk.END).strip()
        if not text:
            messagebox.showwarning("Warning", "Review text is empty.")
            return
        spun = spin_text(text)
        self.review_text.delete("1.0", tk.END)
        self.review_text.insert("1.0", spun)

    def schedule_review(self):
        if not self.accounts:
            messagebox.showerror("Error", "No accounts loaded.")
            return
        if not self.proxies:
            messagebox.showerror("Error", "No proxies loaded.")
            return

        business_url = self.business_url_entry.get()
        review_text = self.review_text.get("1.0", tk.END).strip()
        if not business_url or not review_text or "Enter Google Maps URL" in business_url:
            messagebox.showerror("Error", "Business URL and review text cannot be empty.")
            return

        account_details = self.accounts[self.current_account_index % len(self.accounts)]
        self.current_account_index += 1
        proxy_details = self.proxies[self.current_proxy_index % len(self.proxies)]
        self.current_proxy_index += 1

        review_data = {
            "url": business_url, "rating": self.star_rating.get(), "review_text": review_text,
            "account": account_details, "proxy": proxy_details['proxy'], "status": "Pending"
        }
        self.scheduled_reviews.append(review_data)
        self.update_review_list()
        self.review_text.delete("1.0", tk.END)

    def update_review_list(self):
        self.tree.delete(*self.tree.get_children())
        for i, review in enumerate(self.scheduled_reviews):
            self.tree.insert("", "end", iid=i, values=(
                review["url"], f"{review['rating']} ★", review["account"]["username"],
                review["proxy"], review["review_text"], review["status"]
            ))

    def start_posting(self):
        if not self.scheduled_reviews:
            messagebox.showinfo("Info", "No reviews to post.")
            return
        if self.is_posting:
            messagebox.showwarning("Warning", "Posting process is already running.")
            return

        self.is_posting = True
        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        self.status_label.config(text="Status: Running...")
        self.posting_thread = threading.Thread(target=self._posting_process, daemon=True)
        self.posting_thread.start()

    def stop_posting(self):
        if not self.is_posting:
            return
        self.is_posting = False
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        self.status_label.config(text="Status: Stopped")

    def _update_status(self, index, status_text):
        self.root.after(0, self.tree.set, index, column="Status", value=status_text)

    def _update_status_label(self, text):
        self.root.after(0, self.status_label.config, {"text": text})

    def _posting_process(self):
        reviews_posted_since_pause = 0
        try:
            num_to_pause = self.reviews_before_pause.get()
            duration_str = self.pause_duration.get()
            duration_map = {"15 Minutes": 15*60, "30 Minutes": 30*60, "1 Hour": 60*60, "2 Hours": 120*60}
            pause_seconds = duration_map.get(duration_str, 1800)
        except (tk.TclError, ValueError):
            num_to_pause, pause_seconds = 5, 1800

        for i, review_data in enumerate(self.scheduled_reviews):
            if not self.is_posting:
                break
            if review_data["status"] != "Pending":
                continue

            def status_callback(msg):
                self._update_status(i, msg)

            self._update_status(i, "Starting...")
            success = post_review(
                review_data["account"], review_data["proxy"], review_data, status_callback
            )
            if success:
                self._update_status(i, "Posted")
            else:
                self._update_status(i, "Failed")
            reviews_posted_since_pause += 1

            # --- Handle Pauses ---
            if reviews_posted_since_pause >= num_to_pause:
                reviews_posted_since_pause = 0
                for t in range(pause_seconds, 0, -1):
                    if not self.is_posting:
                        break
                    mins, secs = divmod(t, 60)
                    self._update_status_label(f"Status: Paused ({mins:02d}:{secs:02d})")
                    time.sleep(1)
                if not self.is_posting:
                    break
                self._update_status_label("Status: Running...")

            # Wait before next review
            time.sleep(random.uniform(10, 30))

        if self.is_posting:
            self.root.after(0, self.stop_posting)
            self.root.after(0, lambda: self._update_status_label("Status: Finished"))

def show_ethics_warning():
    warning = (
        "WARNING: Automating Google reviews may violate Google's Terms of Service "
        "and is potentially illegal and unethical. Use this software responsibly. "
        "The author is not responsible for misuse."
    )
    root = tk.Tk()
    root.withdraw()  # Hide main window
    proceed = messagebox.askokcancel("Ethics & Legal Warning", warning)
    root.destroy()
    return proceed

if __name__ == "__main__":
    if show_ethics_warning():
        root = tk.Tk()
        app = ReviewBotApp(root)
        root.mainloop()