# Ścieżka do pliku wejściowego
input_file = "otomoto_links.txt"
# Ścieżka do pliku wyjściowego
output_file = "unique_links.txt"

# Wczytaj linki z pliku wejściowego
with open(input_file, "r", encoding="utf-8") as file:
    lines = file.readlines()

# Usuń duplikaty, zachowując kolejność
unique_lines = []
seen = set()
for line in lines:
    line = line.strip()  # Usuń białe znaki (np. znaki nowej linii)
    if line and line not in seen:  # Sprawdź, czy linia nie jest pusta i nie została już dodana
        unique_lines.append(line)
        seen.add(line)

# Zapisz unikalne linki do pliku wyjściowego
with open(output_file, "w", encoding="utf-8") as file:
    for line in unique_lines:
        file.write(line + "\n")

print(f"Znaleziono {len(unique_lines)} unikalnych linków. Zapisano do pliku '{output_file}'.")