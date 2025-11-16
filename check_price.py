import tkinter as tk
from tkinter import scrolledtext
import requests
import csv
import os
from nsetools import Nse

CSV_URL = "https://nsearchives.nseindia.com/content/equities/EQUITY_L.csv"
CSV_FILE = "EQUITY_L.csv"

def download_csv(url, filename):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/csv,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Referer": "https://www.nseindia.com/",
        "Connection": "keep-alive",
    }
    resp = requests.get(url, headers=headers)
    resp.raise_for_status()  # Raise an error if download fails
    with open(filename, "wb") as f:
        f.write(resp.content)

def load_company_mapping(csv_file):
    company_mapping = {}
    with open(csv_file, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            symbol = row['SYMBOL'].strip()
            company_name = row['NAME OF COMPANY'].strip()
            company_mapping[symbol] = company_name
    return company_mapping

def find_matching_scrips(company_input, company_mapping):
    matches = {symbol: name for symbol, name in company_mapping.items()
               if company_input.lower() in name.lower()}
    return matches

def get_stock_data(symbol, nse, company_mapping):
    try:
        quote = nse.get_quote(symbol)
        last_traded_price = quote.get('lastPrice', 'N/A')
        day_high = quote.get('dayHigh', 'N/A')
        day_low = quote.get('dayLow', 'N/A')
        company_name = company_mapping.get(symbol, symbol)  # Always use the CSV mapping!
        return (company_name, symbol, last_traded_price, day_high, day_low)
    except Exception as e:
        return (company_mapping.get(symbol, symbol), symbol, 'N/A', 'N/A', 'N/A')

def search_company():
    company_input = entry.get().strip()
    results_area.delete('1.0', tk.END)
    matches = find_matching_scrips(company_input, company_mapping)
    if not matches:
        results_area.insert(tk.END, "No matching company found.\n")
    else:
        results_area.insert(tk.END, f"Found {len(matches)} matching companies:\n\n")
        for symbol, company_name in matches.items():
            data = get_stock_data(symbol, nse, company_mapping)
            results_area.insert(tk.END, 
                f"Scrip: {data[1]}\n"
                f"Company Name: {data[0]}\n"
                f"Last Traded Price: {data[2]}\n"
                f"Day's High: {data[3]}\n"
                f"Day's Low: {data[4]}\n"
                + "-"*30 + "\n"
            )

# Main program
download_csv(CSV_URL, CSV_FILE)
company_mapping = load_company_mapping(CSV_FILE)
nse = Nse()

root = tk.Tk()
root.title("NSE Stock Lookup")

tk.Label(root, text="Enter company name:").pack()
entry = tk.Entry(root, width=50)
entry.pack()
tk.Button(root, text="Search", command=search_company).pack()
results_area = scrolledtext.ScrolledText(root, width=80, height=20)
results_area.pack()

root.mainloop()
