// const csrfToken = document.querySelector("meta[name='csrf-token']").content
// Знаходимо кнопку, яка відкриває модальне вікно створення групи.
const openGroupModalButton = document.querySelector("#open-group-modal");
// Знаходимо саме модальне вікно.
const groupModal = document.querySelector("#group-modal");
// Знаходимо перший крок модального вікна з вибором друзів.
const groupStepUsers = document.querySelector("#group-step-users");
// Знаходимо другий крок модального вікна з введенням назви.
const groupStepName = document.querySelector("#group-step-name");
// Знаходимо кнопку закриття на першому кроці.
const closeGroupModalButton = document.querySelector("#close-group-modal");
// Знаходимо кнопку закриття на другому кроці.
const closeGroupNameModalButton = document.querySelector("#close-group-name-modal");
// Знаходимо кнопку скасування створення групи.
const cancelGroupModalButton = document.querySelector("#cancel-group-modal");
// Знаходимо кнопку переходу до другого кроку.
const nextGroupStepButton = document.querySelector("#next-group-step");
// Знаходимо кнопку повернення до вибору друзів.
const backGroupStepButton = document.querySelector("#back-group-step");
// Знаходимо кнопку фінального створення групи.
const createGroupButton = document.querySelector("#create-group");
// Знаходимо поле назви групового чату.
const groupNameInput = document.querySelector("#group-name");
// Знаходимо лічильник вибраних друзів.
const selectedCount = document.querySelector("#selected-count");
// Знаходимо блок, куди показуємо вибраних учасників на другому кроці.
const selectedUsersList = document.querySelector("#selected-users-list");
// Знаходимо всі чекбокси друзів у модальному вікні.
const groupUserCheckboxes = document.querySelectorAll(".group-user-checkbox");
// Знаходимо список груп у правому блоці сторінки.
const groupList = document.querySelector("#group-list");

// Відкриваємо модальне вікно на першому кроці.
function openGroupModal() {
    groupModal.hidden = false
    groupStepUsers.hidden = false
    groupStepName.hidden = true
}
// Закриваємо модальне вікно й очищаємо введені дані.
function closeGroupModal() {
    groupModal.hidden = true
    groupNameInput.value = ""
    selectedUsersList.innerHTML = ""
    groupUserCheckboxes.forEach((checkbox) => {
        checkbox.checked = false
    })
    updateSelectedCount()
}
// Оновлюємо кількість вибраних друзів у модальному вікні.
function updateSelectedCount() {
    const count = document.querySelectorAll(".group-user-checkbox:checked").length
    selectedCount.textContent = count
}
// Показуємо вибраних друзів на другому кроці перед створенням групи.
function renderSelectedUsers() {
    selectedUsersList.innerHTML = ""

    groupUserCheckboxes.forEach((checkbox) => {
        if (checkbox.checked) {
            const user = document.createElement("p")
            user.textContent = checkbox.dataset.userName

            selectedUsersList.appendChild(user)
        }
    })
}

// Переходимо з вибору друзів до введення назви групи.
function showNameStep() {
    renderSelectedUsers()

    groupStepUsers.hidden = true
    groupStepName.hidden = false
}

// Повертаємося з другого кроку до вибору друзів.
function showUsersStep() {
    groupStepUsers.hidden = false
    groupStepName.hidden = true
}

// Додаємо створену групу в правий блок без перезавантаження сторінки.
function addGroupButton(chatId, name) {
    const groupEmpty = document.querySelector("#group-empty")
    if (groupEmpty) {
        groupEmpty.remove()
    }
    const button = document.createElement("button")
    button.type = 'button'
    button.className = "chat-group-button"
    button.dataset.chatId = chatId
    button.dataset.chatTitle = name
    groupList.appendChild(button)
    window.bindGroupChatButtons()
}

// Створюємо груповий чат на backend.
async function createGroup() {
    const formData = new FormData()
    formData.append("name", groupNameInput.value)
    groupUserCheckboxes.forEach((checkbox) => {
        if (checkbox.checked) {
            formData.append("users", checkbox.value)
        }
    })
    const response = await fetch(
        "/chat/create_group/",
        {
            method: "POST",
            headers: {
                "X-CSRFToken": csrfToken
            },
            body: formData
        }
    )
    const data = await response.json()
    if (!data.success) {
        return
    }
    addGroupButton(data.chat_id, data.name)
    closeGroupModal()
}
// Вішаємо відкриття модального вікна на кнопку створення групи.
openGroupModalButton.addEventListener("click", openGroupModal);
// Вішаємо закриття першого кроку.
closeGroupModalButton.addEventListener("click", closeGroupModal);
// Вішаємо закриття другого кроку.
closeGroupNameModalButton.addEventListener("click", closeGroupModal);
// Вішаємо скасування створення групи.
cancelGroupModalButton.addEventListener("click", closeGroupModal);
// Вішаємо перехід до кроку з назвою.
nextGroupStepButton.addEventListener("click", showNameStep);
// Вішаємо повернення до вибору друзів.
backGroupStepButton.addEventListener("click", showUsersStep);
// Вішаємо створення групи.
createGroupButton.addEventListener("click", createGroup);
// Оновлюємо лічильник при кожній зміні чекбокса друга.
groupUserCheckboxes.forEach((checkbox) => {
    // Реагуємо на вибір або зняття вибору друга.
    checkbox.addEventListener("change", updateSelectedCount);
});
