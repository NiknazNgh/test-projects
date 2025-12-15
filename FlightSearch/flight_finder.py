import requests
from datetime import datetime, timedelta

# --- Configuration ---
# NOTE: To make this code run and return real data, you must replace the
# following placeholders with a real API endpoint and your API key from
# a flight data provider (e.g., Amadeus, Skyscanner, FlightAware, etc.).
# These services typically require registration and a subscription.

API_ENDPOINT = "https://api.example-flight-service.com/search" # Placeholder URL
API_KEY = "YOUR_SECRET_API_KEY_HERE" # Placeholder Key

# --- Search Parameters ---
ORIGIN = "DFW"  # Dallas/Fort Worth
DESTINATION = "SJC" # San Jose, CA
DEPART_DATE = "2026-01-16"
RETURN_DATE = "2026-01-19"

# Constraints
MIN_DEPART_HOUR = 14 # 2 PM (14:00)
MAX_DURATION_HOURS = 8
MAX_FLIGHTS_TO_RETURN = 5

def format_time(timestamp):
    """Converts a timestamp string to a readable HH:MM format."""
    try:
        # Assuming timestamp is in ISO format like '2026-01-16T15:30:00'
        dt_obj = datetime.fromisoformat(timestamp)
        return dt_obj.strftime("%H:%M")
    except ValueError:
        return "N/A"

def format_duration(seconds):
    """Converts duration in seconds to Hh Mm format."""
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    return f"{hours}h {minutes}m"

def is_valid_flight(flight_segment, direction):
    """
    Checks if a single flight segment meets the user's constraints.
    Constraints: Departure after 2 PM (for outbound) and duration less than 8 hours (for both).
    """
    try:
        # Extract departure time and hour
        depart_time_str = flight_segment['departureTime']
        depart_dt = datetime.fromisoformat(depart_time_str)
        depart_hour = depart_dt.hour

        # Extract duration (assuming it's provided in seconds in the API response)
        duration_seconds = flight_segment['durationSeconds']
        duration_hours = duration_seconds / 3600

        # Check all constraints
        time_ok = True
        # Only apply the 2 PM rule to the initial DFW -> SJC flight (outbound)
        if direction == 'outbound' and depart_hour < MIN_DEPART_HOUR:
            time_ok = False

        duration_ok = duration_hours < MAX_DURATION_HOURS

        return time_ok and duration_ok

    except KeyError as e:
        print(f"Warning: Missing key in flight data: {e}")
        return False
    except ValueError:
        print("Warning: Invalid date/time format in flight data.")
        return False

