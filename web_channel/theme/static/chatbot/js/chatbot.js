let chatSocket;
let reconnectInterval = 1000; // Initial reconnection interval in milliseconds
let maxReconnectInterval = 30000; // Maximum reconnection interval in milliseconds

window.onload = PrepopulateInitialConvo();




function initializeWebSocket() {
    chatSocket = new WebSocket('ws://' + window.location.host + '/ws/chat/');
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
        
        message = {
            email:email,       
            itax_pin:itax_pin,       
            itax_password:itax_password,      
            nhif_no:nhif_no
        }

    switch(option.value) {
        case '1':
            message = {
                action:option.value,
                email:email,       
                itax_pin:itax_pin,       
                itax_password:itax_password
                        }  
            display_message  =  `Action : `+option.options[option.selectedIndex].text+`<br>Email : `+email+`<br>Itax pin : `+itax_pin+`<br>Itax Password : ******** <br>`
          break;
        case '2':
            message = {
                action:option.value,
                email:email,       
                itax_pin:itax_pin,       
                itax_password:itax_password,      
                nhif_no:nhif_no
            }
            display_message  =  `Action : `+option.options[option.selectedIndex].text+`<br>Email : `+email+`<br>Itax pin : `+itax_pin+`<br>Itax Password : ******** <br>NHIF number : `+nhif_no+`<br>`

            break;
        case '3':
            message = {
                action:option.value,
                email:email,       
                itax_pin:itax_pin,       
                itax_password:itax_password
            }
            display_message  =  `Action : `+option.options[option.selectedIndex].text+`<br>Email : `+email+`<br>Itax pin : `+itax_pin+`<br>Itax Password : ******** <br>`

          break;
        case '4':
          message = {action:option.value,email:email} 
          display_message  =  `Action : `+option.options[option.selectedIndex].text+`<br>Email : `+email+`<br>`
          break;
        default:
          message = {}
          
      }

        SetUserInput(message=message,is_file=false,display_message=display_message)
    };

    document.querySelector('#chat-input').focus();
    document.querySelector('#chat-input').onkeyup = function (e) {
        if (e.keyCode === 13) {  // Enter key
            document.querySelector('#send-button').click();
        }
    };
    document.querySelector('#send-button').onclick = function (e) {
        const messageInputDom = document.querySelector('#chat-input');
        const message = messageInputDom.value;
        SetUserInput(message)
        messageInputDom.value = '';

    };
    document.querySelector('#data_validator_submit').onclick = function (e) {
        var message = "Submited"

        var table = document.getElementById('table');
        let table_data = {}
        let cell;
        for (var r = 0; r < table.rows.length; r++) {
            cell = document.getElementById('table_cell_'+r.toString());
            table_data[r.toString()] = cell.value
        }

        SetUserInput(table_data,is_file=false,display_message=message)
    };
    document.querySelector('#reset-button').onclick = function (e) {
        //delete channel from cookie

        //refresh

        SetUserInput('reset');

    };
    document.querySelector('#reset-button1').onclick = function (e) {
        //delete channel from cookie

        //refresh

        SetUserInput('reset');

    };
    document.querySelector('#reset-button2').onclick = function (e) {
        //delete channel from cookie

        //refresh

        SetUserInput('reset');

    };

   
}

