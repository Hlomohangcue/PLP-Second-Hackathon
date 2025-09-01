document.addEventListener('DOMContentLoaded', () => {
    // DOM elements
    const notesInput = document.getElementById('notes-input');
    const generateBtn = document.getElementById('generate-btn');
    const clearBtn = document.getElementById('clear-btn');
    const charCount = document.getElementById('char-count');
    const inputValidationMsg = document.getElementById('input-validation-msg');
    const inputSection = document.getElementById('input-section');
    const loadingSection = document.getElementById('loading-section');
    const flashcardSection = document.getElementById('flashcard-section');
    const questionText = document.getElementById('question-text');
    const answerText = document.getElementById('answer-text');
    const prevBtn = document.getElementById('prev-btn');
    const nextBtn = document.getElementById('next-btn');
    const showAnswerBtn = document.getElementById('show-answer-btn');
    const cardProgress = document.getElementById('card-progress');
    const saveBtn = document.getElementById('save-btn');
    const newSetBtn = document.getElementById('new-set-btn');
    const loadingMsg = document.getElementById('loading-msg');
    const loadingProgress = document.getElementById('loading-progress');
    const notificationContainer = document.getElementById('notification-container');
    const answerBox = document.querySelector('.answer-box');

    // Constants
    const MIN_CHARS = 50;
    const MAX_CHARS = 2000;
    const API_BASE_URL = 'http://localhost:5000/api';
    
    // State variables
    let currentCardIndex = 0;
    let flashcards = [];

    // Simple section management
    function showSection(sectionId) {
        // Hide all sections by adding the 'hidden' class
        inputSection.classList.add('hidden');
        loadingSection.classList.add('hidden');
        flashcardSection.classList.add('hidden');
    
        // Show target section by removing the 'hidden' class
        const targetSection = document.getElementById(sectionId);
        if (targetSection) {
            targetSection.classList.remove('hidden');
        }
    }

    // Input handling
    notesInput.addEventListener('input', () => {
        const count = notesInput.value.length;
        charCount.textContent = `${count}/${MAX_CHARS}`;
        generateBtn.disabled = count < MIN_CHARS;
        
        if (count < MIN_CHARS && count > 0) {
            inputValidationMsg.textContent = `Minimum ${MIN_CHARS} characters required.`;
        } else {
            inputValidationMsg.textContent = '';
        }
    });

    clearBtn.addEventListener('click', () => {
        notesInput.value = '';
        notesInput.dispatchEvent(new Event('input'));
    });

    // Generate flashcards
    async function generateFlashcards() {
        const notes = notesInput.value.trim();
        
        if (notes.length < MIN_CHARS) {
            showNotification('Please enter more text to generate flashcards.', 'error');
            return;
        }

        showSection('loading-section');
        
        // Update loading message
        loadingMsg.textContent = 'Connecting to AI service...';
        loadingProgress.value = 20;

        try {
            const response = await fetch(`${API_BASE_URL}/process-notes`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ notes: notes })
            });

            loadingProgress.value = 70;
            loadingMsg.textContent = 'Processing response...';

            if (!response.ok) {
                const errorText = await response.text();
                throw new Error(`Server error ${response.status}: ${errorText}`);
            }

            const data = await response.json();
            
            let extractedFlashcards = data.data?.flashcard_set?.flashcards || data.flashcards || (data.success && Array.isArray(data) ? data : []);
            
            if (extractedFlashcards.length === 0) {
                throw new Error('No flashcards were generated from your notes');
            }

            flashcards = extractedFlashcards;
            
            loadingProgress.value = 100;
            
            setTimeout(() => {
                showCard(0);
                showSection('flashcard-section');
                showNotification(`Generated ${flashcards.length} flashcards successfully!`, 'success');
            }, 500);

        } catch (error) {
            showNotification(`Error: ${error.message}`, 'error');
            showSection('input-section');
        }
    }

    generateBtn.addEventListener('click', generateFlashcards);

    // Function to display a specific flashcard
    function showCard(index) {
        if (index >= 0 && index < flashcards.length) {
            currentCardIndex = index;
            const currentCard = flashcards[currentCardIndex];
            
            questionText.textContent = currentCard.question;
            answerText.textContent = currentCard.answer;
            
            // Hide the answer and reset the button text for the new card
            answerBox.classList.add('hidden');
            showAnswerBtn.textContent = 'Show Answer';

            updateCardNavigation();
        }
    }

    // Update navigation
    function updateCardNavigation() {
        cardProgress.textContent = `Card ${currentCardIndex + 1} of ${flashcards.length}`;
        prevBtn.disabled = (currentCardIndex === 0);
        nextBtn.disabled = (currentCardIndex === flashcards.length - 1);
        showAnswerBtn.disabled = false;
    }
    
    // Show/Hide Answer
    showAnswerBtn.addEventListener('click', () => {
        const isHidden = answerBox.classList.toggle('hidden');
        showAnswerBtn.textContent = isHidden ? 'Show Answer' : 'Hide Answer';
    });

    // Flashcard navigation
    nextBtn.addEventListener('click', () => {
        if (currentCardIndex < flashcards.length - 1) {
            showCard(currentCardIndex + 1);
        }
    });

    prevBtn.addEventListener('click', () => {
        if (currentCardIndex > 0) {
            showCard(currentCardIndex - 1);
        }
    });

    // Save and new set functionality
    if (saveBtn) {
        saveBtn.addEventListener('click', () => {
            showNotification('Flashcards saved!', 'success');
        });
    }

    if (newSetBtn) {
        newSetBtn.addEventListener('click', () => {
            notesInput.value = '';
            notesInput.dispatchEvent(new Event('input'));
            flashcards = [];
            currentCardIndex = 0;
            showSection('input-section');
        });
    }

    // Notification system
    function showNotification(message, type = 'info') {
        if (!notificationContainer) {
            return;
        }
        
        const notification = document.createElement('div');
        notification.className = `notification ${type}`;
        notification.textContent = message;
        notificationContainer.appendChild(notification);
        
        setTimeout(() => {
            if (notification.parentNode) {
                notification.remove();
            }
        }, 4000);
    }

    // Keyboard shortcuts
    document.addEventListener('keydown', (event) => {
        if (!flashcardSection || flashcardSection.classList.contains('hidden')) return;

        switch (event.key) {
            case 'ArrowLeft':
                event.preventDefault();
                if (prevBtn && !prevBtn.disabled) prevBtn.click();
                break;
            case 'ArrowRight':
                event.preventDefault();
                if (nextBtn && !nextBtn.disabled) nextBtn.click();
                break;
            case ' ':
            case 'Enter':
                event.preventDefault();
                if (showAnswerBtn) showAnswerBtn.click();
                break;
        }
    });

    // Initialize app
    function initApp() {
        showSection('input-section');
        if (notesInput) {
            notesInput.focus();
        }
    }

    // Start the app
    initApp();
});