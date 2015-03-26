angular.module('controllers', ['services'])

.filter( 'filesize', function () {
     var units = [
        'bytes',
        'KB',
        'MB',
        'GB',
        'TB',
        'PB'
     ];

     return function( bytes, precision ) {
        if ( isNaN( parseFloat( bytes )) || ! isFinite( bytes ) ) {
            return '?';
        }

        var unit = 0;

        while ( bytes >= 1024 ) {
          bytes /= 1024;
          unit ++;
        }

        return bytes.toFixed( + precision ) + ' ' + units[ unit ];
     };
})

.directive('bindHtmlUnsafe', function( $compile ) {
    return function( $scope, $element, $attrs ) {

        var compile = function( newHTML ) { // Create re-useable compile function
            newHTML = $compile(newHTML)($scope); // Compile html
            $element.html('').append(newHTML); // Clear and append it
        };

        var htmlName = $attrs.bindHtmlUnsafe; // Get the name of the variable
                                              // Where the HTML is stored

        $scope.$watch(htmlName, function( newHTML ) { // Watch for changes to
                                                      // the HTML
            if(!newHTML) return;
            compile(newHTML);   // Compile it
        });

    };
})

.controller('StartController', ['$scope', '$http',
function($scope, $http) {
  document.title = 'Start';
  var initial_loading_message = "Start analysis";
  $scope.loading_message = initial_loading_message;
  $scope.startAnalysis = function() {
      $scope.job_submitted = null;
      if ($scope.domain.trim()) {
        $http.post('/analyzer/submit/', {domain: $scope.domain})
        .success(function(response) {
          $scope.job_submitted = $scope.domain;
          $scope.jobs_ahead = response.jobs_ahead;
        })
        .error(function() {
          console.error(arguments);
        })
        .finally(function() {
          $scope.loading_message = initial_loading_message;
        });
      }
      return false;
  };
  $http.get('/analyzer/recent-submissions')
  .success(function(response) {
    $scope.recent_domains = response.domains;
  });
}])

.controller('AnalyzedController', [
  '$scope', '$http', '$stateParams', 'lineLight',
  function($scope, $http, $stateParams, lineLight) {
    $scope.domain = $stateParams.domain;
    document.title = 'Analysis for ' + $scope.domain;
    $http.get('/analyzer/' + $scope.domain + '/data')
    .success(function(response) {
      // console.log(response);
      $scope.results = response.results;
      $scope.pages_count = response.pages_count;
      $scope.total_before = response.total_before;
      $scope.total_after = response.total_after;
    })
    .error(function() {
      $scope.error = arguments;
      console.error(arguments);
    });

    $scope.showDiff = function(result) {
      result._show_diff = !result._show_diff;
    };
    $scope.showSuspects = function(result) {
      result._show_suspects = !result._show_suspects;
    };
    $scope.setSourceViewLine = function(line) {
      lineLight.store(line);
    };
  }]
)

.controller('SourceViewController', [
  '$scope', '$http', '$stateParams', 'lineLight',
  function($scope, $http, $stateParams, lineLight) {
    $scope.domain = $stateParams.domain;
    $scope.id = $stateParams.id;
    document.title = 'Source view for ' + $scope.domain;
    $scope.loading = true;
    $http.get('/analyzer/' + $scope.domain + '/source/' + $scope.id + '/data')
    .success(function(response) {
      $scope.code = response.code;
      $scope.result = response.result;
      lineLight.highlight();
    })
    .error(function() {
      console.error(arguments);
    })
    .finally(function() {
      $scope.loading = false;
    });
  }
])

.controller('DiffViewController', ['$scope', '$http', '$stateParams',
function($scope, $http, $stateParams) {
  $scope.domain = $stateParams.domain;
  $scope.id = $stateParams.id;
  document.title = 'Diff view for ' + $scope.domain;
}])


;
