import json
import os
import time

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

from data_extractor import extract
from simple_logging import log_info, log_error, log_success

PROBLEMATIC_LINKS_FILE_NAME = "error_links.txt"
EXTRACTED_DATA_DIRECTORY_NAME = "extracted_bmw_data"
LINKS_FILE_NAME = "data_scrapping\\unique_bmw_links.txt"
RESUME_FILE_NAME = "resume.txt"
JSON_TAG_ID = "__NEXT_DATA__"

CHROME_OPTIONS = Options()
CHROME_OPTIONS.add_argument("--ignore-certificate-errors")
CHROME_OPTIONS.add_argument("--allow-running-insecure-content")
CHROME_OPTIONS.add_argument("--disable-web-security")
CHROME_OPTIONS.add_argument("--enable-unsafe-swiftshader")
CHROME_OPTIONS.add_argument("--disable-xss-auditor")
DRIVER = webdriver.Chrome(options=CHROME_OPTIONS)


def ensure_resume_file_exists():
    global RESUME_FILE_NAME
    if not os.path.exists(RESUME_FILE_NAME):
        log_info(f'Plik .txt z informacjami o wznawianu nie istnieje, tworzę nowy pod nazwą: {RESUME_FILE_NAME}')
        file = open(RESUME_FILE_NAME, 'w')
        file.write(str(0))
        file.close()


def ensure_error_links_file_exists():
    global PROBLEMATIC_LINKS_FILE_NAME
    if not os.path.exists(PROBLEMATIC_LINKS_FILE_NAME):
        log_info(f'Plik .txt z niedziałającymi linkami nie istnieje, tworzę nowy pod nazwą: {PROBLEMATIC_LINKS_FILE_NAME}')
        file = open(PROBLEMATIC_LINKS_FILE_NAME, "w")
        file.close()


def ensure_extracted_data_directory_exists():
    global EXTRACTED_DATA_DIRECTORY_NAME
    if not os.path.exists(EXTRACTED_DATA_DIRECTORY_NAME):
        log_info(f'Folder z wynikami nie istnieje, tworzę nowy pod nazwą: {EXTRACTED_DATA_DIRECTORY_NAME}')
        os.makedirs("./" + EXTRACTED_DATA_DIRECTORY_NAME)


def update_resume_file():
    global RESUME_FILE_NAME
    with open(RESUME_FILE_NAME, "r") as file:
        line = int(file.read()) + 1
    with open(RESUME_FILE_NAME, "w") as file:
        file.write(str(line))


def append_link_to_problematic_links_file(line):
    global PROBLEMATIC_LINKS_FILE_NAME
    with open(PROBLEMATIC_LINKS_FILE_NAME, 'a') as file:
        file.write(line)
    log_info("Zapisano link jako problematyczny")


def save_to_file(content):
    global EXTRACTED_DATA_DIRECTORY_NAME
    file_name = content["id"]
    path_to_file = f'{EXTRACTED_DATA_DIRECTORY_NAME}/{file_name}'
    with open(path_to_file, 'w') as file:
        file.write(json.dumps(content))
    log_success(f'Zapisano {content["make"].upper()} o id: {file_name}')


def get_raw_offer_data(url):
    global DRIVER
    DRIVER.get(url)
    WebDriverWait(DRIVER, 30).until(EC.presence_of_element_located((By.ID, JSON_TAG_ID)))
    json_data_element = DRIVER.find_element(By.ID, JSON_TAG_ID)
    time.sleep(2)
    return json.loads(json_data_element.get_attribute("innerHTML"))


def resolve_offer(line):
    url = line.rstrip()
    offer_data = get_raw_offer_data(url)
    return extract(offer_data)


def resolve_offers_from_file(file_name, total_lines, resume_line=0):
    if resume_line != 0:
        log_info(f'Wznawiam odczytywanie od linii {resume_line}')
    else:
        log_info("Odczytywanie uruchomi się od początku pliku")
    total_successes = 0
    total_failures = 0
    total_read_lines = total_lines - resume_line
    log_info(f'Odczytuję {total_read_lines} ofert z {file_name}')
    with open(file_name, "r") as file:
        lines_to_resolve = [next(file) for _ in range(resume_line, total_read_lines)]
    for line in lines_to_resolve:
        try:
            resolved_offer = resolve_offer(line)
        except Exception as e:
            log_error(f'Wystąpił błąd: {e}')
            append_link_to_problematic_links_file(line)
            total_failures += 1
            update_resume_file()
            continue
        save_to_file(resolved_offer)
        total_successes += 1
        update_resume_file()
    log_info(f'Odczytano {total_successes} pomyślnie i {total_failures} niepomyślnie z {total_read_lines} ofert')


def setup(links_file_name):
    ensure_extracted_data_directory_exists()
    ensure_error_links_file_exists()
    ensure_resume_file_exists()
    with open(links_file_name, 'r') as file:
        total_lines = sum(1 for _ in file)
    global RESUME_FILE_NAME
    with open(RESUME_FILE_NAME, "r") as file:
        resume_line = int(file.read().rstrip())
    resolve_offers_from_file(links_file_name, total_lines, resume_line)


setup(LINKS_FILE_NAME)
