async function receive_messages() {
    const response = await fetch("/chat");
    const message = await response.json();
    return message["msg"] 
  }

// while (true) {
//     const message = receive_messages();
    
// }