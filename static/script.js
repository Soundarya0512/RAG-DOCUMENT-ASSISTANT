console.log("script loaded!")
let sendbutton=document.getElementById("sendBtn")
console.log("SendButton: ",sendbutton)
let chatarea=document.getElementById("chatArea")
console.log("ChatArea: ",chatarea)
let file=document.getElementById("fileInput")
console.log("Fileupload: ",file)
let userinput=document.getElementById("questionInput")
console.log("UserInput: ",userinput)
let clear=document.getElementById("clearBtn")
console.log("ClearButton: ",clear)
let status=document.getElementById("status")
let user_file = document.getElementById("fileInput")

//Chat Area

async function send(){
    let question = userinput.value;
    chatarea.innerHTML += "<div class='user-message'>👤 " + question + "</div>";
    status.innerHTML += "🤖 Thinking... "
    let response=await fetch ("http://localhost:8000/query",{
        method: "POST",
        headers:{
            "Content-Type": "application/json"
        },
        body: JSON.stringify({question: question})

    });

    let data= await response.json();
    status.innerHTML = "";
    chatarea.innerHTML += "<div class='bot-message'>🤖 " + data.answer + "</div>";
    data.sources.forEach((source) => {
    if (source.page !== "N/A") {
        chatarea.innerHTML += `<div class='source'>📄 ${source.source}: ${source.preview} (page ${source.page})</div>`;
    } else {
        chatarea.innerHTML += `<div class='source'>📄 ${source.source}: ${source.preview}</div>`;
    }
    });

    //console.log(data);
    userinput.value = "";
}

sendbutton.addEventListener("click",send)

userinput.addEventListener("keydown", function(event) {
    if (event.key === "Enter") {
        send();
    }
});

//File Upload
user_file.addEventListener("change",async function(){
    
    let selectedFile=user_file.files[0];

    // Show loading status
    status.innerHTML = "🔄 Uploading";

    let formData = new FormData();
    formData.append("file",selectedFile);

    // Send to backend
    let response = await fetch("http://localhost:8000/upload", {
        method: "POST",
        body: formData
    });
    
    // Get response
    let data = await response.json();
    
    // Clear loading
    status.innerHTML = "";
    
    // Show success message
    chatarea.innerHTML += `<div class='bot-message'>✅ Uploaded: ${data.filename}</div>`;


});

//Clear Button

clear.addEventListener("click", async function() {
    
    await fetch("http://localhost:8000/clear_history", {
        method: "POST"
    });
    
    // Clear the chat area too!
    chatarea.innerHTML = ""

    status.innerHTML = "✅ Chat cleared!";
});