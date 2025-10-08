function change_color_of_item(id) {
    // Change the color of the table cell with id table + id
    var elem = document.getElementById("table" + String(id));
    var elemval = document.getElementById("tableval" + String(id));
    var listval = document.getElementById("listval" + String(id - 1));  // 0-indexed
    console.log(elem);
    console.log(elemval);
    if (elem.style.color == "red") {
      // Already red, change to black
      elem.style.color = "black";
      // Change background color to null to remove the background color and use the default
      elemval.style.backgroundColor = null;
      // Remove the button from the listval
      listval.innerHTML = "";
      // Hide the listval
      listval.setAttribute("hidden", "");
    } else {
      // Highlight the item in red
      elem.style.color = "red";
      elemval.style.backgroundColor = "red";
      // Add a button to the listval
      console.log(listval);
      listval.removeAttribute("hidden");
      listval.appendChild(document.createElement("button")).innerHTML = "Add to Cart";
      // Add an onclick event to the button
      listval.children[0].onclick = function () {
        // Add the item to the cart (in theory, this would be a server request)
        alert("Added " + elem.innerHTML + " to the cart");
      }
    }
  }