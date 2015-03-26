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
  .state('analyzed', {
      url: '/:domain',
      templateUrl: 'analyzed.html',
      controller: 'AnalyzedController'
  })
  .state('sourceview', {
      url: '/:domain/source/:id/',
      templateUrl: 'source_view.html',
      controller: 'SourceViewController'
  })
  .state('diffview', {
      url: '/:domain/diff/:id',
      templateUrl: 'diff_view.html',
      controller: 'DiffViewController'
  })
  ;
}])

.run(['$http', '$cookies', function($http, $cookies) {
    $http.defaults.headers.post['X-CSRFToken'] = $cookies.csrftoken;
}])

;
