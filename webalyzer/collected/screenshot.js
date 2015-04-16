var system = require('system');
var webpage = require("webpage");
var page = webpage.create();

// console.log(phantom.args);
var html_path = phantom.args[0];
var png_path = phantom.args[1];
var width = parseInt(phantom.args[2] || 1024, 10);
var height = parseInt(phantom.args[3] || 768, 10);

console.log(html_path, png_path, width, height);

// javascript should have been removed anyway
page.settings.javascriptEnabled = false;

page.settings.localToRemoteUrlAccessEnabled = true;
// page.settings.webSecurityEnabled = false;

page.viewportSize = {
  width: width,
  height: height,
};

// page.onResourceRequested = function(req) {
//   console.log('::loading', req.url);  // this does get logged now
// };
// page.onResourceReceived = function(res) {
//   console.log('::received', res.stage, res.id, res.status, res.url);
// };

page.settings.resourceTimeout = 3000;

page.open(html_path, function() {
  console.log(':: OPENED');
  // page.render(png_path);
  // page.close();
  // phantom.exit(0);
});

page.onLoadFinished = function() {
  console.log(':: FINISHED');
  // console.log('::rendering');
  // page.render('output.png');
  // phantom.exit();

  page.render(png_path);
  page.close();
  phantom.exit(0);
};

page.onResourceTimeout = function(e) {
  console.log(e.errorCode);   // it'll probably be 408
  console.log(e.errorString); // it'll probably be 'Network timeout on resource'
  console.log(e.url);         // the url whose request timed out
  phantom.exit(1);
};

// var html = system.stdin.read(100);
// page.setContent("<html><body><h1>Hi</h1><img src=image.jpg></body></html>", 'http://www.peterbe.com');
// page.setContent(html, 'http://www.peterbe.com');


// page.close();
// phantom.exit();
