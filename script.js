const chatBody = document.getElementById('chat-body');
const userInput = document.getElementById('user-input');
const sendBtn = document.getElementById('send-btn');

const appendMessage = (message, sender) => {
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${sender}`;
    messageDiv.textContent = message;
    chatBody.appendChild(messageDiv);
    chatBody.scrollTop = chatBody.scrollHeight; 
};

const fetchAIResponse = async (userMessage) => {
    try {
        const response = await fetch('http://127.0.0.1:5000/predict', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ keyword: userMessage }),
        });

        const data = await response.json();

        const botMessage = data.response || "Bilinmeyen bir hata oluştu.";
        appendMessage(botMessage, 'bot');

        if (data.courses && data.courses.length > 0) {
            data.courses.forEach(course => {
                appendMessage(`Başlık: ${course.title}`, 'bot');
                appendMessage(`Kategori: ${course.Kategori}`, 'bot');
                appendMessage(`Süre: ${course.Süre}`, 'bot');
                appendMessage(`Seviye: ${course.Seviye}`, 'bot');
            });
        } else {
            appendMessage('Eğitim bulunamadı. Anahtar kelimenizi gözden geçirin.', 'bot');
        }
    } catch (error) {
        console.error('Hata oluştu:', error);
        appendMessage('Bir hata oluştu. Lütfen tekrar deneyin.', 'bot');
    }
};

sendBtn.addEventListener('click', () => {
    const userMessage = userInput.value.trim();
    if (userMessage) {
        appendMessage(userMessage, 'user');
        userInput.value = '';
        fetchAIResponse(userMessage);
    }
});

userInput.addEventListener('keypress', (event) => {
    if (event.key === 'Enter') {
        sendBtn.click();
    }
});
