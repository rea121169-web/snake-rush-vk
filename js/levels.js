(function(){
  'use strict';
  const themes=[
    {id:'garden',icon:'🌿',bg:'#c8f1cf',grid:'#a9e2b5',wall:'#4a9d69',wallTop:'#72c98d',food:['apple','berry','cherry'],accent:'#53cf7e',dark:'#35a65c'},
    {id:'candy',icon:'🍭',bg:'#ffe2ef',grid:'#f7bfd5',wall:'#d85c91',wallTop:'#f28cb7',food:['donut','candy','berry'],accent:'#ef72a4',dark:'#c64d7d'},
    {id:'neon',icon:'🌃',bg:'#20254c',grid:'#303766',wall:'#6658d7',wallTop:'#9488ff',food:['bolt','berry','candy'],accent:'#58e3d1',dark:'#3db5a8'},
    {id:'ice',icon:'❄️',bg:'#d9f4fa',grid:'#b9e4ef',wall:'#5899c5',wallTop:'#82c8e3',food:['fish','berry','crystal'],accent:'#64c9e7',dark:'#3a9bbc'},
    {id:'space',icon:'🪐',bg:'#161a3a',grid:'#282d55',wall:'#7958b7',wallTop:'#a179df',food:['star','crystal','planet'],accent:'#9b6fe8',dark:'#7146b8'}
  ];
  const raw=[
    [6,390,0,0,0,0],[7,380,1,0,0,0],[8,370,2,0,0,0],[9,360,3,0,0,0],[10,350,4,0,0,0],[10,345,5,0,0,0],
    [11,340,6,0,0,0],[12,335,7,0,0,0],[12,330,8,0,0,0],[13,325,9,0,0,0],[13,320,10,0,0,0],[14,315,11,0,0,0],
    [14,310,12,0,0,0],[15,305,13,0,0,0],[15,300,14,0,0,0],[15,300,15,1,0,0],[16,295,16,1,0,0],[16,290,17,1,1,0],
    [16,290,18,1,1,0],[17,285,19,1,1,1],[17,280,20,1,1,1],[17,280,21,1,1,1],[18,275,22,1,1,1],[18,270,23,1,1,1],
    [18,270,24,1,1,1],[18,265,25,1,1,1],[19,260,26,1,1,1],[19,255,27,1,1,1],[20,250,28,1,1,1],[20,245,29,1,1,1]
  ];
  const levels=raw.map((r,i)=>({id:i+1,world:Math.floor(i/6),target:r[0],speed:r[1],pattern:r[2],portals:!!r[3],movers:!!r[4],hazards:!!r[5],powerups:i>4,par:Math.ceil(20+r[0]*3.3*(r[1]/300))}));
  const skins=[
    {id:'classic',nameRu:'Лайм',nameEn:'Lime',price:0,rarity:'common',colors:['#55d486','#8bebaa'],eye:'#263052',trail:'#75e6a0'},
    {id:'ocean',nameRu:'Океан',nameEn:'Ocean',price:120,rarity:'common',colors:['#3e9cec','#71c9ff'],eye:'#173657',trail:'#68c7ff'},
    {id:'berry',nameRu:'Малинка',nameEn:'Berry',price:180,rarity:'common',colors:['#ed5e9b','#ff9ac1'],eye:'#52213b',trail:'#ff87b5'},
    {id:'bee',nameRu:'Шмель',nameEn:'Bumblebee',price:280,rarity:'rare',colors:['#ffd64f','#292941'],eye:'#1c1d31',stripe:'#2b2c42',trail:'#ffe483'},
    {id:'melon',nameRu:'Арбуз',nameEn:'Watermelon',price:340,rarity:'rare',colors:['#4dcc78','#66e295'],eye:'#283449',stripe:'#e94f70',trail:'#6fe99a'},
    {id:'candy',nameRu:'Леденец',nameEn:'Candy',price:420,rarity:'rare',colors:['#62dce5','#ff78a6'],eye:'#3a3157',stripe:'#fff',trail:'#ffa3c2'},
    {id:'neon',nameRu:'Неон',nameEn:'Neon',price:520,rarity:'rare',colors:['#43f2cf','#6b51ef'],eye:'#151833',stripe:'#ec4eff',trail:'#52ffe0',glow:true},
    {id:'ice',nameRu:'Льдинка',nameEn:'Ice',price:650,rarity:'epic',colors:['#b9f5ff','#5cbce6'],eye:'#214a69',trail:'#d9fbff',glow:true},
    {id:'fire',nameRu:'Искра',nameEn:'Ember',price:780,rarity:'epic',colors:['#ff6a42','#ffc23f'],eye:'#592519',trail:'#ff9b45',glow:true},
    {id:'galaxy',nameRu:'Галактика',nameEn:'Galaxy',price:920,rarity:'epic',colors:['#322864','#9c5be2'],eye:'#fff',stripe:'#f3a8ff',trail:'#c17aff',glow:true},
    {id:'gold',nameRu:'Золотая',nameEn:'Golden',price:1150,rarity:'epic',colors:['#f2ad29','#ffe276'],eye:'#5a3b0c',trail:'#ffd75d',glow:true},
    {id:'rainbow',nameRu:'Радуга',nameEn:'Rainbow',price:1450,rarity:'legendary',colors:['#ff637c','#6fe3a1','#6aa9ff','#b56bea'],eye:'#2b2c4a',trail:'#fff18a',rainbow:true,glow:true},
    {id:'robot',nameRu:'Робо-змей',nameEn:'Robo Snake',price:1750,rarity:'legendary',colors:['#8ba1b2','#cad9e3'],eye:'#e94068',stripe:'#536778',trail:'#7be9ff',robot:true},
    {id:'ghost',nameRu:'Призрачная',nameEn:'Ghost',price:2100,rarity:'legendary',colors:['rgba(213,244,255,.75)','rgba(151,210,240,.72)'],eye:'#495b85',trail:'#d7f5ff',glow:true},
    {id:'royal',nameRu:'Королевская',nameEn:'Royal',price:2600,rarity:'legendary',colors:['#7853d9','#d39af5'],eye:'#fff1a6',stripe:'#f8d25f',trail:'#e7b6ff',glow:true,crown:true}
  ];
  const achievements=[
    {id:'firstBite',icon:'🐍',nameRu:'Первый кусь',nameEn:'First Bite',descRu:'Собери первое угощение',descEn:'Collect your first treat'},
    {id:'perfect',icon:'⭐',nameRu:'Перфекционист',nameEn:'Perfectionist',descRu:'Получи 3 звезды',descEn:'Earn 3 stars'},
    {id:'levels10',icon:'🗺️',nameRu:'Путешественник',nameEn:'Explorer',descRu:'Пройди 10 уровней',descEn:'Clear 10 levels'},
    {id:'collector',icon:'💰',nameRu:'Коллекционер',nameEn:'Collector',descRu:'Накопи 1000 монет',descEn:'Collect 1,000 coins'},
    {id:'fashion',icon:'🎨',nameRu:'Модная змейка',nameEn:'Fashion Snake',descRu:'Купи 5 скинов',descEn:'Own 5 skins'},
    {id:'endless1000',icon:'∞',nameRu:'Без остановки',nameEn:'Unstoppable',descRu:'Набери 1000 в бесконечном режиме',descEn:'Score 1,000 in Endless'},
    {id:'daily',icon:'☀️',nameRu:'Доброе утро',nameEn:'Good Morning',descRu:'Выполни испытание дня',descEn:'Complete a daily challenge'},
    {id:'master',icon:'👑',nameRu:'Мастер змейки',nameEn:'Snake Master',descRu:'Пройди все 30 уровней',descEn:'Clear all 30 levels'}
  ];
  function key(x,y){return x+','+y}
  function buildObstacles(level,cols,rows){
    const set=new Set(),add=(x,y)=>{if(x>1&&x<cols-2&&y>1&&y<rows-2&&!(x<8&&y>=Math.floor(rows/2)-1&&y<=Math.floor(rows/2)+1))set.add(key(x,y))};
    const h=(y,a,b,gap=-1)=>{for(let x=a;x<=b;x++)if(x!==gap)add(x,y)},v=(x,a,b,gap=-1)=>{for(let y=a;y<=b;y++)if(y!==gap)add(x,y)};
    const p=level.pattern;
    if(p===1){v(15,3,rows-4,7)}
    else if(p===2){h(4,8,17,12);h(rows-5,8,17,14)}
    else if(p===3){v(10,3,7,5);v(16,8,12,10)}
    else if(p===4){h(4,9,18,13);v(18,4,11,7)}
    else if(p===5){v(12,2,6,4);v(12,9,13,11);h(7,12,19,16)}
    else if(p===6){h(4,7,18,10);h(11,7,18,15)}
    else if(p===7){v(9,3,12,7);v(17,3,12,9);h(7,9,17,13)}
    else if(p===8){for(let x=10;x<=18;x+=2){add(x,4);add(x,10)}}
    else if(p===9){h(3,9,19,14);v(19,3,12,8);h(12,9,19,15)}
    else if(p===10){v(10,2,12,5);v(17,3,13,10);h(8,10,17,14)}
    else if(p===11){h(4,8,19,12);h(8,7,18,15);h(12,9,19,13)}
    else if(p===12){v(9,3,12,6);v(14,2,8,5);v(19,6,13,10)}
    else if(p===13){for(let y=3;y<=12;y+=3)h(y,8+(y%2),19-(y%3),12+y%5)}
    else if(p===14){h(3,10,19,15);v(10,3,11,7);h(11,10,19,14);v(19,5,11,8)}
    else if(p===15){v(11,3,12,6);v(18,3,12,9);h(3,11,18,14);h(12,11,18,16)}
    else if(p===16){h(5,9,18,13);h(10,9,18,15);v(9,5,10,7);v(18,5,10,8)}
    else if(p===17){for(let i=0;i<6;i++){add(10+i,3+i);add(18-i,9+i)}}
    else if(p===18){v(9,2,13,5);h(4,9,18,14);v(18,4,12,8);h(12,11,18,15)}
    else if(p===19){h(3,8,19,11);h(7,10,20,16);h(11,8,18,13);v(19,7,11,9)}
    else if(p===20){v(9,3,12,5);v(14,4,11,8);v(19,3,12,10);h(3,9,19,16)}
    else if(p===21){for(let x=9;x<20;x+=2)for(let y=3;y<13;y+=4)add(x,y)}
    else if(p===22){h(3,9,19,13);v(9,3,12,8);h(12,9,19,15);v(19,3,12,6)}
    else if(p===23){h(4,8,20,12);v(12,4,12,8);h(12,9,19,16);v(19,3,8,6)}
    else if(p===24){for(let y=3;y<=12;y+=3){h(y,8,20,y%2?11:17)}}
    else if(p===25){v(9,2,13,5);v(14,3,12,9);v(19,2,13,6);h(7,9,19,16)}
    else if(p===26){h(3,8,20,12);h(7,10,18,15);h(11,8,20,13);v(20,3,11,8)}
    else if(p===27){v(9,2,13,4);h(4,9,19,14);v(19,4,12,7);h(12,11,19,16);v(14,7,10,8)}
    else if(p===28){for(let i=0;i<8;i++){add(9+i,3+i%5);add(19-i,9+i%4)}}
    else if(p===29){h(3,9,20,13);v(9,3,12,7);h(12,9,20,16);v(20,3,12,8);h(7,12,17,14)}
    return [...set].map(s=>{const [x,y]=s.split(',').map(Number);return{x,y}})
  }
  function extras(level){
    const portal=level.portals?[{x:3+level.id%3,y:2},{x:19-level.id%3,y:13}]:[];
    const movers=level.movers?[{x:12+(level.id%4),y:6,dx:1,dy:0,min:10,max:18}]:[];
    const hazards=level.hazards?[{x:10+(level.id%8),y:2+(level.id%4)},{x:17-(level.id%6),y:12-(level.id%3)}]:[];
    return{portal,movers,hazards}
  }
  window.GameData={themes,levels,skins,achievements,buildObstacles,extras};
})();
