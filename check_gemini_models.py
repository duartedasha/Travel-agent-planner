import streamlit as st
import json
import os
from serpapi import GoogleSearch 
from agno.agent import Agent
from agno.tools.serpapi import SerpApiTools
from agno.models.google import Gemini
from datetime import datetime

# City Name to IATA Code Mapping Dictionary
CITY_TO_IATA = {
    # Major Cities
    "Mumbai": "BOM",
    "Delhi": "DEL",
    "Bangalore": "BLR",
    "Bengaluru": "BLR",
    "Kolkata": "CCU",
    "Chennai": "MAA",
    "Hyderabad": "HYD",
    "Pune": "PNQ",
    "Ahmedabad": "AMD",
    "Jaipur": "JAI",
    "Kochi": "COK",
    "Cochin": "COK",
    
    # Tourist Destinations
    "Goa": "GOI",
    "Leh": "IXL",
    "Srinagar": "SXR",
    "Shimla": "SLV",
    "Darjeeling": "IXB",
    "Bagdogra": "IXB",
    "Port Blair": "IXZ",
    "Andaman": "IXZ",
    "Udaipur": "UDR",
    "Coimbatore": "CJB",
    "Guwahati": "GAU",
    "Lucknow": "LKO",
    "Chandigarh": "IXC",
    "Varanasi": "VNS",
    "Banaras": "VNS",
    
    # Additional Cities
    "Amritsar": "ATQ",
    "Bhubaneswar": "BBI",
    "Indore": "IDR",
    "Mangalore": "IXE",
    "Nagpur": "NAG",
    "Patna": "PAT",
    "Ranchi": "IXR",
    "Trivandrum": "TRV",
    "Thiruvananthapuram": "TRV",
    "Vijayawada": "VGA",
    "Visakhapatnam": "VTZ",
    "Vizag": "VTZ",
    
    # International
    "Dubai": "DXB",
    "Singapore": "SIN",
    "Bangkok": "BKK",
    "Kathmandu": "KTM",
    "Colombo": "CMB",
    "London": "LHR",
    "New York": "JFK",
    "Paris": "CDG",
    "Tokyo": "NRT"
}

# Create reverse mapping for display
IATA_TO_CITY = {v: k for k, v in CITY_TO_IATA.items()}

# Function to get IATA code from city name
def get_iata_code(city_name):
    """Convert city name to IATA code. Case-insensitive."""
    city_name = city_name.strip().title()
    return CITY_TO_IATA.get(city_name, None)

# Function to validate and convert city input
def validate_city(city_name):
    """Validate city and return IATA code with user feedback."""
    iata = get_iata_code(city_name)
    if iata:
        return iata, True
    else:
        return None, False

