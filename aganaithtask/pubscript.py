import requests
import xml.etree.ElementTree as ET
import csv
from datetime import datetime

# Step 1: Get the search query from the user
query = str(input("Enter your search query: "))
ufilename = ""

# Command options
opt = str(input("Enter option (-h for help, -f for filename input): "))
if opt == "-h":
    print("1. Enter the Book name for book metadata.")
    print("2. Default metadata is generated with a timestamped CSV file or provide a file name using -f.")
elif opt == "-f":
    ufilename = str(input("Enter your custom file name: "))

# Construct the URL for the esearch endpoint
search_url = f'https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=pubmed&term={query}'

# Step 2: Make the API request to esearch
response = requests.get(search_url)

# Check if the request was successful
if response.status_code == 200:
    # Parse the XML response from the esearch endpoint
    data = ET.fromstring(response.text)
    
    # Extract total count of results and list of PubMed IDs
    count = data.find("Count").text if data.find("Count") is not None else "0"
    id_list = [id_elem.text for id_elem in data.findall("IdList/Id")]
    
    # Get the top PubMed ID (if available)
    if id_list:
        top_pmid = id_list[0]
        print(f"Top PubMed ID: {top_pmid}")
        
        # Step 3: Fetch detailed document info using esummary with the top PubMed ID
        esummary_url = f'https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi?db=pubmed&id={top_pmid}&retmode=xml'
        esummary_response = requests.get(esummary_url)
        
        if esummary_response.status_code == 200:
            # Parse the XML response from the esummary endpoint
            esummary_data = ET.fromstring(esummary_response.text)
            
            # Extract relevant data from the XML response
            doc = esummary_data.find("DocSum")
            title = doc.find("Item[@Name='Title']").text if doc.find("Item[@Name='Title']") is not None else "N/A"
            pub_date = doc.find("Item[@Name='PubDate']").text if doc.find("Item[@Name='PubDate']") is not None else "N/A"
            authors = [author.text for author in doc.findall("Item[@Name='Author']")]
            affiliations = [affil.text for affil in doc.findall("Item[@Name='Affil']", namespaces={'': ''})]  # Namespace handling
            email = doc.find("Item[@Name='Email']").text if doc.find("Item[@Name='Email']") is not None else "N/A"
            
            # Use the custom filename if provided, otherwise generate a timestamped filename
            if ufilename != '':
                filename = ufilename
            else:
                filename = f"fetched{datetime.now().strftime('%Y%m%d%H%M%S')}.csv"
            
            # Step 4: Write the extracted data into a CSV file
            with open(filename, mode='w', newline='') as file:
                writer = csv.writer(file)
                # Write the header
                writer.writerow(['Title', 'Publication Date', 'Authors', 'Affiliations', 'Author Email'])
                # Write the article details
                writer.writerow([title, pub_date, ', '.join(authors), ', '.join(affiliations), email])
            
            print(f"Data saved to {filename}")
        else:
            print(f"Error fetching document details: HTTP {esummary_response.status_code}")
    else:
        print("No PubMed IDs found.")
else:
    print(f"Error: HTTP {response.status_code}")

