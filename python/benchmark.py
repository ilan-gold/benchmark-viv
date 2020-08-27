from selenium import webdriver
from selenium.common.exceptions import WebDriverException
import chromedriver_binary

import os

# Image sources.

TEST_IMAGE_GCS = (
    "https://viv-demo.storage.googleapis.com/Vanderbilt-Spraggins-Kidney-MxIF.ome.tif"
)
TEST_IMAGE_S3 = "https://s3.amazonaws.com/vitessce-data/test-data/Vanderbilt-Spraggins-Kidney-MxIF.ome.tif"


def run_benchmark():
    options = webdriver.ChromeOptions()
    options.add_argument(
        "--disable-infobars --disable-extensions --window-size=1366,768"
    )
    options.add_experimental_option("detach", True)
    driver = webdriver.Chrome(chrome_options=options)

    full_path = os.path.abspath("../js/dist/index.html")
    driver.get(f"localhost:9000/?image_url={TEST_IMAGE_GCS}")


if __name__ == "__main__":
    run_benchmark()
