/**
 * VARIABLES
 */
// Connect to websockets server
const mySocket = new WebSocket(`${document.body.dataset.scheme === 'http' ? 'ws': 'wss'}://${document.body.dataset.host}/ws/chat/`)

/**
 * FUNCTIONS
 */


/**
 * EVENTS
 */

mySocket.addEventListener("message", (event) => {
    console.log(event.data)
})