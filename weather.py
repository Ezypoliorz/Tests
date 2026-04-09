import python_weather
import asyncio
import datetime

async def getWeather() :
  async with python_weather.Client() as client:
    weather = await client.get('Bayeux')
    
    for daily in weather :
        date = daily.date.strftime("%d/%m/%Y")
        print(f"{date} :")
        for hourly in daily :
            time = hourly.time.strftime("%H:%M")
            kind = hourly.kind
            temperature = hourly.temperature
            feels_like = hourly.feels_like
            humidity = hourly.humidity
            wind_direction = hourly.wind_direction
            wind_speed = hourly.wind_speed
            print(f"  {time} - {kind.emoji}")
            print(f"    Temperature : {temperature}°C (feels like {feels_like}°C)")
            print(f"    Weather : {str(kind).lower()}")


if __name__ == '__main__':
  asyncio.run(getWeather())