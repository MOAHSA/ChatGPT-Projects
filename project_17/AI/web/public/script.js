// Application State
const state = {
    language: 'ar',
    darkMode: false,
    fontSettings: {
        family: 'Segoe UI',
        size: '16px',
        bold: false,
        italic: false
    },
    colorSettings: {
        text: '#333333',
        background: '#ffffff'
    },
    prompts: [],
    selectedPrompts: new Set()
};

// DOM Elements
const elements = {
    languageToggle: document.getElementById('languageToggle'),
    themeToggle: document.getElementById('themeToggle'),
    mainMessage: document.getElementById('mainMessage'),
    previewText: document.getElementById('previewText'),
    lineNumbers: document.getElementById('lineNumbers'),
    charCount: document.getElementById('charCount'),
    generateBtn: document.getElementById('generateBtn'),
    copyBtn: document.getElementById('copyBtn'),
    promptsContainer: document.getElementById('promptsContainer'),
    settingsModal: document.getElementById('settingsModal'),
    helpModal: document.getElementById('helpModal'),
    fontFamily: document.getElementById('fontFamily'),
    fontSize: document.getElementById('fontSize'),
    boldCheck: document.getElementById('boldCheck'),
    italicCheck: document.getElementById('italicCheck'),
    textColor: document.getElementById('textColor'),
    bgColor: document.getElementById('bgColor'),
    darkModeCheck: document.getElementById('darkModeCheck'),
    settingsPreview: document.getElementById('settingsPreview')
};

// Add Google Translate API
const GOOGLE_TRANSLATE_API_KEY = 'YOUR_API_KEY'; // يجب استبدالها بمفتاح API الخاص بك

