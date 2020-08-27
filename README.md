# Benchmarking Viv

This is a piece of software for automatically benchmarking Viv. It uses `python` and `selenium` to run tests and a minimal setup of `viv` layers + loaders to do the client-side testing. You may need to update Chrome for this to work - open Chrome
and navigate to "About Google Chrome."

### Usage

```bash
./run-benchmark.sh
```

### Benchmarking

So far, we have a list at the top of `js/App.js` called `transitionViewStates` that contains a list of objects like `{ target, zoom, transitionDuration }` specifiying where to transition to and how quickly. For now both `zoom` and `target` are interpolated but that can change.

We can check how long it takes all tiles to load by looking at our network tab on our browser. So, far GCS and S3 (the two image sources) are comparable, but to do this benchmarking properly regarding HTTP vs HTTP2, we need to spin up our servers.
