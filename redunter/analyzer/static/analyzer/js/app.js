angular.module('app', [
  'ngRoute',
  'ngCookies',
  'ngSanitize',
  'controllers'
])

.config(['$routeProvider', '$locationProvider', '$httpProvider',
  function ($routeProvider, $locationProvider, $httpProvider) {
  $locationProvider.html5Mode(true);

  // $httpProvider.defaults.headers.post['Content-Type'] = 'application/x-www-form-urlencoded';

  $routeProvider
  .when('/analyzer/:domain', {
      templateUrl: 'analyzed.html',
      controller: 'AnalyzedController'
  })
  .when('/analyzer/:domain/source/:id', {
      templateUrl: 'source_view.html',
      controller: 'SourceViewController'
  })
  .when('/analyzer/:domain/diff/:id', {
      templateUrl: 'diff_view.html',
      controller: 'DiffViewController'
  })
  .when('/analyzer/', {
      templateUrl: 'start.html',
      controller: 'StartController'
  })
  ;
}])

.run(['$http', '$cookies', function($http, $cookies) {
    $http.defaults.headers.post['X-CSRFToken'] = $cookies.csrftoken;
}])

;
