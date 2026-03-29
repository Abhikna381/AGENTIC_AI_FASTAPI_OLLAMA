import os
import requests
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("ACCUWEATHER_API_KEY")

def get_location_details(user_query):
    """
    Fetches full location details with smart name detection for India.
    """
    if user_query.isdigit():
        url = "http://dataservice.accuweather.com/locations/v1/postalcodes/IN/search"
    else:
        url = "http://dataservice.accuweather.com/locations/v1/cities/IN/search"

    params = {"apikey": API_KEY, "q": user_query}

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()

        if data and len(data) > 0:
            loc = data[0]
            
            # --- SMART NAME DETECTION ---
            # 1. Try standard LocalizedName
            name = loc.get('LocalizedName')
            
            # 2. If it's a PIN search, name might be in ParentCity
            if not name and 'ParentCity' in loc:
                name = loc['ParentCity'].get('LocalizedName')
            
            # 3. Last resort: EnglishName
            if not name:
                name = loc.get('EnglishName', 'Unknown Location')

            return {
                "key": loc.get('Key'),
                "city": name,
                "state": loc['AdministrativeArea']['LocalizedName'],
                "pin": loc.get('PrimaryPostalCode', user_query if user_query.isdigit() else "N/A")
            }
    except Exception as e:
        print(f"❌ API Error: {e}")
        
    return None


def get_weather(location_key):
    """Gets current weather conditions."""
    url = f"http://dataservice.accuweather.com/currentconditions/v1/{location_key}"
    params = {"apikey": API_KEY}
    
    try:
        response = requests.get(url, params=params)
        data = response.json()
        if data:
            return f"{data[0]['Temperature']['Metric']['Value']}°C, {data[0]['WeatherText']}"
    except:
        return "Weather data unavailable."
    return "N/A"

def main():
    print("--- 🌍 AccuWeather India Agent ---")
    user_input = input("🏙️ Enter City or Pin Code: ")
    
    loc = get_location_details(user_input)
    
    if loc:
        print(f"\n📍 Found: {loc['city']}, {loc['state']} (Pin: {loc['pin']})")
        print(f"🔍 Fetching live data for {loc['city']}...")
        
        report = get_weather(loc['key'])
        print(f"🤖 AccuWeather: {report}")
    else:
        print(f"❌ 🤖: Sorry, I couldn't find details for '{user_input}' in India.")

if __name__ == "__main__":
    main()