function welcome (){
    var name = prompt("Enter you name:")
    var ptag = document.createElement("P");
    var welcomemessage = "Welcome " + name;
    ptag.innerText = welcomemessage; 
    console.log(ptag);
    document.body.appendChild(ptag);
    
}