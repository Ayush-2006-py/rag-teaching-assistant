let currentChatId=null;

// ---------- TAB SWITCH ----------
function switchSection(id,btn){
document.querySelectorAll(".section").forEach(s=>s.classList.remove("active"));
document.getElementById(id).classList.add("active");
document.querySelectorAll(".tab-btn").forEach(b=>{
b.classList.remove("border-green-500","border-b-2");
b.classList.add("text-gray-400");
});
btn.classList.add("border-green-500","border-b-2");
btn.classList.remove("text-gray-400");
}

// ---------- CHAT ----------
function createNewChat(){
currentChatId=Date.now().toString();
localStorage.setItem(currentChatId,JSON.stringify([]));
document.getElementById("chatContent").innerHTML="";
}

function sendMessage(){
const input=document.getElementById("chatInput");
const msg=input.value.trim();
if(!msg)return;

if(!currentChatId)createNewChat();

addMessage("user",msg);
input.value="";
input.focus();

/* ---- CONNECT TO RENDER BACKEND ---- */
fetch("https://rag-teaching-assistant-0jps.onrender.com/docs",{
method:"POST",
headers:{
"Content-Type":"application/json"
},
body:JSON.stringify({message:msg})
})
.then(res=>res.json())
.then(data=>{
addMessage("assistant",data.answer || "No response from backend");
})
.catch(()=>{
addMessage("assistant","⚠️ Cannot connect to backend");
});
}

function addMessage(role,text){
const content=document.getElementById("chatContent");
const scroll=document.getElementById("chatArea");

content.innerHTML+=`
<div class="flex ${role==='user'?'justify-end':''}">
<div class="${role==='user'?'bg-green-600':'bg-[#1f1f1f]'}
p-4 rounded-xl max-w-xl">${text}</div>
</div>`;

scroll.scrollTo({top:scroll.scrollHeight,behavior:"smooth"});

let data=JSON.parse(localStorage.getItem(currentChatId))||[];
data.push({role,text});
localStorage.setItem(currentChatId,JSON.stringify(data));
loadHistory();
}

function loadHistory(){
const list=document.getElementById("historyList");
list.innerHTML="";
Object.keys(localStorage).forEach(key=>{
const data=JSON.parse(localStorage.getItem(key));
if(!Array.isArray(data)||data.length===0)return;
const title=data[0].text.slice(0,25);
list.innerHTML+=`
<div class="flex items-center justify-between hover:bg-[#2a2a2a] rounded-lg">
<div onclick="loadChat('${key}')" class="p-2 flex-1 cursor-pointer">${title}</div>
<button onclick="deleteChat('${key}')" class="px-2 text-red-400">✕</button>
</div>`;
});
}

function deleteChat(id){
if(!confirm("Delete this chat?"))return;
localStorage.removeItem(id);
if(id===currentChatId)createNewChat();
loadHistory();
}

function loadChat(id){
currentChatId=id;
const content=document.getElementById("chatContent");
const scroll=document.getElementById("chatArea");
content.innerHTML="";
const data=JSON.parse(localStorage.getItem(id));
data.forEach(m=>{
content.innerHTML+=`
<div class="flex ${m.role==='user'?'justify-end':''}">
<div class="${m.role==='user'?'bg-green-600':'bg-[#1f1f1f]'}
p-4 rounded-xl max-w-xl">${m.text}</div>
</div>`;
});
scroll.scrollTo({top:scroll.scrollHeight});
}

function initializeApp(){
const keys=Object.keys(localStorage)
.filter(k=>Array.isArray(JSON.parse(localStorage.getItem(k))));
if(keys.length===0){
currentChatId=Date.now().toString();
localStorage.setItem(currentChatId,JSON.stringify([]));
}else{
currentChatId=keys[keys.length-1];
}
loadHistory();
loadChat(currentChatId);
}

// ---------- VIDEOS ----------
const videos=[
{name:"Lecture 1",file:"videos/lecture1.mp4"},
{name:"Lecture 2",file:"videos/lecture2.mp4"},
{name:"Lecture 3",file:"videos/lecture3.mp4"}
];

function loadVideos(){
const grid=document.getElementById("videoGrid");
grid.innerHTML="";
videos.forEach(v=>{
const card=document.createElement("div");
card.className="video-card";
card.innerHTML=`
<video controls class="w-full h-40 rounded-lg mb-3">
<source src="${v.file}">
</video>
<h3 class="font-semibold">${v.name}</h3>`;
grid.appendChild(card);
});
}

// ---------- INIT ----------
window.addEventListener("DOMContentLoaded",()=>{
initializeApp();
loadVideos();
});