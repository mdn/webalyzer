angular.module('controllers', [])

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

.controller('StartController', ['$scope', '$http',
function($scope, $http) {
  document.title = 'Start';
  var initial_loading_message = "Start analysis";
  $scope.loading_message = initial_loading_message;
  $scope.startAnalysis = function() {
      console.log($scope.domain);
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

.controller('AnalyzedController', ['$scope', '$http', '$stateParams',
function($scope, $http, $stateParams) {
  $scope.domain = $stateParams.domain;
  document.title = 'Analysis for ' + $scope.domain;
  $http.get('/analyzer/' + $scope.domain + '/data')
  .success(function(response) {
    console.log(response);
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

}])

.controller('SourceViewController', ['$scope', '$http', '$stateParams',
function($scope, $http, $stateParams) {
  $scope.domain = $stateParams.domain;
  $scope.id = $stateParams.id;
  document.title = 'Source view for ' + $scope.domain;
  $scope.loading = true;
  $http.get('/analyzer/' + $scope.domain + '/source/' + $scope.id + '/data')
  .success(function(response) {
    $scope.code = response.code;
    $scope.result = response.result;
  })
  .error(function() {
    console.error(arguments);
  })
  .finally(function() {
    $scope.loading = false;
  });
}])

.controller('DiffViewController', ['$scope', '$http', '$stateParams',
function($scope, $http, $stateParams) {
  $scope.domain = $stateParams.domain;
  $scope.id = $stateParams.id;
  document.title = 'Diff view for ' + $scope.domain;
}])


;
