from config import settings
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException


def get_page_source_urls() -> str:
    """
    Retrieves the page source of the main restaurant listing page, clicking the "meer laden" (load more) button until all results are loaded.

    Returns:
        str: The HTML source of the fully loaded restaurant listing page.
    """
    cService = webdriver.ChromeService(executable_path=settings.CHROMEDRIVE_PATH)
    driver = webdriver.Chrome(service=cService)
    
    driver.get(settings.RESTAURANT_URL)
    
    try:
        driver.find_element(By.ID, "CybotCookiebotDialogBodyLevelButtonLevelOptinAllowAll").click()
    except NoSuchElementException:
        pass

    while True:
        try:
            driver.find_element(By.CLASS_NAME, "meerladen").click()
            time.sleep(1)
        except NoSuchElementException:
            break
    
    page_source = driver.page_source

    driver.quit()

    return page_source

def get_page_source_restaurant(url: str) -> str:
    """
    Retrieves the page source of an individual restaurant page in headless mode without images and other unnecessary content.

    Args:
        url (str): URL path of the restaurant page (relative to the BASE_URL).

    Returns:
        str: The HTML source of the restaurant page.
    """
    options = webdriver.ChromeOptions()
    cService = webdriver.ChromeService(executable_path=settings.CHROMEDRIVE_PATH)

    prefs = {
        'profile.default_content_setting_values': {
            'images': 2
        },
    }
    options.add_experimental_option('prefs', prefs)
    options.add_argument("start-maximized")
    options.add_argument("disable-infobars")
    options.add_argument("--disable-extensions")
    options.add_argument("--disable-popup-blocking")
    options.add_argument('--headless')
    driver = webdriver.Chrome(
            service=cService,
            options=options
    )
    driver.get(settings.BASE_URL + url)

    page_source = driver.page_source

    driver.quit()

    return page_source