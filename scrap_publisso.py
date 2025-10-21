import requests

url = "https://frl.publisso.de/find?q=contentType:researchData&from=0&until=200&format=json"

response = requests.get(url)
response.raise_for_status()  # will raise an error if request failed

data = response.json()  # this is a list

with open("dois.txt", "w") as file:
    for item in data:
        doi = item.get("doi")  # each item is a dict
        if doi:
            file.write(f"{doi}\n")

print("DOIs have been written to dois.txt")