// Function to translate text using Google Translate API
async function translateText(text, targetLang = 'en') {
    try {
        const response = await fetch(`https://translation.googleapis.com/language/translate/v2?key=${GOOGLE_TRANSLATE_API_KEY}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                q: text,
                target: targetLang,
                source: 'ar'
            })
        });

        const data = await response.json();
        if (data.data && data.data.translations && data.data.translations[0]) {
            return data.data.translations[0].translatedText;
        }
        throw new Error('Translation failed');
    } catch (error) {
        console.error('Translation error:', error);
        return text; // Return original text if translation fails
    }
}

// Initialize Application
function init() {
    loadSettings();
    setupEventListeners();
    loadPrompts();
    updateUI();
}

// Load Settings from localStorage
function loadSettings() {
    const savedSettings = localStorage.getItem('appSettings');
    if (savedSettings) {
        const settings = JSON.parse(savedSettings);
        state.language = settings.language || 'ar';
        state.darkMode = settings.darkMode || false;
        state.fontSettings = settings.fontSettings || state.fontSettings;
        state.colorSettings = settings.colorSettings || state.colorSettings;
    }
}

// Save Settings to localStorage
function saveSettings() {
    const settings = {
        language: state.language,
        darkMode: state.darkMode,
        fontSettings: state.fontSettings,
        colorSettings: state.colorSettings
    };
    localStorage.setItem('appSettings', JSON.stringify(settings));
}

// Setup Event Listeners
function setupEventListeners() {
    // Language Toggle
    elements.languageToggle.addEventListener('click', async () => {
        state.language = state.language === 'ar' ? 'en' : 'ar';
        document.documentElement.lang = state.language;
        document.documentElement.dir = state.language === 'ar' ? 'rtl' : 'ltr';

        // Translate main message if switching to English
        if (state.language === 'en' && elements.mainMessage.value.trim()) {
            const translatedText = await translateText(elements.mainMessage.value);
            elements.mainMessage.value = translatedText;
        }

        updateUI();
        saveSettings();
    });

    // Theme Toggle
    elements.themeToggle.addEventListener('click', () => {
        state.darkMode = !state.darkMode;
        document.body.setAttribute('data-theme', state.darkMode ? 'dark' : 'light');
        elements.themeToggle.textContent = state.darkMode ? '☀️' : '🌙';
        saveSettings();
    });

    // Main Message Input
    elements.mainMessage.addEventListener('input', () => {
        updateLineNumbers();
        updateCharCount();
    });

    // Generate Button
    elements.generateBtn.addEventListener('click', generateFinalPrompt);

    // Copy Button
    elements.copyBtn.addEventListener('click', () => {
        copyToClipboard(elements.previewText.value);
    });

    // Settings Modal
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            switchSettingsTab(btn.dataset.tab);
        });
    });

    // Font Settings
    elements.fontFamily.addEventListener('change', updateFontSettings);
    elements.fontSize.addEventListener('change', updateFontSettings);
    elements.boldCheck.addEventListener('change', updateFontSettings);
    elements.italicCheck.addEventListener('change', updateFontSettings);

    // Color Settings
    elements.textColor.addEventListener('change', updateColorSettings);
    elements.bgColor.addEventListener('change', updateColorSettings);

    // Dark Mode Checkbox
    elements.darkModeCheck.addEventListener('change', () => {
        state.darkMode = elements.darkModeCheck.checked;
        document.body.setAttribute('data-theme', state.darkMode ? 'dark' : 'light');
        saveSettings();
    });

    // Close Modals
    document.querySelectorAll('.close').forEach(closeBtn => {
        closeBtn.addEventListener('click', () => {
            elements.settingsModal.style.display = 'none';
            elements.helpModal.style.display = 'none';
        });
    });

    // Toolbar Actions
    document.querySelectorAll('.tool-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            const action = btn.dataset.action;
            switch (action) {
                case 'selectAll':
                    elements.mainMessage.select();
                    break;
                case 'copy':
                    copyToClipboard(elements.mainMessage.value);
                    break;
                case 'cut':
                    copyToClipboard(elements.mainMessage.value);
                    elements.mainMessage.value = '';
                    updateLineNumbers();
                    updateCharCount();
                    break;
                case 'paste':
                    navigator.clipboard.readText().then(text => {
                        elements.mainMessage.value = text;
                        updateLineNumbers();
                        updateCharCount();
                    });
                    break;
                case 'clear':
                    elements.mainMessage.value = '';
                    updateLineNumbers();
                    updateCharCount();
                    break;
            }
        });
    });
}

// Update UI Elements
function updateUI() {
    // Update Language
    elements.languageToggle.textContent = state.language === 'ar' ? 'English' : 'العربية';
    document.querySelectorAll('[data-ar]').forEach(element => {
        const text = state.language === 'ar' ? element.dataset.ar : element.dataset.en;
        if (element.tagName === 'INPUT' && element.type === 'button') {
            element.value = text;
        } else {
            element.textContent = text;
        }
    });

    // Update Theme
    document.body.setAttribute('data-theme', state.darkMode ? 'dark' : 'light');
    elements.themeToggle.textContent = state.darkMode ? '☀️' : '🌙';

    // Update Font Settings
    elements.fontFamily.value = state.fontSettings.family;
    elements.fontSize.value = state.fontSettings.size;
    elements.boldCheck.checked = state.fontSettings.bold;
    elements.italicCheck.checked = state.fontSettings.italic;

    // Update Color Settings
    elements.textColor.value = state.colorSettings.text;
    elements.bgColor.value = state.colorSettings.background;

    // Update Dark Mode Checkbox
    elements.darkModeCheck.checked = state.darkMode;
}

// Update Line Numbers
function updateLineNumbers() {
    const lines = elements.mainMessage.value.split('\n');
    elements.lineNumbers.innerHTML = lines.map((_, i) => i + 1).join('\n');
}

// Update Character Count
function updateCharCount() {
    const count = elements.mainMessage.value.length;
    const text = state.language === 'ar' ? `${count} حرف` : `${count} characters`;
    elements.charCount.textContent = text;
}

// Generate Final Prompt
async function generateFinalPrompt() {
    const mainMessage = elements.mainMessage.value.trim();
    if (!mainMessage) {
        const message = state.language === 'ar' ?
            'الرجاء إدخال رسالة رئيسية' :
            'Please enter a main message';
        alert(message);
        return;
    }

    const selectedPrompts = Array.from(state.selectedPrompts)
        .map(id => state.prompts.find(p => p.id === id))
        .filter(Boolean);

    let finalPrompt = '';

    // Add Critical Instructions
    finalPrompt += state.language === 'ar' ?
        'تعليمات هامة:\n' +
        '1. الرسالة الرئيسية أدناه هي محور تركيزك الأساسي\n' +
        '2. استخدم السياق الإضافي فقط لتعزيز فهمك\n' +
        '3. لا تدع السياق الإضافي يشتتك عن المهمة الأساسية\n' +
        '4. أعطِ الأولوية دائمًا لمتطلبات الرسالة الرئيسية\n' +
        '='.repeat(80) + '\n\n' :
        'CRITICAL INSTRUCTIONS:\n' +
        '1. The MAIN MESSAGE below is your PRIMARY focus\n' +
        '2. Use supplementary context ONLY to enhance understanding\n' +
        '3. Do not let supplementary context distract from main task\n' +
        '4. Always prioritize the requirements in the main message\n' +
        '='.repeat(80) + '\n\n';

    // Add Main Message
    finalPrompt += state.language === 'ar' ?
        '🔴 الرسالة الرئيسية (المهمة الأساسية) 🔴\n' +
        '-'.repeat(50) + '\n' +
        mainMessage + '\n' +
        '-'.repeat(50) + '\n\n' :
        '🔴 MAIN MESSAGE (PRIMARY TASK) 🔴\n' +
        '-'.repeat(50) + '\n' +
        mainMessage + '\n' +
        '-'.repeat(50) + '\n\n';

    // Add Selected Prompts
    if (selectedPrompts.length > 0) {
        finalPrompt += state.language === 'ar' ?
            '📚 السياق الإضافي (معلومات داعمة فقط) 📚\n' :
            '📚 SUPPLEMENTARY CONTEXT (Supporting Information Only) 📚\n';

        for (const [index, prompt] of selectedPrompts.entries()) {
            finalPrompt += `\n${state.language === 'ar' ? 'نص مساعد' : 'Supplementary Prompt'} #${index + 1}:\n`;
            finalPrompt += '-'.repeat(40) + '\n';

            // Translate prompt content if in English mode
            let promptContent = prompt.content;
            if (state.language === 'en') {
                promptContent = await translateText(prompt.content);
            }

            finalPrompt += promptContent + '\n';
            finalPrompt += '-'.repeat(40) + '\n';
        }

        // Add Final Reminder
        finalPrompt += '\n' + '='.repeat(80) + '\n';
        finalPrompt += state.language === 'ar' ?
            'تذكير: ركز على الرسالة الرئيسية أعلاه وتأكد من أن إجابتك تعالج متطلباتها بشكل أساسي.\n' :
            'REMINDER: Focus on the MAIN MESSAGE above and ensure your response primarily addresses its requirements.\n';
        finalPrompt += '='.repeat(80) + '\n';
    }

    elements.previewText.value = finalPrompt;
}

