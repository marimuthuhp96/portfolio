const chatBox = document.getElementById("chat-box");
const form = document.getElementById("chat-form");
const typing = document.getElementById("typing");

// auto scroll
window.onload=()=>{
 chatBox.scrollTop = chatBox.scrollHeight;
}

// typing animation
form.addEventListener("submit",()=>{
 typing.style.display="block";

 setTimeout(()=>{
  typing.style.display="none";
  chatBox.scrollTop = chatBox.scrollHeight;
 },1200);
});

// click suggestions
document.querySelectorAll(".suggestion,.card").forEach(el=>{
 el.addEventListener("click",()=>{
  document.getElementById("user-input").value = el.innerText;
 });
});
