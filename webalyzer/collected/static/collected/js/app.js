angular.module('app', [
  'ngCookies',
  'ngSanitize',
  'ui.router',
  'controllers',
  'services',
])

.config(['$stateProvider', '$locationProvider',
  function ($stateProvider, $locationProvider) {
  $locationProvider.html5Mode(true);

  // $urlRouterProvider.otherwise('/analyzer');
  // $httpProvider.defaults.headers.post['Content-Type'] = 'application/x-www-form-urlencoded';

  $stateProvider
  .state('start', {
      url: '/',
      templateUrl: 'start.html',
      controller: 'StartController'
  })
  .state('collected', {
      url: '/:domain',
      templateUrl: 'collected.html',
      controller: 'CollectedController'
  })
  .state('collected.sourceview', {
      url: '/:id',
      templateUrl: 'source_view.html',
      controller: 'SourceViewController'
  })
  ;
}])

.run(['$http', '$cookies', function($http, $cookies) {
    $http.defaults.headers.post['X-CSRFToken'] = $cookies.csrftoken;
}])

;
