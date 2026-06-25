import { renderMessageImages, hasMessageImages, hasSelectedImages, clearSelectedImages, getSelectedImages } from "./loadImages.js";
// Зберігаємо поточне WebSocket-з'єднання.
let chatSocket = null;
// // Зберігаємо id відкритого чату.
let activeChatId = null;
// // Зберігаємо номер сторінки історії.
let currentPage = 1;
// // Зберігаємо прапорець завантаження.
let isLoading = false;
// // Зберігаємо прапорець наявності старіших повідомлень.
let hasNext = false;
// // Зберігаємо observer для верхнього sentinel.
let observer = null;

// // Беремо CSRF-токен для POST-запиту.
const csrfToken = document.querySelector("meta[name='csrf-token']").content;
// // Робимо CSRF-токен доступним для group_chat.js, який створює групи через POST-запит.
window.csrfToken = csrfToken;
// Знаходимо заголовок чату.
const chatTitle = document.querySelector("#chat-title");
// Знаходимо стартовий статус.
const chatStatus = document.querySelector("#chat-status");
// Знаходимо кнопки відкриття чатів.
const chatButtons = document.querySelectorAll("[data-chat-user]");
// Знаходимо вікно чату.
const chatWindow = document.querySelector("#chat-window");
// Знаходимо блок повідомлень.
const messages = document.querySelector("#messages");
// Знаходимо форму повідомлення.
const messageForm = document.querySelector("#message-form");
// Знаходимо поле вводу.
const messageInput = document.querySelector("#message-input");

const messageImagesInput = document.getElementById("message-images")
const messageImageButton = document.getElementById("message-image-button")

// Створюємо HTML для одного повідомлення.
function renderMessage(data) {
    // Створюємо блок повідомлення.
    const message = document.createElement("div");
    // Додаємо клас повідомлення.
    message.className = "message";
    // Записуємо автора і текст.
    message.textContent = `${data.sender}: ${data.text}`;
    if(hasMessageImages(data)){
        message.appendChild(renderMessageImages(data.images))
    }
    // Повертаємо готовий блок.
    return message;
}

// Готуємо блок повідомлень до нового чату.
function resetMessages(chatId) {
    // Запам'ятовуємо активний чат.
    activeChatId = chatId;
    // Починаємо з першої сторінки.
    currentPage = 1;
    // Дозволяємо перше завантаження.
    hasNext = true;
    // Скидаємо прапорець завантаження.
    isLoading = false;
    // Вимикаємо старий observer.
    if (observer) observer.disconnect();
    // Очищаємо попередній чат.
    messages.innerHTML = "";
    // Створюємо верхній sentinel.
    const sentinel = document.createElement("div");
    // Даємо sentinel id.
    sentinel.id = "message-load-sentinel";
    // Додаємо sentinel на початок.
    messages.prepend(sentinel);
}

// Завантажуємо одну сторінку історії.
async function loadMessages(prepend = false) {
    // Не запускаємо друге завантаження паралельно.
    if (isLoading || !hasNext) return;
    // Позначаємо початок завантаження.
    isLoading = true;
    // Запам'ятовуємо стару висоту списку.
    const oldHeight = messages.scrollHeight;
    // Запитуємо сторінку історії.
    const response = await fetch(`/chat/${activeChatId}/messages/?page=${currentPage}`, {
        // Позначаємо AJAX-запит.
        headers: { "X-Requested-With": "XMLHttpRequest" },
    });
    // Читаємо JSON-відповідь.
    const data = await response.json();
    // Створюємо тимчасовий контейнер для повідомлень.
    const fragment = document.createDocumentFragment();
    // Додаємо повідомлення у контейнер.
    data.messages.forEach((message) => fragment.appendChild(renderMessage(message)));
    // Знаходимо верхній sentinel.
    const sentinel = document.querySelector("#message-load-sentinel");
    // Перевіряємо, чи треба вставити повідомлення зверху.
    if (prepend) {
        // Вставляємо старі повідомлення після sentinel.
        sentinel.after(fragment);
    // Інакше це перше завантаження історії.
    } else {
        // Вставляємо останні повідомлення в кінець списку.
        messages.appendChild(fragment);
    }
    // Запам'ятовуємо, чи є наступна сторінка.
    hasNext = data.has_next;
    // Переходимо до наступної сторінки.
    currentPage++;
    // Перевіряємо, чи повідомлення вставлялися зверху.
    if (prepend) {
        // Зберігаємо позицію після вставки старої історії.
        messages.scrollTop = messages.scrollHeight - oldHeight;
    // Інакше це перше завантаження історії.
    } else {
        // Прокручуємо чат до останнього повідомлення.
        messages.scrollTop = messages.scrollHeight;
    }
    // Зупиняємо observer, якщо сторінок більше немає.
    if (!hasNext && observer) observer.disconnect();
    // Дозволяємо наступне завантаження.
    isLoading = false;
}

