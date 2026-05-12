import json
import os
import smtplib
from email.mime.text import MIMEText
from datetime import datetime
from bs4 import BeautifulSoup
import requests

PRICES_FILE = "prices.json"

URLS = [
    "https://www.superfietsen.nl/elektrische-fiets/",
]

def scrape_prices():
    prices = {}
    headers = {"User-Agent": "Mozilla/5.0"}
    for url in URLS:
        r = requests.get(url, headers=headers, timeout=15)
        soup = BeautifulSoup(r.text, "html.parser")
        for product in soup.select(".product-list-item"):
            name_el = product.select_one(".product-title")
            price_el = product.select_one(".price")
            if name_el and price_el:
                name = name_el.get_text(strip=True)
                price = price_el.get_text(strip=True)
                prices[name] = price
    return prices

def load_old_prices():
    if os.path.exists(PRICES_FILE):
        with open(PRICES_FILE) as f:
            return json.load(f)
    return {}

def save_prices(prices):
    with open(PRICES_FILE, "w") as f:
        json.dump(prices, f, indent=2, ensure_ascii=False)

def send_email(changes):
    sender = os.environ["EMAIL_SENDER"]
    recipient = os.environ["EMAIL_RECIPIENT"]
    password = os.environ["EMAIL_PASSWORD"]
    lines = [f"Prijswijzigingen op superfietsen.nl — {datetime.now().strftime('%d-%m-%Y')}\n"]
    for name, (old, new) in changes.items():
        lines.append(f"• {name}")
        lines.append(f"  Was: {old}")
        lines.append(f"  Nu:  {new}\n")
    msg = MIMEText("\n".join(lines))
    msg["Subject"] = f"🚲 {len(changes)} prijswijziging(en) op superfietsen.nl"
    msg["From"] = sender
    msg["To"] = recipient
    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
        smtp.login(sender, password)
        smtp.send_message(msg)
    print(f"E-mail verstuurd: {len(changes)} wijziging(en)")

def main():
    print("Prijzen ophalen...")
    new_prices = scrape_prices()
    old_prices = load_old_prices()
    changes = {}
    for name, new_price in new_prices.items():
        old_price = old_prices.get(name)
        if old_price and old_price != new_price:
            changes[name] = (old_price, new_price)
    for name in new_prices:
        if name not in old_prices:
            changes[name] = ("(nieuw)", new_prices[name])
    print(f"{len(new_prices)} producten gevonden, {len(changes)} wijziging(en)")
    if changes:
        send_email(changes)
    else:
        print("Geen wijzigingen")
    save_prices(new_prices)

if __name__ == "__main__":
    main()
