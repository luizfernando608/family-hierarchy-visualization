// alert('If you see this alert, then your custom JavaScript script has run!')
window.onscroll = () => { window.scroll(0, 0); };
document.body.style.overflow = "hidden";

document.firstElementChild.style.zoom = "reset";

var metaTag=document.createElement('meta');
metaTag.name = "viewport"
metaTag.content = "width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=0"
document.getElementsByTagName('head')[0].appendChild(metaTag);