from bs4 import BeautifulSoup
import pandas as pd

# File path of the local HTML file
file_path = "RDI_metafiles/BonaRes/BonaRes DOIs.htm"

# Open the file with 'utf-8' encoding and parse the HTML content with BeautifulSoup
with open(file_path, 'r', encoding='utf-8') as f:
    contents = f.read()

soup = BeautifulSoup(contents, 'html.parser')

# Find the table with class 'table'
table = soup.find('table', class_='table')

#print("table: ", table)

# Prepare lists to store the scraped data
titles = []
dois = []

# Check if the table is not None
if table is not None:
    # Iterate over each row in the table (skipping the header)
    for row in table.find_all('tr')[1:]:
        # Get all the columns in the row
        columns = row.find_all('td')
        # Get the title and DOI
        title = columns[1].find("a", class_="bonares-link").text.strip()
        doi = columns[1].find("span", class_="text-muted").text.strip().replace("DOI: ", "")

        # Append the title and DOI to the respective lists
        titles.append(title)
        dois.append(doi)

    # Create a DataFrame from the lists
    df = pd.DataFrame({'Title': titles, 'DOI': dois})

    # Write the DataFrame to a CSV file
    df.to_csv('RDI_metafiles/BonaRes/bonares_dois.csv', index=False)
else:
    print("No table with class 'table' found")
