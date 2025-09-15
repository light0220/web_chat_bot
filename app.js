// 全局变量
let currentConfig = {};
let chatHistory = [];

// DOM元素
const chatMessages = document.getElementById('chat-messages');
const userInput = document.getElementById('user-input');
const sendBtn = document.getElementById('send-btn');
const resetBtn = document.getElementById('reset-btn');
const configBtn = document.getElementById('config-btn');
const configPanel = document.getElementById('config-panel');
const saveConfigBtn = document.getElementById('save-config');
const cancelConfigBtn = document.getElementById('cancel-config');

// 配置表单元素（仅包含用户可修改的字段）
const botNameInput = document.getElementById('bot-name');
const botRoleInput = document.getElementById('bot-role');
const welcomeWordsInput = document.getElementById('welcome-words');
const modelNameInput = document.getElementById('model-name');

// 初始化
document.addEventListener('DOMContentLoaded', async () => {
    // 加载配置
    await loadConfig();
    
    // 加载后端保存的聊天历史
    await loadChatHistoryFromServer();
    
    // 只有当没有历史记录且有欢迎语时显示
    const isHistoryEmpty = Array.isArray(chatHistory) && chatHistory.length === 0;
    const hasValidWelcomeWords = typeof currentConfig.welcome_words === 'string' && currentConfig.welcome_words.trim() !== '';
    
    if (isHistoryEmpty && hasValidWelcomeWords) {
        addMessage('bot', currentConfig.welcome_words, false);
    }
    
    // 设置事件监听器
    setupEventListeners();
});

// 加载配置
async function loadConfig() {
    try {
        const response = await fetch('/get_config');
        if (!response.ok) {
            throw new Error('配置请求失败');
        }
        currentConfig = await response.json();
        // 确保配置字段存在
        currentConfig = {
            bot_name: currentConfig.bot_name || '文心一言',
            bot_role: currentConfig.bot_role || '我是一个AI助手',
            welcome_words: currentConfig.welcome_words || '',
            model_name_text_generate: currentConfig.model_name_text_generate || 'ernie-4.5-turbo-128k',
            sensitive_words: currentConfig.sensitive_words || [] // 保留但不显示
        };
        updateConfigForm();
    } catch (error) {
        console.error('加载配置失败:', error);
        currentConfig = {
            bot_name: '文心一言',
            bot_role: '我是一个AI助手',
            welcome_words: '欢迎使用聊天机器人！',
            model_name_text_generate: 'ernie-4.5-turbo-128k',
            sensitive_words: []
        };
    }
}

// 从后端加载聊天历史
async function loadChatHistoryFromServer() {
    try {
        const response = await fetch('/get_chat_history');
        if (!response.ok) {
            throw new Error('历史记录请求失败');
        }
        const data = await response.json();
        chatHistory = Array.isArray(data.history) ? data.history : [];
        
        // 显示历史记录
        chatHistory.forEach(item => {
            addMessage(item.sender, item.text, false);
        });
    } catch (error) {
        console.error('加载聊天历史失败:', error);
        chatHistory = [];
    }
}

// 更新配置表单（仅更新用户可修改的字段）
function updateConfigForm() {
    botNameInput.value = currentConfig.bot_name || '';
    botRoleInput.value = currentConfig.bot_role || '';
    welcomeWordsInput.value = currentConfig.welcome_words || '';
    modelNameInput.value = currentConfig.model_name_text_generate || '';
}

// 设置事件监听器
function setupEventListeners() {
    // 发送消息
    sendBtn.addEventListener('click', sendMessage);
    userInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') sendMessage();
    });
    
    // 重置聊天
    resetBtn.addEventListener('click', resetChat);
    
    // 配置面板
    configBtn.addEventListener('click', () => {
        configPanel.classList.add('active');
    });
    
    saveConfigBtn.addEventListener('click', saveConfig);
    cancelConfigBtn.addEventListener('click', () => {
        configPanel.classList.remove('active');
    });
}

// 发送消息
async function sendMessage() {
    const message = userInput.value.trim();
    if (!message) return;
    
    // 添加用户消息到聊天界面
    addMessage('user', message);
    userInput.value = '';
    
    try {
        const response = await fetch('/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ message: message })
        });
        
        const data = await response.json();
        
        if (data.response) {
            addMessage('bot', data.response);
        }
    } catch (error) {
        console.error('发送消息失败:', error);
        addMessage('bot', '抱歉，发送消息时出现错误');
    }
}

// 添加消息到聊天界面
function addMessage(sender, text, save = true) {
    const messageDiv = document.createElement('div');
    messageDiv.classList.add('message', `${sender}-message`);
    messageDiv.textContent = text;
    chatMessages.appendChild(messageDiv);
    
    // 滚动到底部
    chatMessages.scrollTop = chatMessages.scrollHeight;
    
    // 保存到本地内存中的聊天历史
    if (save) {
        chatHistory.push({
            sender: sender,
            text: text,
            timestamp: new Date().toISOString()
        });
    }
}

// 重置聊天
function resetChat() {
    chatMessages.innerHTML = '';
    chatHistory = [];
    
    // 发送重置请求到后端
    fetch('/reset_chat', {
        method: 'POST'
    });
    
    // 重新显示欢迎消息
    if (currentConfig.welcome_words && currentConfig.welcome_words.trim() !== '') {
        addMessage('bot', currentConfig.welcome_words, false);
    }
}

// 保存配置（只传递用户可修改的字段）
async function saveConfig() {
    // 只包含用户可修改的配置项，不涉及敏感词和API密钥
    const newConfig = {
        bot_name: botNameInput.value.trim(),
        bot_role: botRoleInput.value.trim(),
        welcome_words: welcomeWordsInput.value.trim(),
        model_name_text_generate: modelNameInput.value.trim()
    };
    
    try {
        const response = await fetch('/save_config', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(newConfig)
        });
        
        if (response.ok) {
            // 合并新配置，保留原有敏感词
            currentConfig = { ...currentConfig, ...newConfig };
            configPanel.classList.remove('active');
            resetChat();
        } else {
            alert('保存配置失败');
        }
    } catch (error) {
        console.error('保存配置失败:', error);
        alert('保存配置时出现错误');
    }
}
    