$(document).ready(function(){ 
    $("button").click(function(){
        changefunc($(this));
    })

    function changefunc(thisObj) {
        $('.btn').attr("disabled", false);
        thisObj.attr("disabled", true);
        console.log(thisObj);
        var message = "<p>" + thisObj[0].innerHTML + " was clicked" + "</p>";
        $('p').remove();
        $('body').append(message);
    }
  });