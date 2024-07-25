import csv
import time
import random
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import undetected_chromedriver as uc

proxies = [
    # Add your Proxies here...
]

user_agents = [
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36 Midori/9.0",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36 Brave/91.1.26.67",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36 Vivaldi/4.0",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Ubuntu Chromium/91.0.4472.77 Chrome/91.0.4472.77 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.93 Safari/537.36 Edg/90.0.818.51",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36 OPR/76.0.4017.177",
    "Mozilla/5.0 (X11; Linux x86_64; rv:89.0) Gecko/20100101 Firefox/89.0",
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.5060.53 Safari/537.36',
]

def get_webdriver(browser, headless=True):
    if browser == "chrome":
        options = webdriver.ChromeOptions()
        if headless:
            options.add_argument('--headless')
        options.add_argument('--proxy-server=%s' % random.choice(proxies))
        options.add_argument('user-agent=%s' % random.choice(user_agents))
        driver = webdriver.Chrome(options=options)
    elif browser == "firefox":
        options = webdriver.FirefoxOptions()
        if headless:
            options.add_argument('--headless')
        options.add_argument('--proxy-server=%s' % random.choice(proxies))
        options.set_preference("general.useragent.override", random.choice(user_agents))
        driver = webdriver.Firefox(options=options)
    elif browser == "edge":
        options = webdriver.EdgeOptions()
        if headless:
            options.add_argument('--headless')
        options.add_argument('--proxy-server=%s' % random.choice(proxies))
        options.add_argument('user-agent=%s' % random.choice(user_agents))
        driver = webdriver.Edge(options=options)
    elif browser == "undetected_chrome":
        options = uc.ChromeOptions()
        if headless:
            options.add_argument('--headless')
        options.add_argument('--proxy-server=%s' % random.choice(proxies))
        options.add_argument('user-agent=%s' % random.choice(user_agents))
        driver = uc.Chrome(options=options)
    else:
        raise ValueError("Unsupported browser")
    return driver

def human_like_delay(min_time=1, max_time=3):
    time.sleep(random.uniform(min_time, max_time))

def extract_bing_info(email, browser, headless=True):
    driver = get_webdriver(browser, headless)
    
    driver.get("https://www.bing.com")
    time.sleep(1)
    search_box = driver.find_element(By.ID, 'sb_form_q')
    search_query = f"{email} site:linkedin.com/in"
    search_box.send_keys(search_query)
    human_like_delay()
    search_box.send_keys(Keys.ENTER)
    time.sleep(1)

    wait = WebDriverWait(driver, 10)
    linkedin_profile = {'email': email, 'name': '', 'company': '', 'url': ''}

    try:
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'li.b_algo')))
        search_result = driver.find_element(By.CSS_SELECTOR, 'li.b_algo')
        
        name_element = search_result.find_element(By.CSS_SELECTOR, 'h2')
        linkedin_profile['name'] = name_element.text.split("-")[0].strip()
        linkedin_profile['company'] = name_element.text.split("-")[1].strip() if len(name_element.text.split("-")) > 1 else ''
        
        link_element = search_result.find_element(By.CSS_SELECTOR, 'h2 a')
        linkedin_profile['url'] = link_element.get_attribute('href')
    except Exception as e:
        print(f"No data found for {email}. Exception: {e}")

    driver.quit()
    return linkedin_profile

input_csv = 'emailstest.csv'  # Path to the input CSV file
output_csv = 'linkedin_profiles_bing.csv'  # Path to the output CSV file

# List of browsers to switch between
browsers = ["firefox", "chrome", "edge", "undetected_chrome"]
browser_index = 0  # Initialize browser index

with open(input_csv, mode='r', newline='', encoding='utf-8') as infile, \
     open(output_csv, mode='a', newline='', encoding='utf-8') as outfile:

    reader = csv.DictReader(infile)
    writer = csv.DictWriter(outfile, fieldnames=['id', 'email', 'name', 'company', 'url'])
    outfile.seek(0, 2)  # Move to the end of the file
    if outfile.tell() == 0:
        writer.writeheader()

    processed_emails = {row['email'] for row in csv.DictReader(open(output_csv))}

    for row in reader:
        if row['email'] in processed_emails:
            continue  # Skip already processed emails

        # Sequentially select a browser for each request
        browser = browsers[browser_index]
        data = extract_bing_info(row['email'], browser, headless=False)  # Set headless=True to run headless
        writer.writerow({'id': row['id'], 'email': row['email'], 'name': data['name'], 'company': data['company'], 'url': data['url']})
        print(f"Processed: ID: {row['id']}, Email: {row['email']}, Name: {data['name']}, Company: {data['company']}, URL: {data['url']}")
        
        # Switch to the next browser
        browser_index = (browser_index + 1) % len(browsers)
        
        # Introduce random delay between requests
        human_like_delay(5, 10)