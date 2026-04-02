import pygame
import pygame_gui
import openmeteo_requests
import requests_cache
from retry_requests import retry

#open meteo settings
cache_session = requests_cache.CachedSession('.cache', expire_after = 3600)
retry_session = retry(cache_session, retries = 5, backoff_factor = 0.2)
openmeteo = openmeteo_requests.Client(session = retry_session)
url = "https://api.open-meteo.com/v1/forecast"
params = {
    "latitude": 52.52,
    "longitude": 13.41,
    "daily": ["temperature_2m_max", "precipitation_probability_max"],
    "forecast_days": 3
}
refresh_mins = 1

days = ["today", "tomorrow", "the day after tomorrow"]
daily_temperature_2m_max = []
daily_precipitation_probability_max = []
weather_index = 0
have_weather_data = False

pygame.init()

pygame.display.set_caption('Weather')
window_surface = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)

background = pygame.Surface((800, 600))
background.fill(pygame.Color('#000000'))
manager = pygame_gui.UIManager((800, 600))


today_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((10, 10), (150, 50)),
                                         text='Today',
                                         manager=manager)

tomorrow_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((200, 10), (150, 50)),
                                         text='Tomorrow',
                                         manager=manager)

tda_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((400, 10), (150, 50)),
                                         text='The Day After',
                                         manager=manager)

main_text = pygame_gui.elements.UITextBox(html_text = "Getting weather info ...", relative_rect=pygame.Rect((10,100), (400,400)),
                                          manager = manager)

clock = pygame.time.Clock()
is_running = True

weather_time = pygame.event.custom_type()
pygame.time.set_timer(weather_time, 60*refresh_mins*1000)
pygame.event.post(pygame.event.Event(weather_time)) # trigger the first weather event at start

    
changed = True

while is_running:

    time_delta = clock.tick(60)/1000.0

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            is_running = False
        if event.type == pygame_gui.UI_BUTTON_PRESSED:
            if event.ui_element == today_button:
                weather_index = 0
                changed = True
            if event.ui_element == tomorrow_button:
                weather_index = 1
                changed = True
            if event.ui_element == tda_button:
                weather_index = 2
                changed = True

        if event.type == weather_time:
            responses = openmeteo.weather_api(url, params=params)
            response = responses[0]
            daily = response.Daily()
            daily_temperature_2m_max = [daily.Variables(0).Values(0), daily.Variables(0).Values(1),daily.Variables(0).Values(2)]
            daily_precipitation_probability_max = [daily.Variables(1).Values(0), daily.Variables(1).Values(1), daily.Variables(1).Values(1)]
            have_weather_data = True
                
            try:
                responses = openmeteo.weather_api(url, params=params)
                response = responses[0]
                daily = response.Daily()
                daily_temperature_2m_max = [daily.Variables(0).Values(0), daily.Variables(0).Values(1),daily.Variables(0).Values(2)]
                daily_precipitation_probability_max = [daily.Variables(1).Values(0), daily.Variables(1).Values(1), daily.Variables(1).Values(1)]
                have_weather_data = True
            except:
                have_weather_data = False
            changed = True
        manager.process_events(event)
        
    #Render
    if changed:
        if have_weather_data:
            main_text.set_text( f"<b>The weather {days[weather_index]} is:</b><br>" \
                   f"Max Temp: {daily_temperature_2m_max[weather_index]:2.1f} deg C <br/>" \
                   f"Chance of precipitation: {daily_precipitation_probability_max[weather_index]:2.1f}%"
                   )               
        else:
            main_text.set_text("Waiting on weather data ...")
        changed = False

    
    manager.update(time_delta)
    window_surface.blit(background, (0, 0))
    manager.draw_ui(window_surface)
    pygame.display.update()
    
pygame.quit()

