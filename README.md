# Benchmarking Viv

This is a piece of software for automatically benchmarking Viv. It uses [Selenium](https://selenium-python.readthedocs.io/) to run tests and a minimal setup of [Viv](http://viv.gehlenborglab.org/) `layers` + `loaders` to do the client-side testing. You may need to update Chrome for this to work - open Chrome and navigate to "About Google Chrome" where you should see an option to automatically update. This is due to the [`chromedriver-binary`](https://pypi.org/project/chromedriver-binary/) version needing to match your browser version, so this could be a pain-point going forward.

The results of this test are captured using the proxy utility [BrowserMob Proxy](https://bmp.lightbody.net/) - the [HAR file](https://toolbox.googleapps.com/apps/har_analyzer/) is dumped as `JSON` into the `results` folder (and will need to be parsed).

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


#### Tasks
- tilesize vs. viewport size:
  - `tilesizes`: 256x256, 512x512, 1024x1024 
  - `viewport sizes`: (375x812) - iPhone X, (768x1024) - iPad, (1280x800) Macbook Pro retina, (1920x1080) large [more info](https://mediag.com/blog/popular-screen-resolutions-designing-for-all/).
  - Expected results: larger tiles for bigger displays will generally be better; smaller tiles faster to load.
- number of channels (1-6):
  - Expected results: fewer channels, faster loading.
- HTTP1 vs HTTP2.
  - Toggle on and off HTTP1/2 clientside for 1.) GCS bucket, 2.) Custom server supporting HTTP/2.
  - Expected results: likely doesn't matter for commercial storage; substantially better for in house server.
- Local vs Remote:
  - Probably just for TIFF. 
  - Expected results: local is much faster (I'm not sure we need to show this).
  
 
