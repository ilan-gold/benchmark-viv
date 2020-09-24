from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
import chromedriver_binary
from browsermobproxy import Server

import os
import time
from urllib.parse import urlparse
import json
import psutil
import shutil

# Top level directory for results.
RESULTS_DIR = "../results/"
# Change to true in order to use BMP
USE_BMP_HTTP1 = False
CAPTURE_HAR_WITH_BMP = False


def make_har_json_name(url, is_http2):
    return f"har_file_{url.split('/')[-1]}_{'http1' if not is_http2 else 'http2'}.json"

def end_daemon_processes():

    for proc in psutil.process_iter():
        cmd = []
        try:
            # The name of the proc is just "java" or something so this is more robust.
            cmd = proc.cmdline()
        except:
            continue
        if any(["chrome" in arg or "Chrome" in arg or "browsermob-proxy" in arg for arg in cmd]):
            proc.kill()
    time.sleep(1)

def start_proxy_server():
    # Unzipped library from `run-benchmark.sh`.
    server = Server("./browsermob-proxy-2.1.4/bin/browsermob-proxy")
    server.start()
    proxy = server.create_proxy()
    return (server, proxy)

def start_chrome(is_http2, proxy_url, use_bmp_http1, capture_har_with_bmp):

    # Set up browser to launch.
    options = webdriver.ChromeOptions()
    options.add_argument(
        "--disable-infobars --disable-extensions"
    )
    # Our servers use self-signing certificates (in the interest of not dealing with a CA).
    options.add_argument("--ignore-certificate-errors")
    if not is_http2 and use_bmp_http1:
        options.add_argument(f"--proxy-server={proxy_url}")
    if not capture_har_with_bmp:
        options.add_extension("../js/har_extension.crx")
    options.add_argument("--auto-open-devtools-for-tabs")
    prefs = {"download.default_directory": os.path.abspath(RESULTS_DIR)}
    options.add_experimental_option("prefs", prefs)
    driver = webdriver.Chrome(options=options)
    driver.set_window_size(1920,1080)
    return driver


def log_results(image):

    url = image["url"]
    is_http2 = image["is_http2"]
    capture_har_with_bmp = image["capture_har_with_bmp"]

    # Get the har file, named after the file name fetched and the protocol (see background.js)
    har_json_file = make_har_json_name(url, is_http2)

    with open(RESULTS_DIR + har_json_file, "r") as f:
        har_log = json.loads(f.read())["log"]

    # Get the entries for the requests to the image.
    image_entries = [
        entry for entry in har_log["entries"] if url in entry["request"]["url"]
    ]

    # Get the timings in detail
    image_timings = [entry["timings"] for entry in image_entries]
    print(f"***** TIMINGS FOR {url} {'http1' if not is_http2 else 'http2'} {'captured with BMP' if capture_har_with_bmp else ''} *******")

    # Print each kind of timing and the total/average.
    print("Total time spent waiting: ", sum([entry["time"] for entry in image_entries]))
    print(
        "Average time spent waiting: ",
        sum([entry["time"] for entry in image_entries]) / len(image_entries),
    )
    for val in image_timings[0].keys():
        print(
            f"Time spent {val}: ",
            sum([timing[val] for timing in image_timings if type(timing[val]) != str and timing[val] > 0]),
        )
    print("*******************************************")


def run_test(image):

    url = image["url"]
    is_http2 = image["is_http2"]
    use_bmp_http1 = image["use_bmp_http1"]
    capture_har_with_bmp = image["capture_har_with_bmp"]
    proxy_url = ''
    if use_bmp_http1 or capture_har_with_bmp:
        (server, proxy) = start_proxy_server()
        proxy_url = urlparse(proxy.proxy).path
    driver = start_chrome(is_http2, proxy_url, use_bmp_http1, capture_har_with_bmp)
    if use_bmp_http1 or capture_har_with_bmp:
        proxy.new_har(
            f"localhost:9000/?image_url={url}",
            options={"captureHeaders": True, "captureContent": True},
        )
    driver.get(f"localhost:9000/?image_url={url}")

    # This should be more than enough for the test to complete and the har to download.
    # It is 10 seconds longer than when the har download starts.
    time.sleep(60)

    # After finishing, download results from proxy of har.
    if not is_http2 and use_bmp_http1 and capture_har_with_bmp:
        os.makedirs(RESULTS_DIR, exist_ok=True)
        with open(f"{RESULTS_DIR}/{make_har_json_name(url, is_http2)}", "w+") as f:
            f.write(json.dumps(proxy.har, ensure_ascii=False))

    # Clean up.
    if use_bmp_http1 or capture_har_with_bmp:
        server.stop()
    driver.quit()


def run_benchmark():

    # Clear out previous results.
    if os.path.exists(RESULTS_DIR) and os.path.isdir(RESULTS_DIR):
        shutil.rmtree(RESULTS_DIR)
        
    os.makedirs(RESULTS_DIR, exist_ok=True)
    # Run the test 20 times.
    for i in range(20):
        # Open configuration file.
        with open('../image_test_files.json', 'r') as f:
            images = json.loads(f.read())

        for image in images:
            end_daemon_processes()

            # Run tests and log results.
            run_test(image)
            log_results(image)

            end_daemon_processes()

        # Move these results out of results and start fresh.
        os.makedirs(RESULTS_DIR.replace('results', f'results{str(i)}'), exist_ok=True)
        shutil.move(RESULTS_DIR, RESULTS_DIR.replace('results', f'results{str(i)}'))
        os.makedirs(RESULTS_DIR, exist_ok=True)
        


if __name__ == "__main__":
    run_benchmark()
