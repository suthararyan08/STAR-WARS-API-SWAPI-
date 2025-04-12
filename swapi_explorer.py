# import the necessary libraries

import requests
import json
import os
import matplotlib.pyplot as plt

# Create a new folder named data
DATA_DIR = "data"
os.makedirs(DATA_DIR, exist_ok=True)


def save_to_json(data, filename):
    """
    Saves the given data to a JSON file in the data directory.
    """
    path = os.path.join(DATA_DIR, filename)
    try:
        with open(path, "w") as f:
            json.dump(data, f, indent=4)
        print(f"Saved to {path}")
    except Exception as e:
        print(f"Error saving file: {e}")


def search_character(name):
    """
    Searches for a Star Wars character by name using SWAPI.
    Returns character data as a dictionary.
    """
    url = f"https://swapi.dev/api/people/?search={name}"
    try:
        response = requests.get(url)
        response.raise_for_status()
        results = response.json().get("results", [])
        if results:
            char = results[0]
            print(f"\nFound: {char['name']}")
            save_to_json(char, f"{char['name'].replace(' ', '_')}.json")
            return char
        else:
            print("Character not found.")
            return None
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
        return None


def compare_characters(name1, name2):
    """
    Compares two Star Wars characters based on height, mass, birth year, and gender.
    """
    char1 = search_character(name1)
    char2 = search_character(name2)
    if not char1 or not char2:
        print("Cannot compare. One or both characters not found.")
        return

    print(f"\n--- Comparison: {char1['name']} vs {char2['name']} ---")
    for key in ['height', 'mass', 'birth_year', 'gender']:
        val1 = char1.get(key, 'N/A')
        val2 = char2.get(key, 'N/A')
        print(f"{key.capitalize()}: {val1} vs {val2}")


def find_connections(name):
    """
    Finds and prints the homeworld and films for a given Star Wars character.
    """
    char = search_character(name)
    if not char:
        return
    try:
        homeworld_resp = requests.get(char['homeworld'])
        homeworld_resp.raise_for_status()
        homeworld = homeworld_resp.json().get('name', 'Unknown')

        films = []
        for film_url in char.get('films', []):
            film_resp = requests.get(film_url)
            film_resp.raise_for_status()
            films.append(film_resp.json().get('title', 'Unknown'))

        print(f"\nConnections for {char['name']}:")
        print(f"Homeworld: {homeworld}")
        print("Films:")
        for f in films:
            print(f" - {f}")
    except requests.exceptions.RequestException as e:
        print(f"Error fetching connections: {e}")


def species_lifespan_stats():
    """
    Fetches all species from SWAPI, calculates average lifespan,
    and generates a bar chart.
    """
    lifespans = []
    labels = []
    url = "https://swapi.dev/api/species/"

    try:
        while url:
            res = requests.get(url)
            res.raise_for_status()
            data = res.json()
            for sp in data['results']:
                lifespan = sp.get('average_lifespan', 'unknown')
                if lifespan.isdigit():
                    lifespans.append(int(lifespan))
                    labels.append(sp.get('name', 'Unknown'))
            url = data.get('next')
    except requests.exceptions.RequestException as e:
        print(f"Failed to fetch species data: {e}")
        return

    if lifespans:
        avg = sum(lifespans) / len(lifespans)
        print(f"\nAverage Lifespan: {avg:.2f} years")
        save_to_json(dict(zip(labels, lifespans)), "species_lifespans.json")
        plot_lifespan_chart(labels, lifespans)
    else:
        print("No valid lifespan data found.")


def plot_lifespan_chart(labels, lifespans):
    """
    Plots a bar chart of average lifespan by species.
    """
    try:
        plt.figure(figsize=(12, 6))
        plt.bar(labels, lifespans, color="skyblue")
        plt.xticks(rotation=45, ha='right')
        plt.xlabel("Species")
        plt.ylabel("Average Lifespan (years)")
        plt.title("Average Lifespan by Species in Star Wars")
        plt.tight_layout()
        chart_path = os.path.join(DATA_DIR, "species_lifespans_chart.png")
        plt.savefig(chart_path)
        print(f"Chart saved as {chart_path}")
        plt.show()
    except Exception as e:
        print(f"Failed to create chart: {e}")


def main():
    """
    Displays the main menu and routes user choices.
    """
    while True:
        print("\nStar Wars Explorer Menu:")
        print("1. Search Character")
        print("2. Compare Characters")
        print("3. Find Connections")
        print("4. Species Lifespan Stats (with Chart)")
        print("5. Exit")
        choice = input("Enter option: ")

        if choice == "1":
            search_character(input("Character name: "))
        elif choice == "2":
            compare_characters(input("First character: "), input("Second character: "))
        elif choice == "3":
            find_connections(input("Character name: "))
        elif choice == "4":
            species_lifespan_stats()
        elif choice == "5":
            print("Goodbye!")
            break
        else:
            print("Error: Invalid choice.")


if __name__ == "__main__":
    main()
