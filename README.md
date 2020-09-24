# Benchmarking Viv

This is a piece of software for automatically benchmarking Viv. It uses [Selenium](https://selenium-python.readthedocs.io/) to run tests and a minimal setup of [Viv](http://viv.gehlenborglab.org/) `layers` + `loaders` to do the client-side testing. You may need to update Chrome for this to work - open Chrome and navigate to "About Google Chrome" where you should see an option to automatically update. This is due to the [`chromedriver-binary`](https://pypi.org/project/chromedriver-binary/) version needing to match your browser version, so this could be a pain-point going forward.

The results of this test are captured using a browser extension built out of `js/har_extension` that downloads a HAR file parsed as json into the `results` folder.
This folder is cleared out on every run of the benchmarking script.

In order to turn off http2, you can route requests through [BrowserMob Proxy](https://bmp.lightbody.net/) which does not support http2.  You can then either use or not use BMP to capture the requests.  These are configurable via the `use_bmp_http1` and `capture_har_with_bmp` parameters in the `image_test_files.json` file, respectively. 

It **seems** that BMP does not actually record requests blocking, which is problematic and probably means it's not a good idea to use it.  Nonetheless, the option is still there.

### Usage

You need `python3` installed in your path as well as `npm`/`node`.

To run the benchmarking and install any dependencies you may need (beyond the above two):

```bash
./run-benchmark.sh
```

### Benchmarking

So far, we have a list at the top of `js/App.js` called `transitionViewStates` that contains a list of objects like `{ target, zoom, transitionDuration }` specifiying where to transition to and how quickly. For now both `zoom` and `target` are interpolated but that can change so that only one is interpolated at a time.

### Data

Right now only the standard Vanderbilt MxIF Kidney OME-ITFF images are used (tile size 512), with one copy on s3 and GCS. Eventually, we will want to test different tile sizes, file formats (i.e Zarr), local and remote files, number of channels, screen size (mobile vs browser), and all the combinations (on both HTTP and HTTP2).

To generate data and push it to the cloud, please see the `data` folder.

### Deployment

To deploy servers to benchmark against, see the `deployment` folder.
