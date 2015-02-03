!setTimeout(function() {
  function collect(callback) {
    var html = document.documentElement.outerHTML;
    var data = new FormData();
    data.append('url', document.location.href);
    data.append('html', html);
    var req;
    if (window.XMLHttpRequest) {
        req = new XMLHttpRequest();
    } else if (window.ActiveXObject) {
        req = new ActiveXObject("Microsoft.XMLHTTP");
    } else {
      console.warn("Unable to XHR");
      return;
    }
    req.open('POST', 'http://localhost:9000/collector/', true);
    req.onreadystatechange = function (response) {
      if (req.readyState === 4) {
        if (req.status === 200) {
          console.log("We have already collected this HTML");
          callback(false);
        } else if (req.status === 201) {
          console.log("Yum! Collected another chunk of HTML");
          callback(true);
        } else {
          console.warn("Failed to collect the HTML of this page");
        }
      }
    };
    req.send(data);

  }

  var interval = 3;
  var timer;
  function loop() {
    collect(function(newhtml) {
      interval *= newhtml && .5 || 2;
      timer = setTimeout(loop, interval * 1000);
    });
  }
  loop();

}, 1.5 * 1000);
