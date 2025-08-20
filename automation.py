import time
import random
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, WebDriverException

def post_review(account, proxy, review_data, status_callback):
    """
    Automate posting a Google review.
    :param account: dict with 'username' and 'password'
    :param proxy: proxy string (IP:Port)
    :param review_data: dict with 'url', 'rating', 'review_text'
    :param status_callback: function for status updates, takes (status_text)
    :return: True if posted, False otherwise
    """
    driver = None
    try:
        chrome_options = webdriver.ChromeOptions()
        if proxy:
            chrome_options.add_argument(f'--proxy-server={proxy}')
        chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        # Uncomment below to run headless
        # chrome_options.add_argument('--headless')
        
        driver = webdriver.Chrome(options=chrome_options)
        wait = WebDriverWait(driver, 20)

        status_callback("Logging in...")
        driver.get("https://accounts.google.com/")

        # Username
        user_field = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="identifierId"]')))
        user_field.send_keys(account["username"])
        driver.find_element(By.XPATH, '//*[@id="identifierNext"]/div/button').click()
        time.sleep(random.uniform(2, 4))

        # Password
        pass_field = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="password"]/div[1]/div/div[1]/input')))
        pass_field.send_keys(account["password"])
        driver.find_element(By.XPATH, '//*[@id="passwordNext"]/div/button').click()
        time.sleep(random.uniform(5, 8))

        # Navigate to business URL
        status_callback("Navigating...")
        driver.get(review_data["url"])

        # Write a review
        write_review_button = wait.until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, 'button[aria-label*="Write a review"]'))
        )
        write_review_button.click()

        # Select star rating
        status_callback("Writing review...")
        star_xpath = f"//button[starts-with(@aria-label, '{review_data['rating']} star')]"
        star_button = wait.until(EC.element_to_be_clickable((By.XPATH, star_xpath)))
        star_button.click()
        time.sleep(random.uniform(1, 2))

        # Enter review text
        review_textarea = wait.until(EC.element_to_be_clickable((By.TAG_NAME, 'textarea')))
        review_textarea.send_keys(review_data["review_text"])
        time.sleep(random.uniform(1, 2))

        # Post
        post_button = driver.find_element(By.XPATH, "//button[span[text()='Post']]")
        post_button.click()

        status_callback("Posted")
        return True

    except (TimeoutException, NoSuchElementException, WebDriverException) as e:
        status_callback(f"Failed: {e}")
        return False

    finally:
        if driver:
            driver.quit()