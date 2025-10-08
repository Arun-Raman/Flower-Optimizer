$(document).ready(function(){
    $("button").click(function(){
      $("#link").attr({
        "href" : "https://www.ece.gatech.edu/",
        "title" : "Gatech ECE"
      });

      // To change the text of the link as well
      // $("#link").text('Gatech ECE');
    });
  });