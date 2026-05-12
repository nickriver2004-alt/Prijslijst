name: Prijsmonitor superfietsen.nl

on:
  schedule:
    - cron: "0 8 * * *"
  workflow_dispatch:

jobs:
  check-prices:
    runs-on: ubuntu-latest

    steps:
      - name: Code ophalen
        uses: actions/checkout@v4

      - name: Opgeslagen prijzen ophalen
        uses: actions/cache@v4
        with:
          path: prices.json
          key: prices-cache-${{ github.run_id }}
          restore-keys: prices-cache-

      - name: Python installen
        uses: actions/setup-python@v5
        with:
          python-version: "3.12"

      - name: Dependencies installeren
        run: pip install requests beautifulsoup4

      - name: Prijzen checken
        env:
          EMAIL_SENDER: ${{ secrets.EMAIL_SENDER }}
          EMAIL_RECIPIENT: ${{ secrets.EMAIL_RECIPIENT }}
          EMAIL_PASSWORD: ${{ secrets.EMAIL_PASSWORD }}
        run: python scraper.py

      - name: Bijgewerkte prices.json opslaan
        uses: actions/cache/save@v4
        with:
          path: prices.json
          key: prices-cache-${{ github.run_id }}