// Copy Text to Clipboard
function copyToClipboard(text) {
    navigator.clipboard.writeText(text).then(() => {
        // Show success message
        const message = state.language === 'ar' ? 'تم النسخ بنجاح' : 'Copied successfully';
        alert(message);
    }).catch(err => {
        console.error('Failed to copy text: ', err);
    });
}

// Load Prompts from Data Directory
function loadPrompts() {
    fetch('/Data/prompts.json')
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(data => {
            state.prompts = data;
            renderPrompts();
        })
        .catch(error => {
            console.error('Failed to load prompts:', error);
        });
}

// Render Prompts in UI
function renderPrompts() {
    elements.promptsContainer.innerHTML = '';

    // Group prompts by category
    const categories = {};
    state.prompts.forEach(prompt => {
        if (!categories[prompt.category]) {
            categories[prompt.category] = [];
        }
        categories[prompt.category].push(prompt);
    });

    // Sort categories alphabetically
    const sortedCategories = Object.entries(categories).sort(([a], [b]) => {
        if (state.language === 'ar') {
            return a.localeCompare(b, 'ar');
        }
        return a.localeCompare(b, 'en');
    });

    // Create category sections
    sortedCategories.forEach(([category, prompts]) => {
        const categoryElement = document.createElement('div');
        categoryElement.className = 'prompt-category';

        // Create category header
        const header = document.createElement('div');
        header.className = 'category-header';
        header.innerHTML = `
            <span>${category}</span>
            <span class="category-toggle">▼</span>
        `;

        // Create category content
        const content = document.createElement('div');
        content.className = 'category-content';

        // Sort prompts alphabetically
        prompts.sort((a, b) => {
            if (state.language === 'ar') {
                return a.title.localeCompare(b.title, 'ar');
            }
            return a.title.localeCompare(b.title, 'en');
        });

        // Add prompts to category
        prompts.forEach(prompt => {
            const promptElement = document.createElement('div');
            promptElement.className = 'prompt-item';

            // Create checkbox with unique ID
            const checkboxId = `prompt-${prompt.id.replace(/[^a-zA-Z0-9]/g, '-')}`;

            promptElement.innerHTML = `
                <div class="prompt-controls">
                    <input type="checkbox" id="${checkboxId}" 
                           ${state.selectedPrompts.has(prompt.id) ? 'checked' : ''}>
                    <button class="edit-btn" title="${state.language === 'ar' ? 'تعديل النص' : 'Edit Template'}">✎</button>
                </div>
                <label for="${checkboxId}" title="${prompt.title}">${prompt.title}</label>
            `;

            // Add click event to show preview
            promptElement.addEventListener('click', (e) => {
                if (!e.target.classList.contains('edit-btn') && e.target.type !== 'checkbox') {
                    elements.previewText.value = prompt.content;
                    document.querySelectorAll('.prompt-item').forEach(item => {
                        item.classList.remove('selected');
                    });
                    promptElement.classList.add('selected');
                }
            });

            // Add edit button click event
            promptElement.querySelector('.edit-btn').addEventListener('click', (e) => {
                e.stopPropagation();
                createTemplateEditor(prompt);
            });

            // Add checkbox change event
            promptElement.querySelector('input').addEventListener('change', (e) => {
                if (e.target.checked) {
                    state.selectedPrompts.add(prompt.id);
                } else {
                    state.selectedPrompts.delete(prompt.id);
                }
                if (state.selectedPrompts.size === 0) {
                    elements.previewText.value = '';
                }
            });

            content.appendChild(promptElement);
        });

        // Add toggle functionality
        header.addEventListener('click', () => {
            const isExpanded = content.style.display !== 'none';
            content.style.display = isExpanded ? 'none' : 'grid';
            header.querySelector('.category-toggle').textContent = isExpanded ? '▶' : '▼';

            // Save category state
            const categoryStates = JSON.parse(localStorage.getItem('categoryStates') || '{}');
            categoryStates[category] = !isExpanded;
            localStorage.setItem('categoryStates', JSON.stringify(categoryStates));
        });

        // Restore category state
        const categoryStates = JSON.parse(localStorage.getItem('categoryStates') || '{}');
        if (categoryStates[category] === false) {
            content.style.display = 'none';
            header.querySelector('.category-toggle').textContent = '▶';
        }

        categoryElement.appendChild(header);
        categoryElement.appendChild(content);
        elements.promptsContainer.appendChild(categoryElement);
    });
}

