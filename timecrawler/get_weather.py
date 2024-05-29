import requests
import json

# https://archive-api.open-meteo.com/v1/archive?latitude=52.52&longitude=13.41&start_date=2024-01-01&end_date=2024-05-29&daily=snowfall_sum,shortwave_radiation_sum&timezone=Europe%2FBerlin


def get_weather(args, timecrawler):
    start_date= timecrawler.start_date.strftime("%Y-%m-%d")
    end_date   = timecrawler.end_date.strftime("%Y-%m-%d")
    url = f"https://archive-api.open-meteo.com/v1/archive?latitude=52.52&longitude=13.41&start_date={start_date}&end_date={end_date}&daily=snowfall_sum,shortwave_radiation_sum&timezone=Europe%2FBerlin"

    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        print("Data fetched successfully:", json.dumps(data, indent=2))
    else:
        print("Failed to fetch data. Status code:", response.status_code)


    dates     = data["daily"]["time"]
    snowfall  = data["daily"]["snowfall_sum"]
    radiation = data["daily"]["shortwave_radiation_sum"]

    for day in timecrawler:
        
        if(day.timestamp in dates):
            index = dates.index(day.timestamp)
            day.update_channel("weather", [], {
                "snowfall": snowfall[index],
                "radiation": radiation[index]
            })
        
