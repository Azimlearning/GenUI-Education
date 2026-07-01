// 1. Select the necessary elements from the HTML
const tabs = document.querySelectorAll('.tab');
const appWrapper = document.querySelector('.app-wrapper');
const chatHistory = document.querySelector('.chat-history');

// 2. Updated subject configurations with semantic theme names
const subjectConfig = {
    'Physics': {
        theme: 'theme-physics',
        welcomeMessage: "Hello! I'm your SPM Science Tutor. Ask me a question about Physics!"
    },
    'Chemistry': {
        theme: 'theme-chemistry',
        welcomeMessage: "Hello! I'm your SPM Science Tutor. Ask me a question about Chemistry!"
    },
    'Biology': {
        theme: 'theme-biology',
        welcomeMessage: "Hello! I'm your SPM Science Tutor. Ask me a question about Biology!"
    }
};

// 3. Add click events to switch subjects
tabs.forEach(tab => {
    tab.addEventListener('click', function() {
        const subjectName = this.textContent.trim();
        const config = subjectConfig[subjectName];

        if (config) {
            // A. Update active tab styling
            tabs.forEach(t => t.classList.remove('active'));
            this.classList.add('active');

            // B. Change the theme color using the new subject classes
            appWrapper.classList.remove('theme-biology', 'theme-chemistry', 'theme-physics');
            appWrapper.classList.add(config.theme);

            // C. Update chat welcome message
            chatHistory.innerHTML = `
                <div class="message ai-message">
                    ${config.welcomeMessage}
                </div>
            `;
            
            // D. Clear the visualizer panel
            const visualizerPanel = document.querySelector('.visualizer-panel');
            if (visualizerPanel) {
                visualizerPanel.innerHTML = ''; 
            }
        }
    });
});