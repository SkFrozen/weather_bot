import csv
import os


def get_countries_list(file_name: str) -> list:
    """Reads csv file with countries name and ISO2 code
    returns list of countries names
    """
    countries_file = os.path.join(os.getcwd(), file_name)
    with open(countries_file, "r") as file:
        reader = csv.reader(file)
        countries = ["/".join(row) for row in reader]
    return countries