// Switch Settings Tab
function switchSettingsTab(tabName) {
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.classList.toggle('active', btn.dataset.tab === tabName);
    });
    document.querySelectorAll('.tab-pane').forEach(pane => {
        pane.classList.toggle('active', pane.id === tabName + 'Tab');
    });
}

// Update Font Settings
function updateFontSettings() {
    state.fontSettings = {
        family: elements.fontFamily.value,
        size: elements.fontSize.value,
        bold: elements.boldCheck.checked,
        italic: elements.italicCheck.checked
    };
    applyFontSettings();
    saveSettings();
}

// Update Color Settings
function updateColorSettings() {
    state.colorSettings = {
        text: elements.textColor.value,
        background: elements.bgColor.value
    };
    applyColorSettings();
    saveSettings();
}

// Apply Font Settings
function applyFontSettings() {
    const { family, size, bold, italic } = state.fontSettings;
    elements.mainMessage.style.fontFamily = family;
    elements.mainMessage.style.fontSize = size;
    elements.mainMessage.style.fontWeight = bold ? 'bold' : 'normal';
    elements.mainMessage.style.fontStyle = italic ? 'italic' : 'normal';
}

// Apply Color Settings
function applyColorSettings() {
    const { text, background } = state.colorSettings;
    elements.mainMessage.style.color = text;
    elements.mainMessage.style.backgroundColor = background;
}

