import requests
from datetime import datetime


def get_current_time(city: str) -> dict:
    """Returns the current time in a specified city using WorldTimeAPI (free service)."""
    # Map cities to timezone identifiers for WorldTimeAPI
    city_to_timezone = {
        "new york": "America/New_York",
        "los angeles": "America/Los_Angeles",
        "chicago": "America/Chicago",
        "london": "Europe/London",
        "paris": "Europe/Paris",
        "tokyo": "Asia/Tokyo",
        "sydney": "Australia/Sydney",
        "melbourne": "Australia/Melbourne",
        "brisbane": "Australia/Brisbane",
        "perth": "Australia/Perth",
        "adelaide": "Australia/Adelaide",
        "mumbai": "Asia/Kolkata",
        "beijing": "Asia/Shanghai",
        "moscow": "Europe/Moscow",
        "dubai": "Asia/Dubai",
        "singapore": "Asia/Singapore",
        "berlin": "Europe/Berlin",
        "madrid": "Europe/Madrid",
        "rome": "Europe/Rome",
        "toronto": "America/Toronto",
        "vancouver": "America/Vancouver",
        "denver": "America/Denver",
        "phoenix": "America/Phoenix",
        "seattle": "America/Los_Angeles",
        "miami": "America/New_York",
        "mexico city": "America/Mexico_City",
        "sao paulo": "America/Sao_Paulo",
        "buenos aires": "America/Argentina/Buenos_Aires",
        "cairo": "Africa/Cairo",
        "johannesburg": "Africa/Johannesburg",
        "lagos": "Africa/Lagos",
        "bangkok": "Asia/Bangkok",
        "jakarta": "Asia/Jakarta",
        "manila": "Asia/Manila",
        "hong kong": "Asia/Hong_Kong",
        "seoul": "Asia/Seoul",
        "kuala lumpur": "Asia/Kuala_Lumpur"
    }

    city_lower = city.lower()

    if city_lower not in city_to_timezone:
        return {
            "status": "error",
            "message": f"City '{city}' not supported. Available cities: {', '.join(city_to_timezone.keys())}"
        }

    try:
        timezone = city_to_timezone[city_lower]
        # Use WorldTimeAPI - completely free, no API key required
        # Try HTTPS first, fallback to HTTP if needed
        urls_to_try = [
            f"https://worldtimeapi.org/api/timezone/{timezone}",
            f"http://worldtimeapi.org/api/timezone/{timezone}"
        ]

        response = None
        last_error = None

        for url in urls_to_try:
            try:
                response = requests.get(url, timeout=15)
                response.raise_for_status()
                break
            except requests.exceptions.RequestException as e:
                last_error = e
                continue

        if response is None:
            return {"status": "error", "message": f"Could not connect to time service for {city}: {str(last_error)}"}

        data = response.json()

        # Parse the datetime from the API response
        datetime_str = data['datetime']
        # Example format: 2023-10-11T15:30:45.123456-04:00
        dt = datetime.fromisoformat(datetime_str.replace('Z', '+00:00'))

        return {
            "status": "success",
            "city": city,
            "time": dt.strftime("%I:%M %p"),
            "date": dt.strftime("%Y-%m-%d"),
            "timezone": timezone,
            "day_of_week": dt.strftime("%A"),
            "utc_offset": data.get('utc_offset', 'Unknown')
        }

    except requests.exceptions.RequestException as e:
        return {"status": "error", "message": f"Network error getting time for {city}: {str(e)}"}
    except Exception as e:
        return {"status": "error", "message": f"Error getting time for {city}: {str(e)}"}


def get_current_time_simple(city: str) -> dict:
    """Returns the current time in a specified city using WorldTimeAPI (free service)."""
    # Just use the same implementation as get_current_time since it's already simple and free
    return get_current_time(city)
