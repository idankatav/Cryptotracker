import tkinter as tk
from tkinter import ttk, StringVar, Listbox, Entry, Canvas
import requests
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from datetime import datetime, timezone
from difflib import get_close_matches

# Create Tkinter window
root = tk.Tk()
root.title("Crypto Price Tracker")
root.geometry("1100x950")  # Adjusted for better layout
root.configure(bg="#1E1E1E")

# Global variable to store last fetched crypto
displayed_crypto = ""

# Function to fetch available crypto names from CoinGecko API
def get_supported_cryptos():
    url = "https://api.coingecko.com/api/v3/coins/list"
    response = requests.get(url)
    if response.status_code == 200:
        coins = response.json()
        return [coin['id'] for coin in coins]  # Get only coin IDs
    return []

# Fetch list of available cryptocurrencies
crypto_list = get_supported_cryptos()

def plot_price_chart(crypto, days=7):
    try:
        url = f"https://api.coingecko.com/api/v3/coins/{crypto}/market_chart?vs_currency={currency_var.get()}&days={days}"
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            timestamps = [datetime.fromtimestamp(point[0] / 1000, timezone.utc) for point in data["prices"]]
            prices = [point[1] for point in data["prices"]]
            
            fig, ax = plt.subplots(figsize=(10, 5))
            ax.plot(timestamps, prices, label=f"{crypto.capitalize()} Price", marker="o", linestyle="-", linewidth=2)
            ax.set_xlabel("Date", fontsize=12)
            ax.set_ylabel(f"Price ({currency_var.get().upper()})", fontsize=12)
            ax.set_title(f"{crypto.capitalize()} {days}-Day Price Chart", fontsize=14, fontweight="bold")
            ax.grid(True, linestyle="--", alpha=0.6)
            ax.xaxis.set_major_formatter(mdates.DateFormatter("%b %d"))
            ax.xaxis.set_major_locator(mdates.DayLocator(interval=max(1, days//7)))
            plt.xticks(rotation=45)
            ax.legend()
            
            for widget in chart_frame.winfo_children():
                widget.destroy()
            
            canvas = FigureCanvasTkAgg(fig, master=chart_frame)
            canvas.draw()
            canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        else:
            print(response.status_code)
    except Exception as e:
        print(f"Error plotting graph for {crypto}: {e}")


# UI Variables
search_var = StringVar()
currency_var = StringVar()
currency_var.set("usd")  # Default currency
time_range_var = StringVar()
time_range_var.set("7")

def update_suggestions(event):
    typed = search_var.get().lower()
    if not typed:
        suggestion_box.delete(0, tk.END)
        return
    matches = get_close_matches(typed, crypto_list, n=10, cutoff=0.4)
    suggestion_box.delete(0, tk.END)
    for match in matches:
        suggestion_box.insert(tk.END, match)

def select_suggestion(event):
    selected_crypto = suggestion_box.get(tk.ACTIVE)
    if selected_crypto:
        search_var.set(selected_crypto)
        suggestion_box.delete(0, tk.END)
        get_crypto_info()

def get_crypto_info():
    global displayed_crypto
    crypto = search_var.get().lower()
    if not crypto or crypto == displayed_crypto:
        return  # Prevent unnecessary API requests
    
    closest_match = get_close_matches(crypto, crypto_list, n=1, cutoff=0.6)

    if not closest_match:  # If no match is found, prevent crashing
        details_label.config(text="Invalid cryptocurrency. Please select from the list.")
        suggestion_box.delete(0, tk.END)  # Clear suggestions
        return

    crypto = closest_match[0]
    search_var.set(crypto)
    
    url = f"https://api.coingecko.com/api/v3/coins/{crypto}"
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raises an HTTPError for bad responses (4xx, 5xx)
    except requests.exceptions.RequestException as e:
        details_label.config(text=f"API Error: {e}\nPlease try again.")
        return
    
    data = response.json()
    if response.status_code == 200:
        displayed_crypto = crypto  # Store last fetched crypto
    else:
        details_label.config(text="Failed to fetch details. Try again.")
        return  # Exit early to prevent program issues
    
    name = data.get("name", "Unknown")
    symbol = data.get("symbol", "N/A").upper()
    market_cap = data.get("market_data", {}).get("market_cap", {}).get(currency_var.get(), "N/A")
    volume = data.get("market_data", {}).get("total_volume", {}).get(currency_var.get(), "N/A")
    high_24h = data.get("market_data", {}).get("high_24h", {}).get(currency_var.get(), "N/A")
    low_24h = data.get("market_data", {}).get("low_24h", {}).get(currency_var.get(), "N/A")
    ath = data.get("market_data", {}).get("ath", {}).get(currency_var.get(), "N/A")
    atl = data.get("market_data", {}).get("atl", {}).get(currency_var.get(), "N/A")
    price_change_24h = data.get("market_data", {}).get("price_change_percentage_24h", "N/A")
    price_change_7d = data.get("market_data", {}).get("price_change_percentage_7d", "N/A")
    last_updated = data.get("last_updated", "N/A")
        
    details_label.config(text=(
        f"\nName: {name}\n"
        f"Symbol: {symbol}\n"
        f"Market Cap: {market_cap} {currency_var.get().upper()}\n"
        f"24H High: {high_24h} {currency_var.get().upper()}\n"
        f"24H Low: {low_24h} {currency_var.get().upper()}\n"
        f"All-Time High: {ath} {currency_var.get().upper()}\n"
        f"All-Time Low: {atl} {currency_var.get().upper()}\n"
        f"Price Change (24H): {price_change_24h:.2f}%\n"
        f"Price Change (7D): {price_change_7d:.2f}%\n"
        f"Volume: {volume} {currency_var.get().upper()}\n"
        f"Last Updated: {last_updated}"
    ))
    plot_price_chart(crypto, int(time_range_var.get()))


# UI Elements
search_entry = ttk.Entry(root, textvariable=search_var, font=("Arial", 14), width=35)
search_entry.pack(pady=5)
search_entry.bind("<KeyRelease>", update_suggestions)
search_entry.bind("<Return>", lambda event: get_crypto_info())

fetch_button = ttk.Button(root, text="Get Details", command=get_crypto_info)
fetch_button.pack(pady=10)

currency_dropdown = ttk.Combobox(root, textvariable=currency_var, values=["usd", "eur", "gbp", "btc", "eth", "ils"], font=("Arial", 12), width=12)
currency_dropdown.pack(pady=5)

suggestion_box = Listbox(root, font=("Arial", 12), background="#2E2E2E", foreground="white", height=5)
suggestion_box.pack(pady=5)
suggestion_box.bind("<Double-Button-1>", select_suggestion)

details_label = ttk.Label(root, text="", font=("Arial", 12), background="#1E1E1E", foreground="white", justify=tk.LEFT)
details_label.pack(pady=10)

chart_frame = tk.Frame(root, bg="#1E1E1E")
chart_frame.pack(pady=15, padx=20, fill=tk.BOTH, expand=True)

# Run Tkinter event loop
root.mainloop()