// Add template editing functionality
function createTemplateEditor(prompt) {
    const modal = document.createElement('div');
    modal.className = 'modal';
    modal.innerHTML = `
        <div class="modal-content template-editor">
            <span class="close">&times;</span>
            <h3>${state.language === 'ar' ? 'تعديل النص' : 'Edit Template'}</h3>
            
            <div class="template-variables">
                <h4>${state.language === 'ar' ? 'أدخل القيم المطلوبة' : 'Enter Required Values'}</h4>
                <div id="variablesList" class="variables-grid"></div>
            </div>

            <div class="template-content">
                <h4>${state.language === 'ar' ? 'معاينة النص' : 'Text Preview'}</h4>
                <textarea id="templateText" rows="10" readonly></textarea>
            </div>

            <div class="template-actions">
                <button class="tool-btn" id="saveTemplate">${state.language === 'ar' ? 'حفظ' : 'Save'}</button>
                <button class="tool-btn" id="resetTemplate">${state.language === 'ar' ? 'إعادة تعيين' : 'Reset'}</button>
                <button class="tool-btn" id="copyTemplate">${state.language === 'ar' ? 'نسخ' : 'Copy'}</button>
            </div>
        </div>
    `;

    document.body.appendChild(modal);
    modal.style.display = 'block';

    // Extract variables from template
    const variables = extractVariables(prompt.content);
    const variablesList = modal.querySelector('#variablesList');
    const templateText = modal.querySelector('#templateText');

    // Create input fields for each variable
    variables.forEach(variable => {
        const variableDiv = document.createElement('div');
        variableDiv.className = 'variable-input';
        variableDiv.innerHTML = `
            <label>${variable}:</label>
            <input type="text" 
                   class="variable-value" 
                   data-variable="${variable}"
                   placeholder="${state.language === 'ar' ? 'أدخل القيمة هنا' : 'Enter value here'}"
                   dir="${state.language === 'ar' ? 'rtl' : 'ltr'}">
        `;
        variablesList.appendChild(variableDiv);
    });

    // Set initial template text
    templateText.value = prompt.content;

    // Handle template editing
    const saveBtn = modal.querySelector('#saveTemplate');
    const resetBtn = modal.querySelector('#resetTemplate');
    const copyBtn = modal.querySelector('#copyTemplate');
    const closeBtn = modal.querySelector('.close');

    // Update template when variables change
    variablesList.querySelectorAll('.variable-value').forEach(input => {
        input.addEventListener('input', () => {
            updateTemplatePreview(templateText, variablesList, prompt.content);
        });
    });

    // Save template
    saveBtn.addEventListener('click', () => {
        const updatedContent = templateText.value;
        prompt.content = updatedContent;
        modal.remove();
        renderPrompts(); // Refresh prompts display
    });

    // Reset template
    resetBtn.addEventListener('click', () => {
        templateText.value = prompt.content;
        variablesList.querySelectorAll('.variable-value').forEach(input => {
            input.value = '';
        });
    });

    // Copy template
    copyBtn.addEventListener('click', () => {
        copyToClipboard(templateText.value);
    });

    // Close modal
    closeBtn.addEventListener('click', () => {
        modal.remove();
    });

    // Close modal when clicking outside
    modal.addEventListener('click', (e) => {
        if (e.target === modal) {
            modal.remove();
        }
    });
}

// Extract variables from template text
function extractVariables(text) {
    const variableRegex = /\[([^\]]+)\]/g;
    const variables = new Set();
    let match;

    while ((match = variableRegex.exec(text)) !== null) {
        variables.add(match[1]);
    }

    return Array.from(variables);
}

// Update template preview with variable values
function updateTemplatePreview(templateText, variablesList, originalContent) {
    let content = originalContent;
    const variables = variablesList.querySelectorAll('.variable-value');

    variables.forEach(input => {
        const variable = input.dataset.variable;
        const value = input.value;
        const regex = new RegExp(`\\[${variable}\\]`, 'g');
        content = content.replace(regex, value || `[${variable}]`);
    });

    templateText.value = content;
}

// Initialize the Application
init();