// Вмикаємо observer для підвантаження старих повідомлень.
function startObserver() {
    // Знаходимо верхній sentinel.
    const sentinel = document.querySelector("#message-load-sentinel");
    // Створюємо observer як у підвантаженні постів.
    observer = new IntersectionObserver(async (entries) => {
        // Перевіряємо, що sentinel видно.
        if (entries[0].isIntersecting && isLoading == false) {
            // Завантажуємо старішу сторінку.
            await loadMessages(true);
        }
    // Обмежуємо observer блоком повідомлень.
    }, { root: messages, rootMargin: "20px" });
    // Починаємо стежити за sentinel.
    observer.observe(sentinel);
}

// Відкриваємо будь-який чат за id і назвою: цю функцію використовують кнопки груп.
async function openChatById(chatId, title) {
    // Показуємо назву вибраного чату в центральному блоці.
    chatTitle.textContent = title;
    // Відкриваємо вікно переписки.
    chatWindow.classList.add("is-open");
    // Ховаємо стартовий статус після вибору чату.
    chatStatus.hidden = true;
    // Готуємо контейнер повідомлень до завантаження історії цього чату.
    resetMessages(chatId);
    // Підключаємо WebSocket до вибраного чату.
    connectWebSocket(chatId);
    // Завантажуємо останні повідомлення вибраного чату.
    await loadMessages();
    // Вмикаємо підвантаження старіших повідомлень при прокрутці вгору.
    startObserver();
}

// Створюємо або відкриваємо чат з конкретним користувачем.
async function openChatWithUser(userId, username) {
    // Надсилаємо POST-запит на backend.
    const response = await fetch(`/chat/chat_with/${userId}/`, { method: "POST", headers: { "X-CSRFToken": csrfToken } });
    // Читаємо JSON-відповідь.
    const data = await response.json();
    // Зупиняємо роботу, якщо чат недоступний.
    if (!data.success) return;
    // Відкриваємо особистий чат через спільну функцію, яку також використовують групи.
    await openChatById(data.chat_id, `Чат з ${data.username || username}`);
}

// Створюємо WebSocket-з'єднання з чатом.
function connectWebSocket(chatId) {
    // Закриваємо попередній WebSocket.
    if (chatSocket) chatSocket.close();
    // Відкриваємо WebSocket поточного чату.
    chatSocket = new WebSocket(`ws://${window.location.host}/chat/${chatId}/`);
    // Обробляємо нове повідомлення.
    chatSocket.onmessage = function(event) {
        // Читаємо JSON з WebSocket.
        const data = JSON.parse(event.data);
        // Додаємо повідомлення вниз.
        messages.appendChild(renderMessage(data));
        // Прокручуємо чат до останнього повідомлення.
        messages.scrollTop = messages.scrollHeight;
    };
}

// Проходимося по кнопках користувачів.
chatButtons.forEach((button) => {
    // Вішаємо click-обробник.
    button.addEventListener("click", async () => {
        // Відкриваємо чат з вибраним користувачем.
        await openChatWithUser(button.dataset.chatUser, button.dataset.chatUsername);
    });
});

// Підключаємо вже наявні кнопки групових чатів у правому блоці.
function bindGroupChatButtons() {
    const groupButtons = document.querySelectorAll("[data-chat-id]")

    groupButtons.forEach((button) => {
        if (button.dataset.groupBound == "true") {
            return
        } 
        button.dataset.groupBound = "true"
        button.addEventListener("click", async () => {
            await openChatById(button.dataset.chatId, button.dataset.chatTitle)
        })
    })
}
// Робимо функцію відкриття чату доступною для group_chat.js після створення нової групи.
window.openChatById = openChatById
// Робимо повторне підключення кнопок груп доступним для group_chat.js.
window.bindGroupChatButtons = bindGroupChatButtons
// Підключаємо кнопки груп, які вже були відрендерені на сторінці.
bindGroupChatButtons()

// Вiдправляємо повiдомлення iз зображеннями через HTTP Upload EndPoint
export async function sendMessageWithImages(text){
    const formData = new FormData()
    formData.append("text", text)

    getSelectedImages().forEach((image) => {
        formData.append("images", image)
    })
    const response = await fetch(
        `/chat/${activeChatId}/messages/upload/`,
        {
            method: "POST",
            headers: { "X-CSRFToken": csrfToken },
            body: formData
        }
    )
    return response.json()
}
// Як тiльки ми будемо клiкати по кнопцi, ми вiдкриємо панель завантаження зображень
messageImageButton.addEventListener(
    'click',
    function(){
        messageImagesInput.click()
    }
)

// Обробляємо відправку форми.
messageForm.addEventListener("submit", async function(event) {
    // Забороняємо перезавантаження сторінки.
    event.preventDefault();
    // Беремо текст повідомлення.
    const text = messageInput.value.trim();
    // Нічого не робимо без тексту.
    if (!text && !hasSelectedImages()) return;
    if (hasSelectedImages()){
        const data = await sendMessageWithImages(text)
        if (!data.success) return;
        messageInput.value = ""
        clearSelectedImages()
        return
    }
    // Надсилаємо повідомлення через WebSocket.
    chatSocket.send(JSON.stringify({ text: text }));
    // Очищаємо поле вводу.
    messageInput.value = "";
});
