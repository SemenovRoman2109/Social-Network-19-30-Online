import { getCSRFToken } from "../../../../static/js/getCSRFToken.js";

const csrfToken = getCSRFToken()

const homeFriendsList = document.querySelector('[data-home-section= "friends"]')
// 
async function handlerFriendAction(actionButton) {
    const response = await fetch(actionButton.dataset.url, {
        method: 'POST',
        headers: {
            'X-CSRFToken': csrfToken
        }
    })
    const data = await response.json()
    if (data.friend_html){
        addFriendToHome(data.friend_html)
    }
    if (data.label){
        actionButton.textContent = data.label
    }
    if (data.remove){
        actionButton.closest('article').remove()
    }
}
// 
function addFriendToHome(friendHtml){
    const friendsCount = homeFriendsList.querySelectorAll('article').length
    if (friendsCount >= 6){
        return
    }
    homeFriendsList.querySelector('p')?.remove()
    homeFriendsList.insertAdjacentHTML('beforeend', friendHtml)
    // 
    connectFriendActionButtons(homeFriendsList)
}
// підключаємо прослуховування подій до кнопок
function connectFriendActionButtons(parent = document){
    const actionButtons = parent.querySelectorAll('[data-friend-action]')
    actionButtons.forEach((actionButton) => {
        if (actionButton.dataset.actionButton){
            return
        }
        actionButton.dataset.actionButton = 'true'
        actionButton.addEventListener(
            'click',
            async () =>{
                await handlerFriendAction(actionButton)
            }
        )
    })
}
window.connectFriendActionButtons = connectFriendActionButtons

connectFriendActionButtons()
