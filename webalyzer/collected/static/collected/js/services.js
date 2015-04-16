angular.module('services', [])

.factory('lineLight', ['$timeout', function($timeout) {
  var line = null;
  var service = {};
  service.store = function(l) {
    line = l;
  };
  service.get = function() {
    return line;
  };
  service.highlight = function() {
    if (line !== null) {
      $timeout(function() {
        var lineAbove = document.getElementById(
          'L-' + Math.max(0, line - 15)
        );
        lineAbove.scrollIntoView();
        var thisLine = document.getElementById('L-' + line);
        thisLine.classList.add('highlit-line');
        $timeout(function() {
          thisLine.classList.remove('highlit-line');
        }, 10 * 1000);
      }, 300);
    }
  };
  return service;
}])

;
