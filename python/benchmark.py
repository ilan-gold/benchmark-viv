from selenium import webdriver
from selenium.common.exceptions import WebDriverException
import chromedriver_binary

import os


def run_benchmark():
    options = webdriver.ChromeOptions()
    options.add_argument(
        "--disable-infobars --disable-extensions --window-size=1366,768"
    )
    options.add_experimental_option("detach", True)
    driver = webdriver.Chrome(chrome_options=options)

    full_path = os.path.abspath("../js/dist/index.html")
    driver.get(f"file://{full_path}")


if __name__ == "__main__":
    run_benchmark()
