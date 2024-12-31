import requests
from bs4 import BeautifulSoup
from tempfile import NamedTemporaryFile
from langchain_community.document_loaders import PyPDFLoader
import os


# Utilities For The FastApi Service
def extract_links_info(a):
    print("Inside the extract_links_info with: ",a)
    return {"category":a.get_text(strip=True), "url":a.get('href')}



def download_law(acts):
    for act in acts:
        base_url = 'https://pakistancode.gov.pk/english/'+act["url"]
        # print(base_url)
        response = requests.get(base_url)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')
        iframe = soup.find('iframe')
        pdf_url = iframe['src']
        pdf_url = pdf_url.split('/')
        pdf_url = pdf_url[0] + '//' + pdf_url[2] + '/' + pdf_url[5] + '/' + pdf_url[6]
        print("Reading the Following: "+pdf_url)
        read_pdf_from_url(pdf_url)



documents = []

def read_pdf_from_url(url):
    # # Fetch the PDF from the URL
    response = requests.get(url)
    
    if response.status_code == 200:
        # Save PDF to a temporary file
        with NamedTemporaryFile(delete=False, suffix='.pdf') as temp_file:
            temp_file.write(response.content)
            temp_file_path = temp_file.name
            temp_file.flush()
        
        # Use PyPDFLoader to load the PDF
        loader = PyPDFLoader(temp_file_path)
        documents.extend(loader.load_and_split())
        # print(documents)
        # # Print the content of each document
        # for doc in documents:
        #     print(doc)
        
        # Clean up the temporary file
        os.remove(temp_file_path)
    else:
        print(f"Failed to fetch PDF: Status code {response.status_code}")
