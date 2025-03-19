import pandas as pd
import numpy as np

# Ścieżka do pliku wejściowego
input_files = ["unique_audi_links.txt", "unique_bmw_links.txt", "unique_mercedes_links.txt", "unique_vw_links.txt"]


def load_files(input_files):
    # Wczytaj linki z plików wejściowych
    all_links = []
    try:
        for file in input_files:
            with open(file, "r", encoding="utf-8") as file:
                lines = file.readlines()
                all_links += lines
    except FileNotFoundError:
        print("Nie znaleziono pliku wejściowego.")
    
    return all_links


def single_scrapper(link: str) -> dict:
    pass

def scrap_cars_details(all_links: list[str]) -> pd.DataFrame:
    pass