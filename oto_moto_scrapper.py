from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import time
import random
import os

# Konfiguracja Selenium
chrome_options = Options()
chrome_options.add_argument("--ignore-certificate-errors")
chrome_options.add_argument("--allow-running-insecure-content")
chrome_options.add_argument("--disable-web-security")
chrome_options.add_argument("--enable-unsafe-swiftshader")
chrome_options.add_argument("--disable-xss-auditor")


def get_all_links_from_page(url: str, retries=3) -> list[str]:
    '''
    Funkcja zwraca listę linków z danej strony.
    
    :param url: Adres URL strony
    :param retries: Liczba prób ponowienia w przypadku błędu
    :return: Lista linków
    
    '''

    for attempt in range(retries):
        try:
            # Inicjalizacja przeglądarki
            driver = webdriver.Chrome(options=chrome_options)
            driver.get(url)
            WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.TAG_NAME, 'a'))
            )
            # Symuluj przewijanie strony
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)  # Poczekaj na załadowanie treści

            # Znajdź wszystkie linki na stronie
            all_links = driver.find_elements(By.TAG_NAME, 'a')
            links = [link.get_attribute('href') for link in all_links]

            # Filtruj tylko linki zaczynające się od "https://www.otomoto.pl/osobowe/oferta/"
            filtered_links = [link for link in links if link and link.startswith('https://www.otomoto.pl/osobowe/oferta/')]

            driver.quit()
            return filtered_links
        except (TimeoutException, NoSuchElementException) as e:
            print(f"Próba {attempt + 1} nie powiodła się: {e}")
            if 'driver' in locals():
                driver.quit()
            time.sleep(5)
    return []

# Funkcja do zapisu numeru ostatniej strony
def save_last_page(page):
    with open("last_page.txt", "w", encoding="utf-8") as file:
        file.write(str(page))

# Funkcja do odczytu numeru ostatniej strony
def load_last_page():
    if os.path.exists("last_page.txt"):
        with open("last_page.txt", "r", encoding="utf-8") as file:
            return int(file.read().strip())
    return 1  # Domyślnie zacznij od strony 1

# Funkcja do zapisywania linków do pliku
def save_links_to_file(links, filename="otomoto_links.txt"):
    with open(filename, "a", encoding="utf-8") as file:  # Tryb append (dopisywanie)
        for link in links:
            file.write(link + "\n")

# Główna funkcja do scrapowania wszystkich ogłoszeń
def scrape_all_offers(base_url):
    all_links = set()  # Używamy set, aby uniknąć duplikatów
    last_page = load_last_page()  # Odczytaj numer ostatniej strony
    page = last_page

    try:
        while True:
            # Format URL dla pierwszej strony i kolejnych
            if page == 1:
                url = base_url
            else:
                url = f"{base_url}?page={page}"

            print(f"Pobieranie linków z strony: {url}")
            links = get_all_links_from_page(url)

            # Jeśli nie ma więcej ogłoszeń, przerwij pętlę
            if not links:
                print("Brak kolejnych ogłoszeń. Zakończono scrapowanie.")
                break

            # Dodaj linki do zbioru (set automatycznie usuwa duplikaty)
            all_links.update(links)
            save_last_page(page)  # Zapisz numer ostatniej strony

            # Zapisz linki do pliku na bieżąco
            save_links_to_file(links)

            page += 1
            time.sleep(random.uniform(2, 5))  # Losowe opóźnienie między 2 a 5 sekund

    except Exception as e:
        print(f"Wystąpił błąd: {e}")
    finally:
        # Zawsze zapisz wyniki, nawet w przypadku błędu
        save_links_to_file(all_links)
        print(f"Znaleziono {len(all_links)} unikalnych linków. Zapisano do pliku 'otomoto_links.txt'.")

# Uruchomienie scrapowania
base_url = "https://www.otomoto.pl/osobowe/bmw"
scrape_all_offers(base_url)