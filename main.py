import pandas as pd
import requests
from bs4 import BeautifulSoup
import time
import os
from datetime import datetime
import schedule
import logging

logging.basicConfig(level=logging.INFO)
# setup the logfile
logging.basicConfig(filename='./logfile.log', filemode='w', format='%(name)s - %(levelname)s - %(message)s')
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# setup chrome options
options = webdriver.ChromeOptions()
options.add_argument("--headless")
options.add_argument("--disable-gpu")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("start-maximized")
options.add_argument("disable-infobars")
options.add_argument("--remote-debugging-port=9222")

# specify the path to chrome driver
driver = webdriver.Chrome("assets/chromedriver", chrome_options=options)
logging.info("Chrome driver started")


def update_file(url, file_name):
    """
    Function that takes in a url and file name and gets the data from the url and writes it to the file
    """
    try:
        html = requests.get(url).text
        soup = BeautifulSoup(html, 'html.parser')
        try:
            table = soup.find('table') # or table = soup.find('table', class_='table')  or table = tables[index_of_the_table]
        except Exception as e:
            logging.error(e)
            print("Error: Table not found on {url} level 1")
            try:
                table = soup.find('table', class_='table')
            except Exception as e:
                logging.error(e)
                print("Error: Table not found on {url} level 2")
                try:
                    table = soup.find('table', class_='table table-bordered table-striped')
                except Exception as e:
                    #* Finally if the table is not found, try selenium to get the table
                    logging.error(e)
                    print("Error: Table not found on {url} level 3")
        df = pd.read_html(str(table))[0]
        df.to_csv(file_name, index=False)
        logging.info(f"{file_name} updated with data from {url}")
    except Exception as e:
        # try:
        #     use_selenium()
        # except Exception as e:
        #     logging.error(e)
        #     print("Error: Table not found on {url} level 4")
        logging.error(e)
        print("Error: Table not found on {url} level 4")


def check_for_updates(url, file_name):
    """
    Function that checks if the file has been updated
    """
    try:
        if os.path.exists(file_name):
            last_modified = datetime.fromtimestamp(os.path.getmtime(file_name))
            current_time = datetime.now()
            time_diff = current_time - last_modified
            if time_diff.seconds > 300:
                update_file(url, file_name)
            else:
                logging.info(f"{file_name} is up to date.")
        else:
            update_file(url, file_name)
    except Exception as e:
        logging.error(e)

def run_job():
    """
    Function that runs the job
    """
    urls = {
        "https://techcrunch.com/tag/layoffs/": "techcrunch_layoffs.csv",
        "https://layoffstracker.com/": "layoffstracker.csv",
        "https://coda.io/@daanyal-kamaal/goto-alumni-list": "coda_alumni.csv",
        "https://docs.google.com/spreadsheets/u/1/d/1OoD3pVxFl718fnxs_cEaOIbcj-45-qNKZFnE1jQW86M/edit#gid=1799438631": "google_docs.csv",
        "https://docs.google.com/spreadsheets/d/1zskuBYEHWep1DDyJSq8cgxMgFGNIZU_lTRy_0WcG1do/edit#gid=1799438631": "tweeps.csv",
        "https://docs.google.com/spreadsheets/u/1/d/1u9li-f7j9_XABMN5GE80kqpfa_mtj3Gq1UPx8Mgp2Hg/htmlview?pru=AAABhHbaQ9Q*UxsibNJRB0F12jFhfAhS3g#" : "jobs_board.csv",
        }
    for url, file_name in urls.items():
        check_for_updates(url, file_name)

        schedule.every(5).minutes.do(run_job)

    while True:
        schedule.run_pending() # Run pending jobs
        time.sleep(1) # Sleep for 1 second

# "https://airtable.com/shrMt3xmtTO0p4MGT/tblka5nfVbLBUTHo4?backgroundColor=green&viewControls=on": "airtable.csv",
#         "https://o1061291.ingest.sentry.io/api/6173372/envelope/?sentry_key=154bcbb799a2437a9aec95856832798e&sentry_version=7": "sentry.csv",
#         "https://layoffs.fyi/": "layoffs.csv",
# def use_selenium():
#     # get the website
#     url = "https://layoffs.fyi"
#     driver.get(url)
#     print(f"Getting data from {url}")
#     try:
#         # wait for the table to load, the table is <div id="table" class="readonly" ...
#         try:
#             element = WebDriverWait(driver, 20).until(
#                 EC.presence_of_element_located((By.ID, "table"))
#             )
#             table = driver.find_element(By.ID,"table")
#         except TimeoutError:
#             print("Error: Table not found on {url} level 5")
#             element = WebDriverWait(driver, 20).until(
#                 EC.presence_of_element_located((By.CSS_SELECTOR, "#table"))
#             )
#             table = driver.find_element(By.CSS_SELECTOR,"#table")

#         # get the table
#         try:
#             df = pd.read_html(table.get_attribute('outerHTML'))[0] # or df = pd.read_html(table.get_attribute('innerHTML'))[0]
#         except Exception as e:
#             logging.error(e)
#             print("Error: Table not found on {url} level 6")
#             try:
#                 df = pd.read_html(table.get_attribute('innerHTML'))[0]
#             except Exception as e:
#                 logging.error(e)
#                 print("Error: Table not found on {url} level 7")

#         df.to_csv('layoffs.csv', index=False)
#         print(f"{'layoffs.csv'} updated with data from {url}")

#     except TimeoutError:
#         print(f"Error: Table not found on {url}")

#     finally:
#         driver.quit()



if __name__ == "__main__":
    run_job() # Run the job once when the script is run