function attemptReconnect() {
    setTimeout(function () {
        console.log('Attempting to reconnect...');
        statusDot.style.backgroundColor = 'red';
        statusText.textContent = 'Disconnected';
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
    var input_box = document.getElementById('input-box');
    var button_container = document.getElementById('button-container');
    var upload_form = document.getElementById('upload-form');
    var data_validator_container = document.getElementById('validator-button');
    var content;

    if(data.action === "START" ){
            localStorage.setItem('chatbotContent', ``);
            chatbotContainer.innerHTML="";
            if (data.cookie){
                    setChannelIdCookie(channelId=data.cookie);
                    chatSocket.close();
                    
            }
        }
    if (is_invalid_file_input){
        content = `<div class="message receiver-message">Invalid file type, kindly upload a pdf P9 - We currently don't support images.</div>`
    }
    else{
        content = `<div class="message sender-message">` + data.message + `</div>`
    }

    var newContent = createElementFromHTML(content);
    chatbotContainer.appendChild(newContent);

    if( data.data && data.keyboard_type=='data_validator'){

        let table_rows = ``;
        for(let i=0;i<data.data.length;i++){
            if (data.data[i].position === "end"){
                var table = `<table id="table"><tbody>`+table_rows+`</tbody></table>`;
                table_rows = ``;
            }
            else{
                table_rows +=`<tr> <td>`+data.data[i].key+`</td> <td> <input type="text" id="table_cell_`+i+`" value=`+data.data[i].value+`></td> </tr>`;
            }
        }

        newContent = createElementFromHTML(table);
        chatbotContainer.appendChild(newContent);



    }

    localStorage.setItem('chatbotContent', chatbotContainer.innerHTML);



    if (data.keyboard_type=="options") {

            let buttons = ``;

            for(let i=0;i<data.data.length;i++){
                buttons += `<button class="optionsButton" value=`+data.data[i].value+`>`+data.data[i].key+`</button>`
            }
            buttons += `<button id="reset-button1" class="fa fa-refresh" ></button>`

            button_container.innerHTML = buttons

            input_box.style.display = "none"
            upload_form.style.display = "none"
            button_container.style.display = "flex"
            data_validator_container.style.display = "none"

            let options_buttons = document.getElementsByClassName("optionsButton");
            for (var i = 0; i < options_buttons.length; i++) {
                options_buttons[i].addEventListener("click", function() {
                    SetUserInput(this.value,is_file=false,display_message=this.innerText)

                });
                }
        }
    else if (data.keyboard_type=="upload_pdf") {

            input_box.style.display = "none"
            upload_form.style.display = "flex"
            button_container.style.display = "none"
            data_validator_container.style.display = "none"


        }
    else if (data.keyboard_type=="validate") {

            var continue_button = document.getElementById('yes');
            var cancel_button = document.getElementById('no');

            continue_button.innerText = "PAID"
            cancel_button.innerText = "CANCEL"


            data_validator_container.style.display = "none"
            input_box.style.display = "none"
            upload_form.style.display = "none"
            button_container.style.display = "flex"
        }
    else if (data.keyboard_type=='data_validator'){
            input_box.style.display = "none"
            upload_form.style.display = "none"
            button_container.style.display = "none"
            data_validator_container.style.display = "flex"

    }
    else {
            input_box.style.display = "flex"
            upload_form.style.display = "none"
            button_container.style.display = "none"
            data_validator_container.style.display = "none"

        }

    var chat_container_input = document.getElementById('chat_container_input');
    localStorage.setItem('ChatContainerInput', chat_container_input.innerHTML);

}

function SetUserInput(message,is_file=false,display_message=null) {
    var chatbotContainer = document.getElementById('chat');
    var content;
    if (is_file) {
        content = `<div class="message receiver-message"><img src= "https://png.pngtree.com/png-clipart/20220612/original/pngtree-pdf-file-icon-png-png-image_7965915.png"
                                    alt="pdf"
                                    width="70" height="80">
                                </div>`
        const reader = new FileReader();
        reader.onload = (event) => {
            const arrayBuffer = event.target.result;
            chatSocket.send(arrayBuffer);
            console.log('File sent:', message.name);
        };
        reader.onerror = (error) => {
            console.error('File reading error:', error);
        };
        reader.readAsArrayBuffer(message);
    }
    else{


/*<div class="chat-bubble you">Welcome to our site, if you need help simply reply to this message, we are online and ready to help.</div>
        <div class="chat-bubble me">Hi, I am back</div>
        <div class="chat-bubble you">
            <svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" style="margin: auto;display: block;shape-rendering: auto;width: 43px;height: 20px;" viewBox="0 0 100 100" preserveAspectRatio="xMidYMid">
                <circle cx="0" cy="44.1678" r="15" fill="#ffffff">
                    <animate attributeName="cy" calcMode="spline" keySplines="0 0.5 0.5 1;0.5 0 1 0.5;0.5 0.5 0.5 0.5" repeatCount="indefinite" values="57.5;42.5;57.5;57.5" keyTimes="0;0.3;0.6;1" dur="1s" begin="-0.6s"></animate>
                </circle> <circle cx="45" cy="43.0965" r="15" fill="#ffffff">
                <animate attributeName="cy" calcMode="spline" keySplines="0 0.5 0.5 1;0.5 0 1 0.5;0.5 0.5 0.5 0.5" repeatCount="indefinite" values="57.5;42.5;57.5;57.5" keyTimes="0;0.3;0.6;1" dur="1s" begin="-0.39999999999999997s"></animate>
            </circle> <circle cx="90" cy="52.0442" r="15" fill="#ffffff">
                <animate attributeName="cy" calcMode="spline" keySplines="0 0.5 0.5 1;0.5 0 1 0.5;0.5 0.5 0.5 0.5" repeatCount="indefinite" values="57.5;42.5;57.5;57.5" keyTimes="0;0.3;0.6;1" dur="1s" begin="-0.19999999999999998s"></animate>
            </circle></svg>
        </div> */


            if (display_message === null) {
                content = `<div class="chat-bubble me">`+message+`</div>`
            }
            else{
                content = `<div class="chat-bubble me">`+display_message+`</div>`
            }
            //chatSocket.send(JSON.stringify({ 'message': message  }));
    }

    var newContent = createElementFromHTML(content);
    chatbotContainer.appendChild(newContent);
    localStorage.setItem('chatbotContent', chatbotContainer.innerHTML);
    scrollSmoothlyToBottom(id="chat")

}

function setChannelIdCookie(channelId) {
    expirationDays = 365;
    // Calculate expiration date
    const d = new Date();
    d.setTime(d.getTime() + (expirationDays * 24 * 60 * 60 * 1000));
    const expires = "expires=" + d.toUTCString();

    // Set the cookie
    document.cookie = `channel_id=${channelId}; ${expires}; path=/`;
}

function showInputs(event) {
    console.log(event)

    var option = document.getElementById('optionSelect').value;

    var email = document.getElementById('email');
    var itax_pin = document.getElementById('itax_pin');
    var itax_password = document.getElementById('itax_password');
    var nhif_no = document.getElementById('nhif_no');


    // Create inputs based on selected option
    switch(option) {
      case '1':
        email.classList.remove("hide")        
        itax_pin.classList.remove("hide")        
        itax_password.classList.remove("hide")        
        nhif_no.classList.add("hide")        
        break;
      case '2':
        email.classList.remove("hide")        
        itax_pin.classList.remove("hide")        
        itax_password.classList.remove("hide")        
        nhif_no.classList.remove("hide") 
        break;
      case '3':
        email.classList.remove("hide")        
        itax_pin.classList.remove("hide")        
        itax_password.classList.remove("hide")        
        nhif_no.classList.add("hide") 
        break;
      case '4':
        email.classList.add("hide")        
        itax_pin.classList.add("hide")        
        itax_password.classList.add("hide")        
        nhif_no.classList.add("hide") 
        break;
      default:
        email.classList.remove("hide")        
        itax_pin.classList.add("hide")        
        itax_password.classList.add("hide")        
        nhif_no.classList.add("hide") 
        
    }
  }

