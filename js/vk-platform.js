(function(){
  'use strict';

  const bridge=window.vkBridge;
  let initPromise=null;

  function isEmbedded(){
    if(!bridge)return false;
    if(typeof bridge.isEmbedded==='function')return bridge.isEmbedded();
    return window.parent!==window;
  }

  function init(){
    if(initPromise)return initPromise;
    if(!bridge||typeof bridge.send!=='function'||!isEmbedded()){
      initPromise=Promise.resolve(false);
      return initPromise;
    }
    initPromise=Promise.race([
      bridge.send('VKWebAppInit').then(()=>true).catch(()=>false),
      new Promise(resolve=>setTimeout(()=>resolve(false),2500))
    ]);
    return initPromise;
  }

  window.VKPlatform={init,isEmbedded};
})();
