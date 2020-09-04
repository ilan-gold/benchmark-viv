setTimeout(function () {
  chrome.devtools.network.getHAR(function (harLog) {
    // Chreate a har log object.
    const updatedHarLog = {};
    updatedHarLog.log = harLog;

    // Make it into a blob/url for downloading.
    const harBLOB = new Blob([JSON.stringify(updatedHarLog, null, 2)], {
      type: "application/json",
    });

    const url = URL.createObjectURL(harBLOB);

    // Get the current tab to name the file and download it to the ../../../results folder.
    chrome.tabs.query({ active: true, lastFocusedWindow: true }, tabs => {
      const docUrl = new URL(tabs[0].url);
      const [name] = docUrl.searchParams.get("image_url").split('/').slice(-1);
      const { httpVersion } = updatedHarLog.log.entries[0].request
      chrome.downloads.download({
        url: url,
        filename: `har_file_${name}_${httpVersion === 'HTTP/1.1' ? 'http1' : 'http2'}.json`,
      });
    })
    
  });
// This is a reasonable number for the automated process to finish.
}, 40000)