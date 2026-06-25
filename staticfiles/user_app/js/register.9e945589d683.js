import { showLoginForm} from "./auth.js"
import { renderErrors } from "../../../../static/js/renderErrors.js"
import { getCSRFToken } from "../../../../static/js/getCSRFToken.js"

document.getElementById('register-form').addEventListener(
    'submit',
    function(event){
        event.preventDefault()

        const form = event.target
        const formData = new FormData(form)
        
        fetch(form.action, {
            method: "POST",
            headers: {
                "X-CSRFToken": getCSRFToken(),
                "X-Requested-With": "XMLHttpRequest",
            },
            body: formData
        })
        .then(async response => {
            const data = await response.json()
            if (!response.ok) {
                throw data
            }
            return data
        })
        .then(data => {
            form.reset()
            showLoginForm()
        })
        .catch(data => {
            if(data.errors){
                renderErrors("register-errors", data.errors)
            }
        })
    }
)