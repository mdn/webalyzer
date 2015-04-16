$(function() {
  $('.result').on('click', 'button.diffs', function() {
    $(this).toggleClass('button-primary');
    $('div.diff', $(this).parents('.result')).toggle();
  });
  $('.result').on('click', 'button.suspects', function() {
    $(this).toggleClass('button-primary');
    $('div.suspects', $(this).parents('.result')).toggle();
  });
});