# Set up Streamlit UI with a travel-friendly theme
st.set_page_config(page_title="🌍 AI Travel Planner", layout="wide")
st.markdown(
    """
    <style>
        .title {
            text-align: center;
            font-size: 36px;
            font-weight: bold;
            color: #ff5733;
        }
        .subtitle {
            text-align: center;
            font-size: 20px;
            color: #555;
        }
        .stSlider > div {
            background-color: #f9f9f9;
            padding: 10px;
            border-radius: 10px;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

# Title and subtitle
st.markdown('<h1 class="title">✈️ AI-Powered Travel Planner</h1>', unsafe_allow_html=True)
st.markdown('<p class="subtitle">Plan your dream trip with AI! Get personalized recommendations for flights, hotels, and activities.</p>', unsafe_allow_html=True)

# API Keys (Set your keys here)
SERPAPI_KEY = "67d2b79786fca1c3775324dd96b071d0feec19482b2c30a1e702a64dadb4f528"
GOOGLE_API_KEY = "AIzaSyCci5cFOaoMmBexIJp4k4yyrMw27CnWn5o"
os.environ["GOOGLE_API_KEY"] = GOOGLE_API_KEY

# User Inputs Section
st.markdown("### 🌍 Where are you headed?")

col1, col2 = st.columns(2)

with col1:
    source_city = st.text_input("🛫 Departure City:", "Mumbai", 
                                help="Enter city name (e.g., Mumbai, Delhi, Goa)")
    
with col2:
    destination_city = st.text_input("🛬 Destination City:", "Goa",
                                    help="Enter city name (e.g., Mumbai, Delhi, Goa)")

# Validate cities in real-time and show IATA codes
source_iata, source_valid = validate_city(source_city)
dest_iata, dest_valid = validate_city(destination_city)

if source_city:
    if source_valid:
        st.success(f"✅ {source_city} → Airport Code: {source_iata}")
    else:
        st.error(f"❌ '{source_city}' not found. Please enter a valid city name.")
        with st.expander("📋 See list of supported cities"):
            cities_list = sorted(list(set(CITY_TO_IATA.keys())))
            # Display in columns for better readability
            cols = st.columns(4)
            for idx, city in enumerate(cities_list):
                with cols[idx % 4]:
                    st.write(f"• {city}")

if destination_city:
    if dest_valid:
        st.success(f"✅ {destination_city} → Airport Code: {dest_iata}")
    else:
        st.error(f"❌ '{destination_city}' not found. Please enter a valid city name.")
        with st.expander("📋 See list of supported cities"):
            cities_list = sorted(list(set(CITY_TO_IATA.keys())))
            cols = st.columns(4)
            for idx, city in enumerate(cities_list):
                with cols[idx % 4]:
                    st.write(f"• {city}")

st.markdown("### 📅 Plan Your Adventure")
num_days = st.slider("🕒 Trip Duration (days):", 1, 14, 5)
travel_theme = st.selectbox(
    "🎭 Select Your Travel Theme:",
    ["💑 Couple Getaway", "👨‍👩‍👧‍👦 Family Vacation", "🏔️ Adventure Trip", "🧳 Solo Exploration"]
)

# Divider for aesthetics
st.markdown("---")

st.markdown(
    f"""
    <div style="
        text-align: center; 
        padding: 15px; 
        background-color: #ffecd1; 
        border-radius: 10px; 
        margin-top: 20px;
    ">
        <h3>🌟 Your {travel_theme} from {source_city} to {destination_city} is about to begin! 🌟</h3>
        <p>Let's find the best flights, stays, and experiences for your unforgettable journey.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

def format_datetime(iso_string):
    try:
        dt = datetime.strptime(iso_string, "%Y-%m-%d %H:%M")
        return dt.strftime("%b-%d, %Y | %I:%M %p")
    except:
        return "N/A"

activity_preferences = st.text_area(
    "🌍 What activities do you enjoy? (e.g., relaxing on the beach, exploring historical sites, nightlife, adventure)",
    "Relaxing on the beach, exploring historical sites"
)

departure_date = st.date_input("Departure Date")
return_date = st.date_input("Return Date")

# Sidebar Setup
st.sidebar.title("🌎 Travel Assistant")
st.sidebar.subheader("Personalize Your Trip")

# Travel Preferences
budget = st.sidebar.radio("💰 Budget Preference:", ["Economy", "Standard", "Luxury"])
flight_class = st.sidebar.radio("✈️ Flight Class:", ["Economy", "Business", "First Class"])
hotel_rating = st.sidebar.selectbox("🏨 Preferred Hotel Rating:", ["Any", "3⭐", "4⭐", "5⭐"])

# Packing Checklist
st.sidebar.subheader("🎒 Packing Checklist")
packing_list = {
    "👕 Clothes": True,
    "🩴 Comfortable Footwear": True,
    "🕶️ Sunglasses & Sunscreen": False,
    "📖 Travel Guidebook": False,
    "💊 Medications & First-Aid": True
}
for item, checked in packing_list.items():
    st.sidebar.checkbox(item, value=checked)

# Travel Essentials
st.sidebar.subheader("🛂 Travel Essentials")
visa_required = st.sidebar.checkbox("🛃 Check Visa Requirements")
travel_insurance = st.sidebar.checkbox("🛡️ Get Travel Insurance")
currency_converter = st.sidebar.checkbox("💱 Currency Exchange Rates")

# Quick city suggestions
st.sidebar.markdown("---")
st.sidebar.subheader("🔥 Popular Destinations")
st.sidebar.markdown("""
**Beaches:** Goa, Andaman, Kochi  
**Mountains:** Leh, Shimla, Srinagar  
**Culture:** Delhi, Jaipur, Varanasi  
**Metro Cities:** Mumbai, Bangalore, Hyderabad
""")

# Function to fetch flight data
def fetch_flights(source, destination, departure_date, return_date):
    params = {
        "engine": "google_flights",
        "departure_id": source,
        "arrival_id": destination,
        "outbound_date": str(departure_date),
        "return_date": str(return_date),
        "currency": "INR",
        "hl": "en",
        "api_key": SERPAPI_KEY
    }
    search = GoogleSearch(params)
    results = search.get_dict()
    return results

# Function to extract top 3 cheapest flights
def extract_cheapest_flights(flight_data):
    best_flights = flight_data.get("best_flights", [])
    sorted_flights = sorted(best_flights, key=lambda x: x.get("price", float("inf")))[:3]
    return sorted_flights

# AI Agents
researcher = Agent(
    name="Researcher",
    instructions=[
        "Identify the travel destination specified by the user.",
        "Gather detailed information on the destination, including climate, culture, and safety tips.",
        "Find popular attractions, landmarks, and must-visit places.",
        "Search for activities that match the user's interests and travel style.",
        "Prioritize information from reliable sources and official travel guides.",
        "Provide well-structured summaries with key insights and recommendations."
    ],
    model=Gemini(id="gemini-2.0-flash-exp"),
    tools=[SerpApiTools(api_key=SERPAPI_KEY)],
)

planner = Agent(
    name="Planner",
    instructions=[
        "Gather details about the user's travel preferences and budget.",
        "Create a detailed itinerary with scheduled activities and estimated costs.",
        "Ensure the itinerary includes transportation options and travel time estimates.",
        "Optimize the schedule for convenience and enjoyment.",
        "Present the itinerary in a structured format."
    ],
    model=Gemini(id="gemini-2.0-flash-exp"),
)

hotel_restaurant_finder = Agent(
    name="Hotel & Restaurant Finder",
    instructions=[
        "Identify key locations in the user's travel itinerary.",
        "Search for highly rated hotels near those locations.",
        "Search for top-rated restaurants based on cuisine preferences and proximity.",
        "Prioritize results based on user preferences, ratings, and availability.",
        "Provide direct booking links or reservation options where possible."
    ],
    model=Gemini(id="gemini-2.0-flash-exp"),
    tools=[SerpApiTools(api_key=SERPAPI_KEY)],
)

# Generate Travel Plan - Only enabled if both cities are valid
if st.button("🚀 Generate Travel Plan", disabled=not (source_valid and dest_valid)):
    if not source_valid or not dest_valid:
        st.error("⚠️ Please enter valid city names before generating the travel plan.")
    else:
        with st.spinner("✈️ Fetching best flight options..."):
            flight_data = fetch_flights(source_iata, dest_iata, departure_date, return_date)
            cheapest_flights = extract_cheapest_flights(flight_data)

        # AI Processing
        with st.spinner("🔍 Researching best attractions & activities..."):
            research_prompt = (
                f"Research the best attractions and activities in {destination_city} for a {num_days}-day {travel_theme.lower()} trip. "
                f"The traveler enjoys: {activity_preferences}. Budget: {budget}. Flight Class: {flight_class}. "
                f"Hotel Rating: {hotel_rating}. Visa Requirement: {visa_required}. Travel Insurance: {travel_insurance}."
            )
            research_results = researcher.run(research_prompt, stream=False)

        with st.spinner("🏨 Searching for hotels & restaurants..."):
            hotel_restaurant_prompt = (
                f"Find the best hotels and restaurants near popular attractions in {destination_city} for a {travel_theme.lower()} trip. "
                f"Budget: {budget}. Hotel Rating: {hotel_rating}. Preferred activities: {activity_preferences}."
            )
            hotel_restaurant_results = hotel_restaurant_finder.run(hotel_restaurant_prompt, stream=False)

        with st.spinner("🗺️ Creating your personalized itinerary..."):
            planning_prompt = (
                f"Based on the following data, create a {num_days}-day itinerary for a {travel_theme.lower()} trip to {destination_city}. "
                f"The traveler enjoys: {activity_preferences}. Budget: {budget}. Flight Class: {flight_class}. Hotel Rating: {hotel_rating}. "
                f"Visa Requirement: {visa_required}. Travel Insurance: {travel_insurance}. Research: {research_results.content}. "
                f"Flights: {json.dumps(cheapest_flights)}. Hotels & Restaurants: {hotel_restaurant_results.content}."
            )
            itinerary = planner.run(planning_prompt, stream=False)

        # Display Results
        st.subheader(f"✈️ Cheapest Flight Options: {source_city} → {destination_city}")
        if cheapest_flights:
            cols = st.columns(len(cheapest_flights))
            for idx, flight in enumerate(cheapest_flights):
                with cols[idx]:
                    airline_logo = flight.get("airline_logo", "")
                    price = flight.get("price", "Not Available")
                    total_duration = flight.get("total_duration", "N/A")
                    
                    flights_info = flight.get("flights", [{}])
                    departure = flights_info[0].get("departure_airport", {})
                    arrival = flights_info[-1].get("arrival_airport", {})
                    airline_name = flights_info[0].get("airline", "Unknown Airline") 
                    
                    departure_time = format_datetime(departure.get("time", "N/A"))
                    arrival_time = format_datetime(arrival.get("time", "N/A"))
                    
                    departure_token = flight.get("departure_token", "")
                    booking_options = ""

                    if departure_token:
                        try:
                            params_with_token = {
                                "engine": "google_flights",
                                "departure_id": source_iata,
                                "arrival_id": dest_iata,
                                "outbound_date": str(departure_date),
                                "return_date": str(return_date),
                                "currency": "INR",
                                "hl": "en",
                                "api_key": SERPAPI_KEY,
                                "departure_token": departure_token
                            }
                            search_with_token = GoogleSearch(params_with_token)
                            results_with_booking = search_with_token.get_dict()

                            if 'best_flights' in results_with_booking and idx < len(results_with_booking['best_flights']):
                                booking_options = results_with_booking['best_flights'][idx].get('booking_token', '')
                        except Exception as e:
                            st.warning(f"Could not fetch booking link: {str(e)}")

                    booking_link = f"https://www.google.com/travel/flights?tfs={booking_options}" if booking_options else "#"
                    
                    # Flight card layout
                    st.markdown(
                        f"""
                        <div style="
                            border: 2px solid #ddd; 
                            border-radius: 10px; 
                            padding: 15px; 
                            text-align: center;
                            box-shadow: 2px 2px 10px rgba(0, 0, 0, 0.1);
                            background-color: #f9f9f9;
                            margin-bottom: 20px;
                        ">
                            <img src="{airline_logo}" width="100" alt="Flight Logo" />
                            <h3 style="margin: 10px 0;">{airline_name}</h3>
                            <p><strong>Departure:</strong> {departure_time}</p>
                            <p><strong>Arrival:</strong> {arrival_time}</p>
                            <p><strong>Duration:</strong> {total_duration} min</p>
                            <h2 style="color: #008000;">💰 ₹{price}</h2>
                            <a href="{booking_link}" target="_blank" style="
                                display: inline-block;
                                padding: 10px 20px;
                                font-size: 16px;
                                font-weight: bold;
                                color: #fff;
                                background-color: #007bff;
                                text-decoration: none;
                                border-radius: 5px;
                                margin-top: 10px;
                            ">🔗 Book Now</a>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )
        else:
            st.warning("⚠️ No flight data available.")

        st.subheader("🏨 Hotels & Restaurants")
        st.write(hotel_restaurant_results.content)

        st.subheader("🗺️ Your Personalized Itinerary")
        st.write(itinerary.content)

        st.success("✅ Travel plan generated successfully!")