const socket = new WebSocket(`wss://${window.location.host}/status/`)
const status = []

socket.onopen(() => {
    const userIds = []
    socket.send(JSON.stringify({
        action: "getStatuses",
        user_ids: userIds
    }))
})

socket.onmessage((event) => {
    const data = JSON.parse(event.data)
    if (data.type === "statuses") {
        
    }

})