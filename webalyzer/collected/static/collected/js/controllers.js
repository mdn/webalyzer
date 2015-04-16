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
  $http.get('/collected/recently-collected')
  .success(function(response) {
    $scope.recent_domains = response.domains;
  });
}])

.controller('CollectedController', [
  '$scope', '$http', '$stateParams', '$interval',
  function($scope, $http, $stateParams, $interval) {
    $scope.domain = $stateParams.domain;
    
    document.title = 'Collected pages for ' + $scope.domain;
    $scope.loading = true;
    $http.get('/collected/' + $scope.domain + '/data')
    .success(function(response) {
      console.log(response);
      // $scope.results = response.results;
      $scope.pages_count = response.pages_count;
      $scope.total_html_size = response.total_html_size;
      $scope.pages = response.pages;
      $scope.missing_title = response.missing_title;
      $scope.missing_thumbnail = response.missing_thumbnail;
    })
    .error(function() {
      $scope.error = arguments;
      console.error(arguments);
    })
    .finally(function() {
      $scope.loading = false;
    });

    $scope.thumbnailSrc = function(page, dimensions) {
      return '/collected/' + $scope.domain + '/' + page.id + '/thumbnail.png' +
      '?dimensions=' + dimensions;
    };

    $scope.imageSrc = function(page) {
      return '/collected/' + $scope.domain + '/' + page.id + '/screenshot.png';
    };

  }]
)

// .controller('SourceViewController', [
//   '$scope', '$http', '$stateParams', 'lineLight',
//   function($scope, $http, $stateParams, lineLight) {
//     $scope.domain = $stateParams.domain;
//     $scope.id = $stateParams.id;
//     document.title = 'Source view for ' + $scope.domain;
//     $scope.loading = true;
//     $http.get('/analyzer/' + $scope.domain + '/source/' + $scope.id + '/data')
//     .success(function(response) {
//       $scope.code = response.code;
//       $scope.result = response.result;
//       lineLight.highlight();
//     })
//     .error(function() {
//       console.error(arguments);
//     })
//     .finally(function() {
//       $scope.loading = false;
//     });
//   }
// ])


;
