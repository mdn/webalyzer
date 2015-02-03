$(function() {
  $('.result input[type="button"].diffs').click(function() {
    $(this).toggleClass('button-primary');
    $('div.diff', $(this).parents('.result')).toggle();
  });
  $('.result input[type="button"].suspects').click(function() {
    $(this).toggleClass('button-primary');
    $('div.suspects', $(this).parents('.result')).toggle();
  });
});
