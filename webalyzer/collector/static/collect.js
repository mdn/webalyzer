var Webalyzer = function(domain, options) {
  options = options || {};
  options.doSend = options.doSend || function(html, url) {
    return true;
  };
  options.beforeSendHTML = options.beforeSendHTML || function(html, url) {
    return html;
  };
  options.server = options.server || 'https://webalyzer.dev/collector/';

  var request = function() {
    if (window.XMLHttpRequest) {
        return new XMLHttpRequest();
    } else if (window.ActiveXObject) {
        return new ActiveXObject("Microsoft.XMLHTTP");
    } else {
      throw "Unable to XHR at all";
    }
  };

  function _postHash(source_hash, type, domain, cb) {
    var req = request();
    req.open('HEAD', options.server + 'check/' + type + '/'+ domain + '/' + source_hash);
    req.onreadystatechange = function (response) {
      if (req.readyState === 4) {
        cb(req.status);
      }
    };
    req.send();
  }

  function _post(data, cb) {
    var req = request();
    req.open('POST', options.server);
    req.onreadystatechange = function (response) {
      if (req.readyState === 4) {
        cb(req.status);
      }
    };
    req.send(data);
  }

  function _getCSS(url, cb) {
    var req = request();
    req.open('GET', url);
    req.onreadystatechange = function(response) {
      if (req.readyState === 4) {
        cb(req.status, req.response);
      }
    };
    req.send();
  }

  function postCSS(url, callback) {
    _getCSS(url, function(status, response) {
      if (status === 200) {
        var source_hash = makeHash(response);

        _postHash(source_hash, 'css', domain, function(status) {
          if(status === 200) {
            console.log('We have already collected CSS matching ' + source_hash);
          } else {
            console.log('Sending CSS.');
            var req = request();
            var data = new FormData();
            data.append('url', url);
            data.append('domain', domain);
            data.append('css', response);
            data.append('source_hash', source_hash);
            _post(data, function(status) {
              if (status === 200) {
                console.log("We have already collected this CSS");
                if (callback) {
                  callback(url, false);
                }
              } else if (status === 201) {
                console.log("Yum! Collected another chunk of CSS");
                if (callback) {
                    callback(url, true);
                }
              } else {
                console.warn("Failed to collect the CSS of this page");
              }
            });
          }
        });
      }
    });
  }

  // hashCode() from http://erlycoder.com/49/javascript-hash-functions-to-convert-string-into-integer-hash-
  function makeHash(source) {
    var hash = 0;
    if (source.length === 0) return hash;
    for (var i = 0; i < source.length; i++) {
        var char = source.charCodeAt(i);
        hash = ((hash<<5)-hash)+char;
        hash = hash & hash; // Convert to 32bit integer
    }
    return hash;
  }

  function postHTML(html, callback) {
    var source_hash = makeHash(html);

    _postHash(source_hash, 'html', domain, function(status) {
        if(status === 200) {
          console.log('We have already collected HTML matching ' + source_hash);
        } else {
          console.log('Sending HTML.');

        var data = new FormData();
        data.append('url', document.location.href);
        data.append('domain', domain);
        data.append('html', html);
        data.append('source_hash', source_hash);
        _post(data, function(status) {
          if (status === 200) {
            console.log("We have already collected this HTML");
            if (callback) {
              callback(false);
            }
          } else if (status === 201) {
            console.log("Yum! Collected another chunk of HTML");
            if (callback) {
              callback(true);
            }
          } else {
            console.warn("Failed to collect the HTML of this page");
          }
        });
      }
    });
  }

  function collect(callback) {
    // send the HTML
    var html = document.documentElement.outerHTML;
    if (!options.doSend(html, document.location.href)) {
      return;
    }
    html = options.beforeSendHTML(html, document.location.href);
    postHTML(html, callback);

    // send the stylesheets
    var collected = JSON.parse(
      sessionStorage.getItem('webalyzedcss' + domain) || '[]'
    );
    var links = document.querySelectorAll('link[rel="stylesheet"]');
    for (var i=0, L=links.length; i < L; i++) {
      var url = links[i].href;
      if (collected.indexOf(url) === -1) {
        postCSS(url, function(url) {
          if (collected.length === 0) {
            console.log(
              "Webalyzer will use sessionStorage to remember which " +
              "stylesheets it has collected. To reset this run: \n\n\t" +
              "sessionStorage.removeItem('webalyzedcss" + domain +"')\n"
            );
          }
          collected.push(url);
          sessionStorage.setItem(
            'webalyzedcss' + domain,
            JSON.stringify(collected)
          );
        });
      }
    }
  }

  var interval = 3;
  var timer;
  function loop() {
    collect(function(newhtml) {
      interval *= newhtml && 0.5 || 2;
      if (!MutationObserver) {
        timer = setTimeout(loop, interval * 1000);
      }
    });
  }
  loop();

  var MutationObserver = window.MutationObserver ||
                         window.WebKitMutationObserver ||
                         window.MozMutationObserver;
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

    // pass in the target node, as well as the observer options
    observer.observe(document.body, {
      attributes: true,
      childList: true,
      characterData: true,
      subtree: true
    });
  }

};
