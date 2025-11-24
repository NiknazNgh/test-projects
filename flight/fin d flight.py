from playwright.sync_api import sync_playwright
import re

def parse_duration(text):
    """Convert '3 hr 45 min' into minutes"""
    hours = re.search(r"(\d+)\s*hr", text)
    mins = re.search(r"(\d+)\s*min", text)
    total = 0
    if hours:
        total += int(hours.group(1)) * 60
    if mins:
        total += int(mins.group(1))
    return total

def check_flights():
    # UPDATED: DFW → SJC
    url = (
        "https://www.google.com/travel/flights?q="
        "Flights%20from%20DFW%20to%20SJC%20on%202026-01-16%20"
        "returning%202026-01-19"
    )

    print("Checking flights... please wait.")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(url, timeout=90000)

        page.wait_for_timeout(6000)  # Wait for results to load

        flights = page.query_selector_all("div[jscontroller='XZx4n']")
        deals = []

        for f in flights:
            try:
                dep_time = f.query_selector("div.gws-flights-results__times div:nth-child(1)").inner_text()
                arr_time = f.query_selector("div.gws-flights-results__times div:nth-child(2)").inner_text()
                duration_text = f.query_selector("div.gws-flights-results__duration").inner_text()
                price = f.query_selector("div.gws-flights-results__price").inner_text()

                dur_minutes = parse_duration(duration_text)

                # filter time > 2 PM
                match = re.match(r"(\d+):?(\d*)\s*(AM|PM)", dep_time)
                if not match:
                    continue

                hour = int(match.group(1))
                mins = match.group(2)
                mins = int(mins) if mins else 0
                ampm = match.group(3)

                if ampm == "PM" and hour < 12:
                    hour += 12

                if hour < 14:  # 2 PM cutoff
                    continue

                if dur_minutes > 480:  # 8 hours
                    continue

                deals.append({
                    "depart": dep_time,
                    "arrive": arr_time,
                    "duration": duration_text,
                    "price": price
                })

            except:
                continue

        browser.close()

    # sort by price
    def price_to_num(text):
        return int(re.sub(r"[^0-9]", "", text))

    deals = sorted(deals, key=lambda x: price_to_num(x["price"]))

    print("\nTop 5 cheapest options for DFW → SJC:\n")
    for i, d in enumerate(deals[:5], start=1):
        print(f"{i}) {d['price']} — {d['depart']} → {d['arrive']}  ({d['duration']})")

    if not deals:
        print("No flights matched your filters today.")

if __name__ == "__main__":
    check_flights()
