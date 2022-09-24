/**
 * VARIABLES
 */
// Connect to websockets server
const mySocket = new WebSocket(`${document.body.dataset.scheme === 'http' ? 'ws': 'wss'}://${document.body.dataset.host}/ws/chat/`)

/**
 * FUNCTIONS
 */
/**
 * Send data to WebSockets server
 * @param {string} message
 * @param { WebSocket} WebSocket
 * @return {void}
 */

function sendData(message, webSocket) {
    webSocket.send(JSON.stringify(message))
}

/**
 * Send message to websockets server
 * @param {Event} event
 * @return {void}
 */
function sendNewMessage(event) {
    event.preventDefault()
    const messageText = document.querySelector("#message-text")
    sendData({
        action: 'New message',
        data: {
            message: messageText.value
        }
    }, mySocket)

    messageText.value = ''
}

/**
 * Requests the consumer to change the group with respect to the Dataset group-name
 * @param {Event} event
 * @return {void}
 */

function changeGroup(event) {
    event.preventDefault()
    sendData({
        action: 'Change group',
        data: {
            groupName: event.target.dataset.groupName,
            isGroup: event.target.dataset.groupPublic === 'true'
        }
    }, mySocket)
}

/**
 * EVENTS
 */
// Event when a new message is received by WebSockets
mySocket.addEventListener("message", (event) => {
    // Parse the data received
    const data = JSON.parse(event.data)
    // Renders the HTML received from the Consumer
    document.querySelector(data.selector).innerHTML = data.html
    // Scrolls to the bottom of the chat
    const messagesList = document.querySelector("#messages-list")
    messagesList.scrollTop = messagesList.scrollHeight
})

/**
 * Reassigns the events of the newly rendered HTML
 */
// Button to send ne wmessae button
document.querySelector("#send").addEventListener("click", sendNewMessage)
// Buttons for changing groups
document.querySelectorAll(".nav__link").forEach(button => {
    button.addEventListener("click", changeGroup)
})