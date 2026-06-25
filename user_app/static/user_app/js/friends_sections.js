// Знаходимо головну вкладку з трьома блоками.
const homeBlock = document.querySelector("#friends-home");
// Знаходимо контейнер повної вкладки.
const sectionBlock = document.querySelector("#friends-section");
// Знаходимо заголовок повної вкладки.
const sectionTitle = document.querySelector("#friends-section-title");
// Знаходимо список карток повної вкладки.
const sectionList = document.querySelector("#friends-section-list");
// Знаходимо sentinel для порційного підвантаження людей.
const friendsSentinel = document.querySelector("#friends-load-sentinel");
// Знаходимо кнопку повернення на головну вкладку.
const backHomeButton = document.querySelector("#friends-back-home");
// Зберігаємо назви вкладок для заголовка.
const sectionTitles = {
  requests: "Запити",
  recommendations: "Рекомендації",
  friends: "Всі друзі",
};
// Зберігаємо активну секцію.
let currentSection = "";
// Зберігаємо поточну сторінку активної секції.
let currentPage = 1;
// Запам'ятовуємо, чи є наступна порція людей.
let hasNext = false;
// Захищаємося від одночасних fetch-запитів.
let isLoading = false;

// Завантажуємо одну порцію людей для активної секції.
async function loadSectionPage(section, page) {
  // Позначаємо початок завантаження.
  isLoading = true;
  // Запитуємо одну сторінку карток вибраної секції.
  const response = await fetch(`/friends/${section}/?page=${page}`, {
    headers: { "X-Requested-With": "XMLHttpRequest" },
  });
  // Перетворюємо відповідь сервера у JSON.
  const data = await response.json();
  // Додаємо отримані картки в кінець списку.
  sectionList.insertAdjacentHTML("beforeend", data.html);
  // Запам'ятовуємо, чи є ще наступна сторінка.
  hasNext = data.has_next;
  // Підключаємо слухачі до кнопок у щойно завантаженій порції.
  window.connectFriendActionButtons(sectionList);
  // Позначаємо завершення завантаження.
  isLoading = false;
}

// Функція відкриває повну вкладку без перезавантаження сторінки.
async function openSection(section) {
  // Запам'ятовуємо активну секцію.
  currentSection = section;
  // Починаємо кожну секцію з першої сторінки.
  currentPage = 1;
  // Скидаємо ознаку наступної сторінки перед новим запитом.
  hasNext = false;
  // Ставимо заголовок відповідно до вибраної вкладки.
  sectionTitle.textContent = sectionTitles[section];
  // Очищаємо попередні картки перед новим списком.
  sectionList.innerHTML = "";
  // Ховаємо головну вкладку з трьома короткими блоками.
  homeBlock.style.display = "none";
  // Показуємо повну вкладку.
  sectionBlock.style.display = "block";
  // Завантажуємо перші 6 людей вибраної секції.
  await loadSectionPage(section, currentPage);
}

// Функція повертає користувача на головну вкладку.
function openHome() {
  // Ховаємо повну вкладку.
  sectionBlock.style.display = "none";
  // Очищаємо повний список, щоб не змішувати старі картки з новими.
  sectionList.innerHTML = "";
  // Скидаємо активну секцію.
  currentSection = "";
  // Скидаємо ознаку наступної сторінки.
  hasNext = false;
  // Показуємо головну вкладку з трьома блоками.
  homeBlock.style.display = "block";
}

// Стежимо за sentinel і довантажуємо наступну порцію людей.
const friendsObserver = new IntersectionObserver(async (entries) => {
  // Перевіряємо, чи sentinel видимий і чи можна вантажити наступну сторінку.
  if (entries[0].isIntersecting && hasNext && isLoading == false) {
    // Переходимо до наступної сторінки.
    currentPage++;
    // Завантажуємо наступні 6 людей активної секції.
    await loadSectionPage(currentSection, currentPage);
  }
}, { rootMargin: "200px" });

// Починаємо стежити за sentinel повної вкладки.
friendsObserver.observe(friendsSentinel);

// Вішаємо повернення на кнопку головної вкладки.
backHomeButton.addEventListener("click", openHome);

// Знаходимо всі кнопки переходу між секціями.
const sectionButtons = document.querySelectorAll("[data-section-link]");

// Проходимо по кожній кнопці секції.
sectionButtons.forEach((sectionButton) => {
  // Вішаємо слухач кліку на конкретну кнопку.
  sectionButton.addEventListener("click", async () => {
    // Відкриваємо першу порцію карток вибраної вкладки.
    await openSection(sectionButton.dataset.sectionLink);
  });
});
