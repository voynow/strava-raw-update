import utils.configs as configs
import requests

from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.chrome.options import Options


options = Options()
options.add_argument('--headless')


def create_driver(link=None):
    """
    Create chrome driver, get link if available
    """
    driver = webdriver.Chrome(ChromeDriverManager().install(), chrome_options=options)
    if link:
        driver.get(link)

    return driver


def create_driver_helper():
    """
    Handles Chrome failed to start error
    """
    driver = None
    while driver is None:
        try:
            driver = create_driver()
        except WebDriverException:
            create_driver_helper()
            
    return driver
        

def get_code_from_strava():
    """
    Selenium code to automate access to account authorization for API
    Storing code from URL in configs file, this code is required for oauth API call
    """
    driver = create_driver_helper()
    driver.get(configs.get_oauth_code_param())

    driver.find_element(By.CSS_SELECTOR, f'input#email').send_keys(configs.email)
    driver.find_element(By.CSS_SELECTOR, f'input#password').send_keys(configs.password + Keys.ENTER)

    driver.find_element(By.CLASS_NAME, "btn-primary").click()

    for param in driver.current_url.split("&"):
            if "code" in param:
                    code = param.split("=")[1]
    driver.quit()
    return code


def create_oauth_url():
    """
    Constrct oauth url from configuration data
    """
    code = get_code_from_strava()
    url_data = configs.get_oauth_url(code)
    url_string = url_data['url']

    for k, v in url_data['params'].items():
        url_string += f'{k}={v}&'
    return url_string


def auth():
    """
    Connect to strava api
    """
    oauth_url = create_oauth_url()
    resp = requests.post(oauth_url)

    if resp.status_code == 200:
        return resp
    else:
        raise Exception(f"Oauth request returning invalid status code: {resp.status_code}")


def get_request(access_token, url_suffix):
    """
    Constructs get request to strava api
    """
    return requests.get(
        f'https://www.strava.com/api/v3/{url_suffix}',
        headers={'Authorization': f'Bearer {access_token}'},
        params={'per_page': 200, 'page': 1}
    ).json()


def validate_resp(resp):
    # extract data from nested list
    if isinstance(resp, list):
        if len(resp) == 1:
            resp = resp[0]
    # skip error response from API limit
    if 'message' in resp:
        if resp['message'] == configs.rate_exceeded_message:
            return None
    return resp


def batch_get_request(table, ids, access_token):
    """
    construct list of get urls given table and activty ids
    """
    prefix = configs.activities_base_url
    suffix = configs.activities_endpoints[table]

    data = {}
    for i, idx in enumerate(ids):
        if not (i + 1) % 10:
            print(f"{table}: executing request {i + 1} of {len(ids)}")

        url = f'{prefix}{idx}{suffix}'
        response = validate_resp(get_request(access_token, url))
        if not response:
            print("API Limit Reached, exiting batch get request")
            break

        data[idx] = response
    return data