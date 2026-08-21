// ==========================
// Chat Socket
// ==========================

let chatSocket = null;


// 初始化聊天 Socket

function initChatSocket(){

    if(typeof io === "undefined"){
        console.log("Socket.IO 未加载");
        return;
    }


    chatSocket = io();


    window.chatSocket = chatSocket;


    chatSocket.on(
        "connect",
        function(){

            console.log(
                "聊天Socket连接成功"
            );

        }
    );



    // 接收消息

    chatSocket.on(
        "receive_message",
        function(data){

            console.log(
                "收到消息:",
                data
            );


            renderMessage(data);

        }
    );



    // 撤回同步

    chatSocket.on(
        "withdraw_message",
        function(data){

            let msg =
            document.querySelector(
                `[data-message-id="${data.id}"]`
            );


            if(msg){

                msg.innerHTML =
                "消息已撤回";

            }

        }
    );

}



// 发送消息

function sendChatMessage(){


    let input =
    document.getElementById(
        "message"
    );


    if(!input){
        return;
    }


    let content =
    input.value.trim();


    if(!content){
        return;
    }



    chatSocket.emit(
        "send_message",
        {
            content:content,
            type:"text"
        }
    );


    input.value="";

}



// 渲染消息

function renderMessage(data){


    let box =
    document.getElementById(
        "messages"
    );


    if(!box){
        console.log(
            "没有消息容器 #messages"
        );
        return;
    }



    let div =
    document.createElement(
        "div"
    );


    div.className =
    "message";



    div.dataset.messageId =
    data.id;



    div.innerHTML = `

        <div class="bubble">

        ${data.content}

        </div>

        <span class="read-status">

        未读

        </span>

    `;



    box.appendChild(div);

}