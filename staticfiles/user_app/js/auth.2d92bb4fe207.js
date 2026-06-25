// 
// export function getCSRFToken(){
//     return document.querySelector('meta[name="csrf-token"]').getAttribute('content')
// }
// 
export function showRegisterForm(){
    document.querySelector(".section-register").style.cssText = 'display: flex;'
    document.querySelector(".section-login").style.display = 'none'
    document.querySelector('.section-register nav').firstElementChild.style.cssText = 'border-bottom: 2px solid #543C52'
}
showRegisterForm()
// 
export function showLoginForm(){
    document.querySelector(".section-register").style.display = 'none'
    document.querySelector(".section-login").style.display = 'flex'
    document.querySelector('.section-login nav').lastElementChild.style.cssText = 'border-bottom: 2px solid #543C52'
}
// 
document.getElementById('register').addEventListener(
    'click',
    function(){
        showRegisterForm()
    }
)
// 
document.getElementById('login').addEventListener(
    'click',
    function(){
        showLoginForm()
    }
)
