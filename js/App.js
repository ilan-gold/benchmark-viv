import React, { useState, useEffect, useCallback } from "react";
import ReactDOM from "react-dom";

import DeckGL, { OrthographicView, LinearInterpolator } from "deck.gl";
import { MultiscaleImageLayer, createOMETiffLoader, createBioformatsZarrLoader } from "@hms-dbmi/viv";

// Interpolator.  We can turn off and on what gets interpolated.
const transitionInterpolator = new LinearInterpolator(["target", "zoom"]);

// Different view states and the transitions between them to interpolate.
const transitionViewStates = [
  {
    target: [20000, 20000, 0],
    zoom: 0,
    transitionDuration: 10000,
  },
  {
    target: [10000, 30000, 0],
    zoom: -5,
    transitionDuration: 4000,
  },
  {
    target: [25000, 10000, 0],
    zoom: 1,
    transitionDuration: 6000,
  },
];

const url = new URL(document.location);

export default function App() {
  const [loader, setLoader] = useState(null);
  const [initialViewState, setInitialViewState] = useState({
    target: [13000, 13000, 0],
    zoom: -7,
  });

  const goToPoint = useCallback(() => {
    let total = 0;
    transitionViewStates.forEach((transition) => {
      const { transitionDuration } = transition;
      setTimeout(function () {
        setInitialViewState({
          transitionInterpolator,
          ...transition,
        });
      }, total);
      total += transitionDuration;
    });
  }, []);

  useEffect(() => {
    const getLoader = async () => {
      const imageUrl = url.searchParams.get("image_url")
      const newLoader = imageUrl.includes('ome.tif') ? await createOMETiffLoader({
        url: imageUrl,
        offsets: [],
      }) : await createBioformatsZarrLoader({ url: imageUrl });
      setLoader(newLoader);
    };
    getLoader();
  }, []);

  const imageLayer =
    loader &&
    new MultiscaleImageLayer({
      loader,
      id: "image-layer",
      // These are pretty arbitrary - four channels is standard though.
      // We may want to make the number of channels a URL parameter as well.
      loaderSelection: [
        { channel: 0 },
        { channel: 1 },
        { channel: 2 },
        { channel: 3 },
      ],
      colorValues: [
        [0, 255, 0],
        [0, 0, 255],
        [0, 255, 255],
        [255, 255, 0],
      ],
      sliderValues: [
        [1500, 20000],
        [1500, 20000],
        [1500, 20000],
        [1500, 20000],
      ],
      channelIsOn: [true, true, true, true],
      opacity: 1,
    });

  return (
    <div>
      <DeckGL
        views={[new OrthographicView({ id: "ortho" })]}
        layers={[imageLayer]}
        initialViewState={initialViewState}
        controller={true}
        onLoad={goToPoint}
      />
    </div>
  );
}

ReactDOM.render(<App />, document.getElementById("app"));
