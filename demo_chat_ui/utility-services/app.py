import logging
import os
from bs4 import BeautifulSoup
from fastapi import FastAPI
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings
from langchain_community.document_loaders import PyPDFDirectoryLoader
import requests
from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())

# Custom Imports
from utils import *



# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = FastAPI()

@app.get("/generate_vector")
def generate_vector():
    # options : list, categories : list
    logger.info("RequestIn: Generate Vector Function.")
    
    try:
        # Load and split document
        loader = PyPDFDirectoryLoader("../example_data")
        pages = loader.load_and_split()
        logger.info("Document loaded and split successfully.")

        # Create and save vector store
        # [
        #     "Milk is a source of essential nutrients such as calcium, vitamin D, and protein.",
        #     "The average cow produces about 22 liters of milk per day.",
        #     "Milk is typically pasteurized to kill harmful bacteria and extend shelf life.",
        #     "Different types of milk include whole milk, skim milk, and lactose-free milk.",
        #     "The United States is one of the largest milk producers globally, with over 9 million dairy cows.",
        #     "Milk should be stored at a temperature below 4°C (39°F) to maintain its freshness.",
        #     "Milk is a versatile ingredient used in cooking and baking, enhancing the flavor and texture of many dishes.",
        #     "There are various types of milk beyond dairy, including almond milk, soy milk, and oat milk, catering to different dietary needs and preferences.",
        #     "Milk production involves several steps, including milking, cooling, and processing to ensure quality and safety.",
        #     "The fat content in milk can vary, with whole milk containing about 3.25% fat, reduced-fat milk at 2%, and skim milk with less than 0.5% fat.",
        #     "Organic milk comes from cows that are fed organic feed and are not treated with antibiotics or synthetic hormones.",
        #     "Milk is often fortified with additional nutrients, such as vitamin A and D, to improve its nutritional value.",
        #     "The shelf life of milk is typically around 7-10 days after the 'sell by' date if stored properly in the refrigerator.",
        #     "Milk is a crucial part of many traditional diets around the world and is integral to numerous cultural practices and recipes.",
        #     "You can order milk from us online, on-site, or over the call.",
        #     "We Provide Quality Milk in bulk quantity.",
        #     "Our company name is Sheer Ghar.",
        # ]
        vectorstore = FAISS.from_documents(pages, embedding=OpenAIEmbeddings())
        
        vectorstore.save_local("../index")
        logger.info("Vector store created and saved successfully.")
        logger.info("RequestOut: Generate Vector Function.")
        
        return {"success": 200}
    
    except FileNotFoundError as e:
        logger.error(f"File not found: {e}", exc_info=True)
        return {"error": "File not found"}

    except ValueError as e:
        logger.error(f"Value error: {e}", exc_info=True)
        return {"error": "Value error"}

    except TypeError as e:
        logger.error(f"Type error: {e}", exc_info=True)
        return {"error": "Type error"}

    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}", exc_info=True)
        return {"error": "An unexpected error occurred"}




@app.get("/get_categories")
def get_categories():
    categories = []
    try:
        # Get the base URL from environment variable
        PAKISTAN_CODE_BASE_URL = os.getenv("PAKISTAN_CODE_BASE_URL")
        if not PAKISTAN_CODE_BASE_URL:
            raise ValueError("Environment variable 'PAKISTAN_CODE_BASE_URL' not set")

        try:
            response = requests.get(PAKISTAN_CODE_BASE_URL)
            response.raise_for_status()
        except requests.RequestException as e:
            logger.error(f"Error in fetching the URL '{PAKISTAN_CODE_BASE_URL}': {e}")
            return []

        try:
            soup = BeautifulSoup(response.content, 'html.parser')
            category_div = soup.find('div', id='category')
            if not category_div:
                raise ValueError("Div with id 'category' not found")

            ul_element = category_div.find("ul")
            if not ul_element:
                raise ValueError("No <ul> element found within the category div")

            deptlist_divs = ul_element.find_all('div', class_='deptlist')
            if not deptlist_divs:
                logger.warning("No department list divs found")
                return []

            for i, div in enumerate(deptlist_divs):
                a = div.find('a')
                if a:
                    link_info = extract_links_info(a)
                    categories.append(link_info)
                    logger.info(f"Inserted: {link_info} in Categories")
                else:
                    logger.warning(f"No <a> tag found in deptlist div {i}")

        except (AttributeError, ValueError) as e:
            logger.error(f"Error processing HTML content: {e}")
            return []

    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return []

    return categories

# def get_categories_data():