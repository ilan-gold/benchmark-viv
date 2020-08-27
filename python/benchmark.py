from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
import chromedriver_binary
from browsermobproxy import Server

import os
import time
from urllib.parse import urlparse
import json
import psutil

# Image sources.

TEST_IMAGE_GCS = {
    "name": "gcs_http2_vanderbilt",
    "url": "https://viv-demo.storage.googleapis.com/Vanderbilt-Spraggins-Kidney-MxIF.ome.tif",
}

TEST_IMAGE_S3 = {
    "name": "s3_http_vanderbilt",
    "url": "https://s3.amazonaws.com/vitessce-data/test-data/Vanderbilt-Spraggins-Kidney-MxIF.ome.tif",
}
TEST_IMAGES = [TEST_IMAGE_GCS, TEST_IMAGE_S3]


def run_benchmark():

    # Check whether there are browsermob processes and end them.
    for proc in psutil.process_iter():
        cmd = []
        try:
            cmd = proc.cmdline()
        except:
            continue
        if any(["browsermob-proxy" in arg for arg in cmd]):
            proc.kill()

    # There seems to be an issue where starting up the server immediately after ending the old processes is problematic.
    time.sleep(1)

    # Start up the proxy server to record the traffic.
    server = Server("./browsermob-proxy-2.1.4/bin/browsermob-proxy")
    server.start()
    proxy = server.create_proxy()

    # Set up browser to launch.
    options = webdriver.ChromeOptions()
    options.add_argument(
        "--disable-infobars --disable-extensions --window-size=1366,768"
    )
    # The proxy doesn't work with ssl/https.
    options.add_argument("--ignore-certificate-errors")
    proxy_url = urlparse(proxy.proxy).path
    options.add_argument("--proxy-server={0}".format(proxy_url))
    driver = webdriver.Chrome(chrome_options=options)

    # Run tests.
    for image in TEST_IMAGES:
        url = image["url"]
        name = image["name"]
        # Set up har download (i.e the log of traffic) and launch webpage for testing the current image.
        proxy.new_har(
            f"localhost:9000/?image_url={url}",
            options={"captureHeaders": True, "captureContent": True},
        )
        driver.get(f"localhost:9000/?image_url={url}")
        # This should be more than enough for the test to complete.
        time.sleep(40)

        # Dump the results of the test.
        os.makedirs("results", exist_ok=True)
        with open(f"results/{name}.json", "w+") as f:
            f.write(json.dumps(proxy.har, ensure_ascii=False))

    # Clean up.
    server.stop()
    driver.quit()


if __name__ == "__main__":
    run_benchmark()
