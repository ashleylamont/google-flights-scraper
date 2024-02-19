import os
from time import sleep
from typing import TypedDict

import requests
import tabulate
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

CBR_TO_MEL = "https://www.google.com/travel/flights?tfs=CBwQARoXagwIAhIIL20vMGRwOTByBwgBEgNNRUxAAUgBcAGCAQsI____________AZgBAg&tfu=KgIIAw"
MEL_TO_CBR = "https://www.google.com/travel/flights?tfs=CBwQARoSagcIARIDTUVMcgcIARIDQ0JSQAFIAXABggELCP___________wGYAQI&tfu=KgIIAw"


class Flight(TypedDict):
    airline: str
    price: float
    departure_time: str
    arrival_time: str
    plane: str
    date: str
    departure_airport: str
    arrival_airport: str


start_dates = ['2024-10-09', '2024-10-10', '2024-10-11']
end_dates = ['2024-10-13', '2024-10-14', '2024-10-15']

options = Options()
# For some reason, headless means that some data isn't shown properly
# So you just need to run this as headful from xvfb and it works
# options.add_argument("--headless")
# options.add_argument("--disable-gpu")
options.add_argument('--disable-dev-shm-usage')
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)


def get_flight_info(is_cbr_to_mel: bool, date: str):
    flights: list[Flight] = []
    driver.get(CBR_TO_MEL if is_cbr_to_mel else MEL_TO_CBR)
    departure_field = driver.find_element(By.CSS_SELECTOR,
                                          "input[aria-label='Departure']")
    departure_field.click()
    departure_field.send_keys(date)
    departure_field.send_keys(Keys.RETURN)
    driver.implicitly_wait(2)
    sleep(2)
    driver.find_element(By.CSS_SELECTOR,
                        'div[aria-selected="true"]>div[role="button"]').click()
    driver.implicitly_wait(2)
    sleep(2)
    done_button = driver.find_element(By.CSS_SELECTOR,
                                      "button[aria-label^='Done. Search for']")
    done_button.click()
    driver.implicitly_wait(2)
    search_button = driver.find_element(By.CSS_SELECTOR,
                                        "button[aria-label='Search']")
    search_button.click()
    driver.implicitly_wait(2)
    results = driver.find_elements(By.CSS_SELECTOR,
                                   'ul > li:has(* div[aria-label^="From "])')
    for result in results:
        times_element = result.find_element(By.CSS_SELECTOR,
                                            '*[aria-label^="Leaves"]')
        times_text = times_element.text.replace("\n", "")
        airline_element = result.find_element(By.CSS_SELECTOR,
                                              'div>div>div>div>div>div:has(*[aria-label^="Leaves"])>div+div')
        airline_text = airline_element.text
        price_element = result.find_element(By.CSS_SELECTOR,
                                            'span[aria-label*="dollars"]')

        price_text = price_element.text
        more_button = result.find_element(By.CSS_SELECTOR,
                                          'button[aria-label^="Flight details"]');
        more_button.click()
        driver.implicitly_wait(0.5)
        sleep(0.5)
        plane_text = result.find_element(By.CSS_SELECTOR,
                                         'div[aria-label^="Arrival time"]+div+div>span:nth-child(10)').text
        flights.append({
            "airline": airline_text,
            "price": float(price_text.split("$")[1]),
            "departure_time": times_text.replace(' ', ' ').split(" – ")[0],
            "arrival_time": times_text.replace(' ', ' ').split(" – ")[1],
            "plane": plane_text,
            "date": date,
            "departure_airport": "CBR" if is_cbr_to_mel else "MEL",
            "arrival_airport": "MEL" if is_cbr_to_mel else "CBR"
        })
    print(f"Fetched {len(flights)} flights from {flights[0]['departure_airport']} to {flights[0]['arrival_airport']} on {date}")
    return flights


formatted_flight_info = "# Flight Information\n\n"
formatted_flight_info += f"## CBR -> MEL\n\n"
for start_date in start_dates:
    formatted_flight_info += f"### {start_date}\n\n"
    flight_data = get_flight_info(True, start_date)
    tabulated_flight_data = [["Airline", "Flight", "Price", "Departure Time", "Arrival Time", "From", "To", "Date"]]
    for flight in flight_data:
        tabulated_flight_data.append([flight["airline"], flight["plane"], f"${flight['price']}", flight["departure_time"], flight["arrival_time"], flight["departure_airport"], flight["arrival_airport"], flight["date"]])
    formatted_flight_info += tabulate.tabulate(tabulated_flight_data, headers="firstrow", tablefmt="github")
    formatted_flight_info += "\n\n"
formatted_flight_info += f"## MEL -> CBR\n\n"
for end_date in end_dates:
    formatted_flight_info += f"### {end_date}\n\n"
    flight_data = get_flight_info(False, end_date)
    tabulated_flight_data = [["Airline", "Flight", "Price", "Departure Time", "Arrival Time", "From", "To", "Date"]]
    for flight in flight_data:
        tabulated_flight_data.append([flight["airline"], flight["plane"], f"${flight['price']}", flight["departure_time"], flight["arrival_time"], flight["departure_airport"], flight["arrival_airport"], flight["date"]])
    formatted_flight_info += tabulate.tabulate(tabulated_flight_data, headers="firstrow", tablefmt="github")
    formatted_flight_info += "\n\n"

load_dotenv()
requests.post(os.getenv('WIKI_URL')+"api/documents.update", headers={
    "Authorization": f"Bearer {os.getenv('WIKI_API_KEY')}",
    "Content-Type": "application/json",
    "Accept": "application/json"
}, json={
    "id": os.getenv('PAGE_ID'),
    "title": "Flight Information",
    "text": formatted_flight_info,
    "append": False,
    "publish": True,
    "done": True
})

driver.quit()
