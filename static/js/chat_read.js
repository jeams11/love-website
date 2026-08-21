/* ==========================
   已读未读同步
========================== */


function markRead(messageId){

    if(!messageId){
        return;
    }


    if(window.socket){

        window.socket.emit(
            "read_message",
            {
                id: messageId
            }
        );

    }

}




document.addEventListener(
    "click",
    function(e){


        const msg =
        e.target.closest(".message");


        if(!msg){
            return;
        }



        const id =
        msg.getAttribute("data-id");



        if(id){

            markRead(id);

        }


    }
);





document.addEventListener(
    "visibilitychange",
    function(){


        if(
            document.visibilityState !== "visible"
        ){

            return;

        }



        document
        .querySelectorAll(".message")
        .forEach(function(msg){


            const id =
            msg.getAttribute("data-id");



            if(id){

                markRead(id);

            }


        });


    }
);





window.addEventListener(
    "message_read",
    function(e){


        const data=e.detail;


        const msg=document.querySelector(

            `[data-id="${data.id}"]`

        );



        if(!msg){

            return;

        }



        const status =
        msg.querySelector(".read-status");



        if(status){

            status.innerHTML="已读";

        }


    }
);