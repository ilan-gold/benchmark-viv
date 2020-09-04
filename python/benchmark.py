from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
import chromedriver_binary

import os
import time
from urllib.parse import urlparse
import json
import psutil
import shutil

# Image sources.
TEST_IMAGE_GCS_HTTP2 = {
    "name": "gcs_http2_vanderbilt",
    "url": "https://viv-demo.storage.googleapis.com/Vanderbilt-Spraggins-Kidney-MxIF.ome.tif",
    "use_http2": True,
}

TEST_IMAGE_GCS_HTTP1 = {
    "name": "gcs_http2_vanderbilt",
    "url": "https://viv-demo.storage.googleapis.com/Vanderbilt-Spraggins-Kidney-MxIF.ome.tif",
    "use_http2": False,
}

TEST_IMAGES = [TEST_IMAGE_GCS_HTTP1, TEST_IMAGE_GCS_HTTP2]

# Top level directory for results.
RESULTS_DIR = "../results/"


def end_daemon_chrome_processes():

    for proc in psutil.process_iter():
        cmd = []
        try:
            # The name of the proc is just "java" or something so this is more robust.
            cmd = proc.cmdline()
        except:
            continue
        if any(["chrome" in arg or "Chrome" in arg for arg in cmd]):
            proc.kill()


def start_chrome(use_http2):

    # Set up browser to launch.
    options = webdriver.ChromeOptions()
    options.add_argument(
        f"--disable-infobars --disable-extensions --window-size=1900,900 {'--disable-http2' if not use_http2 else ''}"
    )
    options.add_argument("--auto-open-devtools-for-tabs")
    options.add_extension("../js/har_extension.crx")
    prefs = {"download.default_directory": os.path.abspath(RESULTS_DIR)}
    options.add_experimental_option("prefs", prefs)
    driver = webdriver.Chrome(options=options)
    return driver


def log_results(image):

    url = image["url"]
    name = image["name"]
    use_http2 = image["use_http2"]

    # Get the har file, named after the file name fetched and the protocol (see background.js)
    har_json_file = (
        f"har_file_{url.split('/')[-1]}_{'http1' if not use_http2 else 'http2'}.json"
    )
    with open(RESULTS_DIR + har_json_file, "r") as f:
        har_log = json.loads(f.read())["log"]

    # Get the entries for the requests to the image.
    image_entries = [
        entry for entry in har_log["entries"] if entry["request"]["url"] == url
    ]

    # Get the timings in detail
    image_timings = [entry["timings"] for entry in image_entries]
    print(f"***** TIMINGS FOR {url} {'http1' if not use_http2 else 'http2'} *******")

    # Print each kind of timing and the total/average.
    print("Total time spent waiting: ", sum([entry["time"] for entry in image_entries]))
    print(
        "Average time spent waiting: ",
        sum([entry["time"] for entry in image_entries]) / len(image_entries),
    )
    for val in image_timings[0].keys():
        print(
            f"Time spent {val}: ",
            sum([timing[val] for timing in image_timings if timing[val] > 0]),
        )
    print("*******************************************")


def run_test(image):

    url = image["url"]
    name = image["name"]
    use_http2 = image["use_http2"]

    driver = start_chrome(use_http2)
    driver.get(f"localhost:9000/?image_url={url}")

    # This should be more than enough for the test to complete and the har to download.
    # It is 10 seconds longer than when the har download starts.
    time.sleep(50)

    # Clean up.
    driver.quit()


def run_benchmark():

    # Clear out previous results.
    shutil.rmtree(RESULTS_DIR)

    for image in TEST_IMAGES:
        end_daemon_chrome_processes()

        # Run tests and log results.
        run_test(image)
        log_results(image)

        end_daemon_chrome_processes()


if __name__ == "__main__":
    run_benchmark()
