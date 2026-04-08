(function(){
  function lum(r,g,b){return .299*r+.587*g+.114*b}
  function parse(s){
    var m=s.match(/rgb\(\s*(\d+),\s*(\d+),\s*(\d+)\)/);
    if(m)return[+m[1],+m[2],+m[3]];
    m=s.match(/#([0-9a-f]{2})([0-9a-f]{2})([0-9a-f]{2})/i);
    if(m)return[parseInt(m[1],16),parseInt(m[2],16),parseInt(m[3],16)];
    return null}
  function fix(){
    document.querySelectorAll('.mermaid svg .node').forEach(function(n){
      var s=n.querySelector('rect,polygon,circle,path');
      if(!s)return;
      var st=s.getAttribute('style')||'';
      var fm=st.match(/fill:\s*(#[0-9a-f]{6}|rgb\([^)]+\))/i);
      if(!fm)return;
      var c=parse(fm[1]);
      if(c&&lum(c[0],c[1],c[2])<140)
        n.querySelectorAll('.nodeLabel').forEach(function(l){l.style.color='#fff'})
    })}
  new MutationObserver(fix).observe(document.body,{childList:true,subtree:true});
  document.addEventListener('DOMContentLoaded',function(){setTimeout(fix,400)});
})();
