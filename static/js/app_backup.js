/* ==========================
   在线状态检测
========================== */


function updateStatus(){


    fetch("/heartbeat")


    .then(response => response.json())


    .then(data => {


        const dot =
        document.getElementById("status-dot");


        const text =
        document.getElementById("status-text");


        const time =
        document.getElementById("last-time");




        if(data.online){


            dot.style.background =
            "#62ff9b";


            dot.style.boxShadow =
            "0 0 15px #62ff9b";


            text.innerHTML =
            "在线";



        }else{


            dot.style.background =
            "#aaa";


            dot.style.boxShadow =
            "none";


            text.innerHTML =
            "离线";


        }



        if(data.last_online){


            time.innerHTML =
            data.last_online;


        }


    })


    .catch(()=>{


        const text =
        document.getElementById("status-text");


        if(text){

            text.innerHTML =
            "检测失败";

        }


    });



}




// 页面打开检测

updateStatus();



// 每 10 秒更新

setInterval(

updateStatus,

10000

);









/* ==========================
   桌面端玻璃鼠标光效
========================== */


if(window.innerWidth > 800){



document.addEventListener(

"mousemove",

(e)=>{



    document.documentElement.style
    .setProperty(

    "--mouse-x",

    e.clientX+"px"

    );



    document.documentElement.style
    .setProperty(

    "--mouse-y",

    e.clientY+"px"

    );



}



);



}








/* ==========================
   鼠标玻璃光层
========================== */



const cards = document.querySelectorAll(

".days-card, .online-box, .memory-box"

);



if(window.innerWidth > 800){



cards.forEach(card=>{



    card.addEventListener(

    "mousemove",

    (e)=>{


        const rect =
        card.getBoundingClientRect();



        const x =
        e.clientX - rect.left;



        const y =
        e.clientY - rect.top;



        card.style.setProperty(

        "--light-x",

        x+"px"

        );



        card.style.setProperty(

        "--light-y",

        y+"px"

        );



    }



    );




});



}






/* ==========================
   页面加载完成动画
========================== */


window.addEventListener(

"load",

()=>{


    document.body.classList.add(

    "loaded"

    );


}

);