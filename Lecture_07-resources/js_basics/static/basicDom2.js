function displayMessage(elem) {
    var clickedButton = elem.innerHTML;
    var displayString = clickedButton + " was clicked";
    var pTag = document.createElement("P");
    pTag.innerHTML = displayString;

    // Replace the existing paragraph
    currPTags = document.getElementsByTagName('p');
    if (currPTags.length != 0) {

        for (i = 0; i < currPTags.length; i++) {
            currPTags[i].remove();
        }
    }
    document.body.appendChild(pTag);
    elem.disabled = true;

    // Enable clicking the others

    currButtons = document.getElementsByTagName('button');
    // elem1 = document.getElementById("elem2")
    // elem1.innerText = "Some new message"
    if (currButtons.length != 0) {

        for (i = 0; i < currButtons.length; i++) {
            console.log(currButtons[i]);
            if (currButtons[i].innerHTML != clickedButton) {
                currButtons[i].disabled = false;
            }
        }
    }
}
