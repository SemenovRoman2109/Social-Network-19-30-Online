const messageImagesInput = document.getElementById("message-images")
const messageImageButton = document.getElementById("message-image-button")
// 
export function hasMessageImages(data){
    return Array.isArray(data.images) && data.images.length > 0
}
// 
export function renderMessageImages(images){
    const imageList = document.createElement("div")
    imageList.className = "message-images"

    images.forEach((imageUrl) => {
        const image = document.createElement("img")
        image.src = imageUrl
        image.alt = "Зображення в повідомленні"
        imageList.appendChild(image)

    });
    return imageList
}
// Поверта
// Возвращение массива выбранных изображений
export function getSelectedImages(){
    return Array.from(messageImagesInput.files)
}
// Перевiряємо чи користувач обрав хочаб одне зображення
export function hasSelectedImages(){
    return getSelectedImages().length > 0
}
// Очищаємо вибраннi зображення пiсля успiшноЇ вiдправки
export function clearSelectedImages(){
    messageImagesInput.value = ""
}
