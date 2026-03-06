weather_data = { 
   "Chennai": {"temp": 34, "condition": "Sunny"}, 
   "Mumbai": {"temp": 29, "condition": "Rainy"}, 
   "Delhi": {"temp": 32, "condition": "Cloudy"}, 
   "Bangalore": {"temp": 27, "condition": "Windy"}
}

def get_weather(city):
    if city in weather_data:
        return weather_data[city]
    else:
        return "City not found in the database."
    
def find_hottest_city():
    hottest_city = None
    max_temp = -float('inf')
    
    for city, data in weather_data.items():
        if data["temp"] > max_temp:
            max_temp = data["temp"]
            hottest_city = city
    
    return hottest_city, max_temp

 #its working perfectly :)   
    