import time,pandas
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common import NoSuchElementException

# Checking runtime
initial = time.time()

# Set up web driver
service = Service(ChromeDriverManager().install())
chrome_options = webdriver.ChromeOptions()
chrome_options.add_experimental_option("detach",True)
chrome_options.add_argument("--start-maximized")
driver = webdriver.Chrome(options=chrome_options,service=service)
driver.get(url="https://www.amazon.in/s?rh=n%3A6612025031&fs=true&ref=lp_6612025031_sar")

# Temporary Dictionary
details_dic={
    "title" : [],
    "price" : [],
    "rating": [],
    "seller_name": [],
}
page_count = 1

# Repeat after page change
while page_count < 3:

    # initial loading wait
    time.sleep(2)
    # Bypass Response 503
    driver.refresh()
    # Get Details
    all_products = driver.find_elements(By.XPATH,value='//*[@data-component-type="s-search-result"]//div[@data-cy="asin-faceout-container"]//div[@class="a-section a-spacing-small puis-padding-left-small puis-padding-right-small"]')
    time.sleep(2)


    for product in all_products:
        product_found=page_exists = True

        # Check if in Stock
        try:
            price = product.find_element(By.XPATH,value='.//div[@data-cy="price-recipe"]//a[@class="a-link-normal s-no-hover s-underline-text s-underline-link-text s-link-style a-text-normal"]//span[@class="a-price-whole"]').text
        except NoSuchElementException:
            product_found = False

        # Get details when in Stock
        if product_found:
            title = product.find_element(By.XPATH,value='.//h2[@class="a-size-mini a-spacing-none a-color-base s-line-clamp-4"]//span').text
            rating = product.find_element(By.XPATH,value='.//div[@data-cy="reviews-block"]/div/span').get_attribute('aria-label')[:3]
            # Get page link
            product_link = product.find_element(By.LINK_TEXT,value=title).get_attribute("href")

            # Open product page for seller name
            driver.execute_script("window.open(arguments[0]);", product_link)
            driver.switch_to.window(driver.window_handles[1])

            time.sleep(2)

            # Check page validity
            try:
                logo_404 = driver.find_element(By.XPATH,value='//a[@href="ref=cs_404_logo"]')

            except NoSuchElementException:
                # Get seller name
                seller_name = driver.find_element(By.ID,value='sellerProfileTriggerId').text
            else:
                page_exists = False

            # Enter Details only when page is valid
            if page_exists:
                # insert data into dictionary
                details_dic['title'].append(title)
                details_dic['price'].append(price)
                details_dic['rating'].append(rating)
                details_dic['seller_name'].append(seller_name)

            # close window and move to next
            driver.close()
            driver.switch_to.window(driver.window_handles[0])

    # Change page once done
    page_count += 1
    driver.find_element(By.XPATH,value='/html/body/div[1]/div[1]/div[1]/div[1]/div/span[1]/div[1]/div[35]/div/div/span/a[3]').click()

# Convert Dictionary to DataFrame
details_df = pandas.DataFrame(details_dic)
# Convert DataFrame to csv
details_df.to_csv("scrape.csv",index=False)

print(f"Completed in {time.time() - initial}s")