let chatSocket;
let reconnectInterval = 1000; // Initial reconnection interval in milliseconds
let maxReconnectInterval = 30000; // Maximum reconnection interval in milliseconds

window.onload = function (){
    //PrepopulateInitialConvo();
    showInputs();
}

function validateEmail(email){
  return String(email)
    .toLowerCase()
    .match(
      /^(([^<>()[\]\\.,;:\s@"]+(\.[^<>()[\]\\.,;:\s@"]+)*)|.(".+"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/
    );
};
function initializeWebSocket() {
    chatSocket = new WebSocket('ws://' + window.location.host + '/ws/chat/?channel_id='+localStorage.getItem('conversation_id'));
    chatSocket.onopen = function (event) {
        console.log('WebSocket is open now.');
        reconnectInterval = 1000;
    };
    chatSocket.onmessage = function (e) {
        const data = JSON.parse(e.data);
        SetBotResponse(data)
        scrollSmoothlyToBottom(id = "chat")
        chatSocket.send(JSON.stringify({"acknowledged":true,"message_id":data.message_id}))

    };
    chatSocket.onclose = function (e) {
        console.error('Chat socket closed unexpectedly');
        attemptReconnect();
    };
    chatSocket.onerror = function (error) {
        console.error('WebSocket error observed:', error);
        chatSocket.close();
    };

    document.querySelector('#start_filing').onclick = function (e) {

        var option = document.getElementById('optionSelect');
        var email = document.getElementById('email').value;
        var itax_pin = document.getElementById('itax_pin').value;
        var itax_password = document.getElementById('itax_password').value;
        var nhif_no = document.getElementById('nhif_no').value;


        var chatbotContainer = document.getElementById('chat');
        chatbotContainer.innerHTML = ""
        localStorage.setItem('chatbotContent', ``);

        const now = Date.now(); // Unix timestamp in milliseconds
        localStorage.setItem('conversation_id', now);

        let has_error = false;
        switch(option.value) {
            case '1':
                if (!validateEmail(email)) {
                    has_error = true;
                }
                if (itax_pin == "" || itax_pin.length !== 11 ){
                    has_error = true;
                }
                if (itax_password == "" || itax_password.length == 0){
                    has_error == true
                }


                message = {
                    id:now,
                    is_start:true,
                    action:option.value,
                    email:email,
                    itax_pin:itax_pin,
                    itax_password:itax_password,
                    nhif_no:nhif_no
                }
                display_message  =  `Action : `+option.options[option.selectedIndex].text+`<br>Email : `+email+`<br>Itax pin : `+itax_pin+`<br>Itax Password : ******** <br>NHIF number : `+nhif_no+`<br>`

                break;
            case '2':
                if (!validateEmail(email)) {
                    has_error = true;
                }
                if (itax_pin == "" || itax_pin.length !== 11 ){
                    has_error = true;
                }
                if (itax_password == "" || itax_password.length == 0){
                    has_error == true
                }
                if (nhif_no == "" || nhif_no.length == 0){
                    has_error == true
                }
                message = {
                    id:now,
                    is_start:true,
                    action:option.value,
                    email:email,
                    itax_pin:itax_pin,
                    itax_password:itax_password
                            }
                display_message  =  `Action : `+option.options[option.selectedIndex].text+`<br>Email : `+email+`<br>Itax pin : `+itax_pin+`<br>Itax Password : ******** <br>`
              break;
            case '3':
                if (!validateEmail(email)) {
                    has_error = true;
                }
                if (itax_pin == "" || itax_pin.length !== 11 ){
                    has_error = true;
                }
                if (itax_password == "" || itax_password.length == 0){
                    has_error == true
                }
                if (nhif_no == "" || nhif_no.length == 0){
                    has_error == true
                }
                message = {
                    id:now,
                    is_start:true,
                    action:option.value,
                    email:email,
                    itax_pin:itax_pin,
                    itax_password:itax_password
                }
                display_message  =  `Action : `+option.options[option.selectedIndex].text+`<br>Email : `+email+`<br>Itax pin : `+itax_pin+`<br>Itax Password : ******** <br>`

              break;
            case '4':
                if (!validateEmail(email)) {
                    has_error = true;
                }
                if (itax_pin == "" || itax_pin.length !== 11 ){
                    has_error = true;
                }
                if (itax_password == "" || itax_password.length == 0){
                    has_error == true
                }
                if (nhif_no == "" || nhif_no.length == 0){
                    has_error == true
                }
              message = {
                         id:now,
                         is_start:true,
                         action:option.value,
                         email:email,
                         itax_password:itax_password
                        }
              display_message  =  `Action : `+option.options[option.selectedIndex].text+`<br>Email : `+email+`<br>Itax Password : ******** <br>`
              break;

            case '5':
                if (!validateEmail(email)) {
                    has_error = true;
                }

              message = { id:now,
                          is_start:true,
                          action:option.value,
                          email:email }
              display_message  =  `Action : `+option.options[option.selectedIndex].text+`<br>Email : `+email+`<br>`
              break;


            default:
              message = {}

          }
          if(has_error == true){
              console.log("ghhgfhjkg")
              var error_div = document.getElementById('error_div');
              error_div.classList.remove("hide");
          }
          else{
                $('.chat-start-form').addClass('hide');
                $('.chat-body').removeClass('hide');
                $('.chat-input').removeClass('hide');
                $('.chat-header-option').removeClass('hide');
                SetUserInput(message=message,is_file=false,display_message=display_message);

          }
        };

    document.querySelector('#send_button').onclick = function (e) {
                const messageInputDom = document.querySelector('#chat-input');
                var input_text = messageInputDom.value

                var phonePattern = /^(?:\+?254|0)?(7|1)\d{8}$/;
                if (!phonePattern.test(input_text)) {
                    messageInputDom.placeholder = 'Invalid phone number';
                }
                else {
                     var message = {id:localStorage.getItem('conversation_id'),
                                                       is_start:false,
                                                       text:input_text};

                    SetUserInput(message=message,is_file=false,display_message=input_text)
                    messageInputDom.value = '';

                }



            };

    document.querySelector('#fileInput').onchange = function (e) {
                console.log("e.files")
                console.log(e.files)

                var file_input = document.getElementById('fileInput')
                var file = file_input.files[0];
                if (file) {
                    var fileType = file.type;
                    if (fileType !== 'application/pdf') {
                         SetBotResponse(data={"keyboard_type":"upload_pdf"},
                             is_invalid_file_input=true)
                    } else {
                         SetUserInput(message=file_input.files,is_file=true)
                    }

                }
                scrollSmoothlyToBottom(id = "chat")

            };

    document.querySelector('#upload_multiple_files').onclick = function (e) {
                var file_inputs = document.getElementById('multiFileInput')
                var files = file_inputs.files;
                if (files) {
                            SetUserInput(message=files,is_file=true)
                           }
                scrollSmoothlyToBottom(id = "chat")

            };

multi_upload
}

function attemptReconnect() {
    setTimeout(function () {
        console.log('Attempting to reconnect...');
        // Increase the reconnection interval for the next attempt
        reconnectInterval = Math.min(reconnectInterval * 2, maxReconnectInterval);
        initializeWebSocket();
    }, reconnectInterval);
}

function createElementFromHTML(htmlString) {
    var div = document.createElement('div');
    div.innerHTML = htmlString.trim();
    return div.firstChild;
}

function scrollSmoothlyToBottom(id){
            const element = $(`#${id}`);
            element.animate({
                scrollTop: element.prop("scrollHeight")
            }, 500);
        }

function PrepopulateInitialConvo(){
    var chatbotContainer = document.getElementById('chat');
    var chat_container_input = document.getElementById('chat_container_input');

    // Load content from local storage when the page loads
    var savedContent = localStorage.getItem('chatbotContent');
    var savedContainerInput = localStorage.getItem('ChatContainerInput');
    if (savedContent) {
        chatbotContainer.innerHTML = savedContent;
    }
    if (savedContainerInput) {
        chat_container_input.innerHTML = savedContainerInput;
    }
    scrollSmoothlyToBottom(id="chat")
    // Initialize the WebSocket connection
    initializeWebSocket();
}

function SetBotResponse(data,is_invalid_file_input=false){

    var chatbotContainer = document.getElementById('chat');
    var content;

    content = ``
    for (var i = 0;i< data.message.length ; i++){
        content += `<div class="chat-bubble you">`+data.message[i]+`</div>`
    }


    var newContent = createElementFromHTML(content);
    chatbotContainer.appendChild(newContent);
    localStorage.setItem('chatbotContent', chatbotContainer.innerHTML);


    if(data.has_table){
        var table_content = ``
        if (data.table_type === "toggle") {
            let rows = ``;
            for (var i = 0;i< data.data.length ; i++){
                rows += `<tr>
                            <td>`+data.data[i].label+`</td>
                            <td>
                                <label class="switch">
                                  <input class="`+data.table_id+`_buttons" id=`+data.data[i].id+` type="checkbox">
                                  <span class="slider round"></span>
                                </label>                       
                            </td>
                        </tr>`
            }
            table_content += `<div class="chat-bubble you"><table id=`+data.table_id+`>`+ rows+`</table></div>`
        }
        else if(data.table_type === "validator"){
             let rows = ``;
             for (var i = 0;i< data.data.length ; i++){
                rows += `<tr>
                            <td>`+data.data[i].label+`</td>
                            <td>
                                <label >
                                  <input class="`+data.table_id+`_inputs" id=`+data.data[i].id+` type="text" value=`+data.data[i].value+`>
                                </label>                       
                            </td>
                        </tr>`
            }
             table_content += `<div class="chat-bubble you"><table id=`+data.table_id+`>`+ rows+`</table></div>`

        }

        var new_table_content = createElementFromHTML(table_content);
        chatbotContainer.appendChild(new_table_content);
        localStorage.setItem('chatbotContent', chatbotContainer.innerHTML);
    }


    var chat_input = document.getElementById('chat_input');
    var normal_input = document.getElementById('normal-input');
    var button_input = document.getElementById('button-input');
    var upload_input = document.getElementById('upload-input');
    var multi_upload = document.getElementById('multi_upload');

    chat_input.classList.remove("hide")

    if (data.keyboard_type === "buttons"){
        button_input.classList.remove("hide")
        normal_input.classList.add("hide")
        upload_input.classList.add("hide")
        multi_upload.classList.add("hide")

        let buttons = ``;
        for(let i=0;i<data.buttons.length;i++){
            buttons += `<button class="btn btn-primary btn-rounded btn-block" id=`+ data.buttons[i].id + ` value=`+ data.buttons[i].id +`>`+data.buttons[i].label+`</button>`
        }
        button_input.innerHTML = buttons
        for(let i=0;i<data.buttons.length;i++) {
            document.querySelector('#' + data.buttons[i].id).onclick = function (e) {
                var message = {};
                if (data.buttons[i].id == "taxpayer_matrix") {
                    var taxpayer_matrix_checkboxes = document.getElementsByClassName(data.table_id+`_buttons`);
                    for(let j=0;j<taxpayer_matrix_checkboxes.length;j++) {
                        message[taxpayer_matrix_checkboxes[j].id] = taxpayer_matrix_checkboxes[j].checked;
                    }
                    SetUserInput(message={id:localStorage.getItem('conversation_id'),is_start:false,data:message},
                                   is_file=false,
                           display_message="Submited")
                }
                else if (data.buttons[i].id == "validate"){
                    var p9_validated_data = document.getElementsByClassName(data.table_id+`_inputs`);
                    for(let j=0;j<p9_validated_data.length;j++) {
                        message[p9_validated_data[j].id] = p9_validated_data[j].value;
                    }
                    SetUserInput(message={id:localStorage.getItem('conversation_id'),is_start:false,data:message},
                                   is_file=false,
                           display_message="Validated")
                }

                else {
                    SetUserInput(message={id:localStorage.getItem('conversation_id'),is_start:false,text:e.target.id},
                                   is_file=false,
                           display_message=e.target.innerText)
                }
            }
        }
    }
    else if (data.keyboard_type === "normal"){
        button_input.classList.add("hide")
        normal_input.classList.remove("hide")
        upload_input.classList.add("hide")
        multi_upload.classList.add("hide")

    }
    else if (data.keyboard_type === null){
        chat_input.classList.add("hide")
        button_input.classList.add("hide")
        normal_input.classList.add("hide")
        upload_input.classList.add("hide")
        multi_upload.classList.add("hide")


    }
    else if (data.keyboard_type === "upload"){
        button_input.classList.add("hide")
        normal_input.classList.add("hide")
        upload_input.classList.remove("hide")
        multi_upload.classList.add("hide")

    }
    else if (data.keyboard_type === "multi_upload"){
        button_input.classList.add("hide")
        normal_input.classList.add("hide")
        upload_input.classList.add("hide")
        multi_upload.classList.remove("hide")
    }
}

function stringToArrayBuffer(str) {
    const encoder = new TextEncoder();
    return encoder.encode(str).buffer;
}

// Function to combine file and JSON data
async function combineFileAndJson(file, jsonData) {
    // Convert JSON data to string and then to ArrayBuffer
    const jsonString = JSON.stringify(jsonData);
    const jsonBuffer = stringToArrayBuffer(jsonString);

    // Read the file as ArrayBuffer
    const fileBuffer = await file.arrayBuffer();

    // Create a delimiter as ArrayBuffer
    const delimiter = stringToArrayBuffer("|delimiter|");

    // Combine all parts into a single ArrayBuffer
    const combinedBuffer = new Uint8Array(jsonBuffer.byteLength + delimiter.byteLength + fileBuffer.byteLength);
    combinedBuffer.set(new Uint8Array(jsonBuffer), 0);
    combinedBuffer.set(new Uint8Array(delimiter), jsonBuffer.byteLength);
    combinedBuffer.set(new Uint8Array(fileBuffer), jsonBuffer.byteLength + delimiter.byteLength);

    return combinedBuffer.buffer;
}


async function SetUserInput(message,is_file=false,display_message=null) {
    var chatbotContainer = document.getElementById('chat');
    var content = ``;
    if (is_file) {
        for (let k = 0; k < message.length ; k++){
            var file = message[k];
            content = `<div class="chat-bubble me"><img src= "https://png.pngtree.com/png-clipart/20220612/original/pngtree-pdf-file-icon-png-png-image_7965915.png"
                                        alt="pdf"
                                        width="70" height="80">
                                    </div>`
            const base_message= {  id:localStorage.getItem('conversation_id'),
                                        is_start:false,
                                        is_last_doc:false,
                                        file_name:file.name,
                                      };
            if (k==message.length - 1){
                base_message.is_last_doc = true;
            }

            const combinedData = await combineFileAndJson(file, base_message);
            chatSocket.send(combinedData);

            var newContent = createElementFromHTML(content);
            chatbotContainer.appendChild(newContent);

        }



    }
    else{
            if (display_message === null) {
                content = `<div class="chat-bubble me">`+message+`</div>`
            }
            else{
                content = `<div class="chat-bubble me">`+display_message+`</div>`
            }
            chatSocket.send(JSON.stringify({ 'message': message  }));

            var newContent = createElementFromHTML(content);
            chatbotContainer.appendChild(newContent);
    }


    localStorage.setItem('chatbotContent', chatbotContainer.innerHTML);
    scrollSmoothlyToBottom(id="chat")

}

function showInputs() {
    var option = document.getElementById('optionSelect').value;
    var email = document.getElementById('email');
    var itax_pin = document.getElementById('itax_pin');
    var itax_password = document.getElementById('itax_password');
    var nhif_no = document.getElementById('nhif_no');
    var start_button = document.getElementById('start_filing');


    start_button.disabled = false;

    // Create inputs based on selected option
    switch(option) {
      case '1':
        email.classList.remove("hide")
        itax_pin.classList.remove("hide")
        itax_password.classList.remove("hide")
        nhif_no.classList.remove("hide")
        break;
      case '2':
        email.classList.remove("hide")        
        itax_pin.classList.remove("hide")        
        itax_password.classList.remove("hide")        
        nhif_no.classList.add("hide")        
        break;
      case '3':
        email.classList.remove("hide")        
        itax_pin.classList.remove("hide")        
        itax_password.classList.remove("hide")        
        nhif_no.classList.add("hide") 
        break;
      case '4':
        email.classList.add("hide")        
        itax_pin.classList.remove("hide")
        itax_password.classList.remove("hide")
        nhif_no.classList.add("hide") 
        break;
      case '5':
        email.classList.remove("hide")
        itax_pin.classList.add("hide")
        itax_password.classList.add("hide")
        nhif_no.classList.add("hide")
        break;
      default:
        email.classList.add("hide")
        itax_pin.classList.add("hide")        
        itax_password.classList.add("hide")        
        nhif_no.classList.add("hide")
        start_button.disabled = true;

        
    }
  }

