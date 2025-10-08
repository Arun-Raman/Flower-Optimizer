function fakesubmitfn(first_name) {
    // Show the real submit button and relish in your mischief
    document.getElementById("realsubmit").hidden = false;
    // Change the text in the fake submit button to show first name
    document.getElementById("fakesubmit").value = "Fooled you " + first_name + "!"
    document.getElementById("fakesubmit").setAttribute("disabled", "true");
  };

  function alertwithcontent(content) {
    alert("Hello " + content.first_name + " " + content.last_name + "! You submitted your previous form at " + content.date);
  };