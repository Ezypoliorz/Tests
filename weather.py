# Simple program fetching weather data from Python_weather

import python_weather
import asyncio
import sys
import io

# Forces output to UTF-8, needed to display certain symbols in the console
sys.stdout = io.TextIOWrapper(sys.stdout.buffer , encoding = 'utf-8')

async def getWeather(city : str) :
	# Initializes a Python_weather client
	async with python_weather.Client() as client :
		# Fetches a weather forecast for a specified city
		weather = await client.get(city)

		daysFetched = 50 # Number of days' forecasts to fetch

		# Goes through the forecast for the following days
		forecasts = list(weather)
		for daily in forecasts[0:daysFetched] if len(forecasts) >= daysFetched else forecasts :
			dailyWeather = {
				'output' : [],
			}
			# Goes through the hourly forecast
			for hourly in daily :
				# Fetches the main informations
				time = hourly.time.strftime("%H:%M")
				kind = hourly.kind
				temperature = hourly.temperature
				feelsLike = hourly.feels_like
				humidity = hourly.humidity
				windDirection = hourly.wind_direction
				windSpeed = hourly.wind_speed
				windGust = hourly.wind_gust

				# Appends the data to the output
				dailyWeather['output'].append(f"  {time}")
				dailyWeather['output'].append(f"    Temperature : {temperature}°C (feels like {feelsLike}°C)")
				dailyWeather['output'].append(f"    Weather : {str(kind).lower()}")
				dailyWeather['output'].append(f"    Humidity : {humidity}%")
				dailyWeather['output'].append(f"    Winds : {windSpeed}km/h from {windDirection} (gusts up to {windGust}km/h)")

				# Checks for weather hazards
				dailyWeather['frost'] = hourly.chances_of_frost if not 'frost' in dailyWeather or dailyWeather['frost'] <= hourly.chances_of_frost else dailyWeather['frost']
				dailyWeather['snow'] = hourly.chances_of_snow if not 'snow' in dailyWeather or dailyWeather['snow'] <= hourly.chances_of_snow else dailyWeather['snow']
				dailyWeather['thunder'] = hourly.chances_of_thunder if not 'thunder' in dailyWeather or dailyWeather['thunder'] <= hourly.chances_of_thunder else dailyWeather['thunder']
				dailyWeather['fog'] = hourly.chances_of_fog if not 'fog' in dailyWeather or dailyWeather['fog'] <= hourly.chances_of_fog else dailyWeather['fog']
			
			# Displays the data
			date = daily.date.strftime("%d/%m/%Y")
			print(f"{date} :")
			for warning in ["frost", "snow", "thunder", "fog"] :
				if dailyWeather[warning] and dailyWeather[warning] >= 50 :
					print(f"    ⚠️ - Risk of {warning} : {dailyWeather[warning]}%")
			for output in dailyWeather['output'] :
				print(output)

if __name__ == '__main__':
	asyncio.run(getWeather("Tessel"))