def search_and_filter_flights():
    """
    Simulates calling an API, filtering results, and returning the top 5 cheapest.
    """
    print(f"--- Searching Flights: {ORIGIN} to {DESTINATION} and back ---")
    print(f"Dates: {DEPART_DATE} (after {MIN_DEPART_HOUR}:00) to {RETURN_DATE} (duration < {MAX_DURATION_HOURS}h)")

    # 1. API Call Simulation (Placeholder)
    try:
        # --- Mock Data for demonstration ---
        # This mock data structure mimics a common API response.
        raw_results = [
            # Cheap, but fails the DFW -> SJC 2 PM rule (departs at 10:00)
            {'id': 1, 'price': 350.00, 'outbound': {'departureTime': '2026-01-16T10:00:00', 'durationSeconds': 21600}, 'inbound': {'departureTime': '2026-01-19T08:00:00', 'durationSeconds': 18000}},
            # Passes all rules, duration < 8h
            {'id': 2, 'price': 420.50, 'outbound': {'departureTime': '2026-01-16T16:30:00', 'durationSeconds': 25200}, 'inbound': {'departureTime': '2026-01-19T10:00:00', 'durationSeconds': 23400}},
            # Cheap, but fails the duration rule (10 hours)
            {'id': 3, 'price': 399.00, 'outbound': {'departureTime': '2026-01-16T15:00:00', 'durationSeconds': 36000}, 'inbound': {'departureTime': '2026-01-19T18:00:00', 'durationSeconds': 14400}},
            # Passes all rules (Rank #1)
            {'id': 4, 'price': 415.75, 'outbound': {'departureTime': '2026-01-16T18:15:00', 'durationSeconds': 24000}, 'inbound': {'departureTime': '2026-01-19T12:00:00', 'durationSeconds': 26000}},
            # Passes all rules (Rank #5)
            {'id': 5, 'price': 450.00, 'outbound': {'departureTime': '2026-01-16T14:05:00', 'durationSeconds': 18000}, 'inbound': {'departureTime': '2026-01-19T15:00:00', 'durationSeconds': 20000}},
            # Passes all rules (Rank #2)
            {'id': 6, 'price': 418.00, 'outbound': {'departureTime': '2026-01-16T19:00:00', 'durationSeconds': 20000}, 'inbound': {'departureTime': '2026-01-19T16:00:00', 'durationSeconds': 19000}},
            # Passes all rules (Rank #4)
            {'id': 7, 'price': 430.00, 'outbound': {'departureTime': '2026-01-16T15:00:00', 'durationSeconds': 22000}, 'inbound': {'departureTime': '2026-01-19T09:00:00', 'durationSeconds': 21000}},
            # Fails 2 PM rule
            {'id': 8, 'price': 405.00, 'outbound': {'departureTime': '2026-01-16T12:00:00', 'durationSeconds': 24000}, 'inbound': {'departureTime': '2026-01-19T11:00:00', 'durationSeconds': 24000}},
        ]
        print(f"Mock Data: Found {len(raw_results)} potential itineraries.")
        # --- End Mock Data ---

    except requests.exceptions.RequestException as e:
        print(f"Error connecting to flight API: {e}")
        return []

    # 2. Filter the Results
    filtered_itineraries = []
    for itinerary in raw_results:
        # Check if BOTH the outbound and inbound flights meet the criteria
        outbound_ok = is_valid_flight(itinerary['outbound'], 'outbound')
        inbound_ok = is_valid_flight(itinerary['inbound'], 'inbound')

        if outbound_ok and inbound_ok:
            # All constraints met, add to the filtered list
            filtered_itineraries.append(itinerary)

    print(f"Filtered Results: {len(filtered_itineraries)} itineraries meet all criteria.")

    # 3. Sort by Price (Cheapest first)
    sorted_itineraries = sorted(filtered_itineraries, key=lambda x: x['price'])

    # 4. Select the Top 5
    top_5_itineraries = sorted_itineraries[:MAX_FLIGHTS_TO_RETURN]

    return top_5_itineraries

def display_results(itineraries):
    """
    Prints the final, formatted list of the top itineraries.
    """
    if not itineraries:
        print("\nNo flights matching all criteria were found.")
        return

    print("\n=======================================================")
    print(f"   Top {len(itineraries)} Cheapest Valid Flight Itineraries")
    print("=======================================================")

    for i, flight in enumerate(itineraries):
        outbound = flight['outbound']
        inbound = flight['inbound']

        # Format details
        out_time = format_time(outbound['departureTime'])
        out_duration = format_duration(outbound['durationSeconds'])
        in_time = format_time(inbound['departureTime'])
        in_duration = format_duration(inbound['durationSeconds'])

        print(f"\nRANK #{i + 1} | TOTAL PRICE: ${flight['price']:.2f}")
        print("-------------------------------------------------------")

        # Outbound Details (DFW -> SJC)
        print(f"  > Outbound ({DEPART_DATE}): {ORIGIN} -> {DESTINATION}")
        print(f"    - Departs: {out_time} (Passes > {MIN_DEPART_HOUR}:00 Check)")
        print(f"    - Duration: {out_duration} (Passes < {MAX_DURATION_HOURS}h Check)")

        # Inbound Details (SJC -> DFW)
        print(f"  > Inbound ({RETURN_DATE}): {DESTINATION} -> {ORIGIN}")
        print(f"    - Departs: {in_time}")
        print(f"    - Duration: {in_duration} (Passes < {MAX_DURATION_HOURS}h Check)")

if __name__ == "__main__":
    results = search_and_filter_flights()
    display_results(results)
    print("\n--- Script Execution Complete ---")
    print("Remember to integrate a real flight API to get live data.")