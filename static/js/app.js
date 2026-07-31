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


        const last =
        document.getElementById("last-time");





        if(!dot || !text){

            return;

        }





        if(data.online){


            dot.style.background = "#6cff9b";


            dot.style.boxShadow =
            "0 0 12px rgba(108,255,155,.8)";


            text.innerHTML = "在线";



        }else{


            dot.style.background = "#aaa";


            dot.style.boxShadow = "none";


            text.innerHTML = "离线";


        }





        if(last && data.last_online){


            last.innerHTML =
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




// 每10秒检测一次

setInterval(

    updateStatus,

    10000

);









/* ==========================
   动态流星系统
========================== */


const meteorColors = [


    "rgba(255,190,220,.9)",


    "rgba(180,225,255,.9)",


    "rgba(220,200,255,.9)",


    "rgba(255,255,255,.85)"


];





function getMeteorCount(){


    const width = window.innerWidth;



    // 手机

    if(width <= 600){

        return 4;

    }



    // iPad

    if(width <= 1200){

        return 7;

    }



    // Mac

    return 9;


}









function random(min,max){


    return Math.random()*(max-min)+min;


}









function createMeteor(){



    const container =

    document.querySelector(".shooting-stars");



    if(!container){

        return;

    }





    const meteor =

    document.createElement("span");



    meteor.className = "dynamic-meteor";






    const color =

    meteorColors[

        Math.floor(

            Math.random()*meteorColors.length

        )

    ];






    const duration =

    random(1,2.5);





    const opacity =

    random(.35,.9);






    meteor.style.background = color;


    meteor.style.opacity = opacity;



    meteor.style.left =

    random(5,90)+"%";



    meteor.style.top =

    random(5,70)+"%";





    meteor.style.animationDuration =

    duration+"s";





    meteor.style.setProperty(

        "--meteor-color",

        color

    );





    container.appendChild(meteor);





    watchWidgetLight(meteor);







    setTimeout(()=>{


        meteor.remove();


    },


    duration*1000

    );





}









function startMeteorSystem(){



    const count =

    getMeteorCount();





    for(let i=0;i<count;i++){


        setTimeout(

            createMeteor,

            i*500

        );


    }





    setInterval(()=>{


        createMeteor();


    },


    random(3000,5000)

    );


}









/* ==========================
   Widget玻璃反光
========================== */


function watchWidgetLight(meteor){



    const widgets =

    document.querySelectorAll(".widget");



    if(!widgets.length){

        return;

    }






    const timer =

    setInterval(()=>{



        const m =

        meteor.getBoundingClientRect();





        widgets.forEach(widget=>{


            const w =

            widget.getBoundingClientRect();





            const hit =


            m.left < w.right &&

            m.right > w.left &&

            m.top < w.bottom &&

            m.bottom > w.top;







            if(hit){



                widget.classList.remove(

                    "shine"

                );



                void widget.offsetWidth;



                widget.classList.add(

                    "shine"

                );



            }





        });





        if(!document.body.contains(meteor)){


            clearInterval(timer);


        }





    },100);




}









// 启动流星

startMeteorSystem();