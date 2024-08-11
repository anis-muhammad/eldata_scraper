import time
from selenium.webdriver.common.by import By
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from urllib.parse import quote_plus

def driverInitialize():
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_experimental_option("excludeSwitches",["enable-automation"])
    chrome_options.add_argument("--statrt-maximized")
    chrome_options.add_argument("--no-sendbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-notifications")
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument("--dns-prefetch-disable")
    chrome_options.add_argument('ignore-certificate-errors')
    # prefs = {"profile.managed_default_content_settings.images":2}
    # chrome_options.add_experimental_option("prefs",prefs)
    #driver=webdriver.Chrome(ChromeDriverManager().install(),options=chrome_options)
    driver=webdriver.Chrome(options=chrome_options)
    driver.set_page_load_timeout(500)
    return driver  

def searchGoogle(query, driver):
    search_url = f"https://www.google.com/search?q={quote_plus(query)}"
    driver.get(search_url)
    time.sleep(2)  # Wait for the page to load
    search_results = driver.find_elements(By.CSS_SELECTOR, 'a')
    
    urls = []
    for result in search_results:
        href = result.get_attribute('href')
        if href:
            urls.append(href)
    
    return urls

def extract_url(driver, xpath):
    try:
        return driver.find_element(By.XPATH, xpath).get_attribute('href')
    except:
        return None

def scraper():
    driver = driverInitialize()
    
    # Read processed URLs
    try:
        with open('processed_urls.txt', 'r') as processed_file:
            processed_urls = set(url.strip() for url in processed_file.readlines())
    except FileNotFoundError:
        processed_urls = set()
    
    with open('weblinks.txt', 'r') as file:
        urls = file.readlines()
    
    with open('processed_urls.txt', 'a') as processed_file:
        for url in urls:
            url = url.strip()  # Remove leading/trailing whitespace and newlines
            if url and url not in processed_urls:  # Check if URL is not empty and not processed
                print(f"Processing URL: {url}")
                try:
                    driver.get(url)
                    time.sleep(2)
                    
                    website_link = ''
                    address1 = ''
                    address2 = ''
                    business_Name = ''

                    try:
                        website_link = driver.find_element(By.XPATH, "//a[contains(text(),'Ver página web')]").get_attribute('href')
                        print(f"Website link found: {website_link}")
                    except:
                        try:
                            website_link = driver.find_element(By.XPATH, '//a[@class="web-address-link"]').get_attribute('href')
                            print(f"Website link found with second XPath: {website_link}")
                        except:
                            try:
                                website_link = driver.find_element(By.XPATH, '//a[@data-asoch-targets="landing_page,landing_page_clk"]').get_attribute('href')
                                print(f"Website link found with third XPath: {website_link}")
                            except:
                                print('Website link not found with any XPath')
                    
                    try:
                        address1 = driver.find_element(By.XPATH, '//span[@class="business-address"]').get_attribute('innerText')
                        print(f"address1 found: {address1}")
                    except:
                        print(f"address1 not found")
                    
                    try:
                        address2 = driver.find_element(By.XPATH, '//div[@class="place-name"]').get_attribute('innerText')
                        print(f"address2 found: {address2}")
                    except:
                        print(f"address2 not found")

                    try:
                        business_Name = driver.find_element(By.XPATH, '//h1[@class="detail-headline"]').get_attribute('innerText')
                        print(f"business_Name found: {business_Name}")
                    except:
                        print(f"business_Name not found")

                    # Mark this URL as processed
                    processed_file.write(url + '\n')
                    processed_file.flush()

                    # If website link not found, perform Google searches
                    if not website_link and business_Name:
                        # Define XPaths for each social media site
                        xpath_dict = {
                            'facebook': '//div[@id="rso"]/div[5]//span//a',
                            'instagram': '//div[@id="rso"]/div[5]//span//a',
                            'youtube': '//div[@id="rso"]/div//span//a',
                            'linkedin': '//div[@id="rso"]/div[1]//span//a',
                            'website_url' : '//div[@id="rso"]//div[1]//span//a'
                        }
                        
                        for site in ['facebook', 'instagram', 'youtube', 'linkedin', 'website_url']:
                            search_query = f'{business_Name} @{site}'
                            urls = searchGoogle(search_query, driver)
                            time.sleep(2)
                            
                            # Use the site name to get the correct XPath
                            xpath = xpath_dict.get(site)
                            url = extract_url(driver, xpath)
                            
                            if url:
                                print(f"{site} found: {url}")
                            else:
                                print(f"{site} not found")
                            
                            print(f"Searching for: {search_query}")
                            # print(f"Google search URLs: {urls}")

                except Exception as e:
                    print(f"Error processing URL {url}: {e}")
    
    driver.quit()

scraper()
