// AI First-Aid Assistant JavaScript
document.addEventListener('DOMContentLoaded', () => {
    // Tab functionality
    const tabBtns = document.querySelectorAll('.tab-btn');
    const tabPanes = document.querySelectorAll('.tab-pane');
    
    // Form elements
    const uploadForm = document.getElementById('upload-form');
    const describeForm = document.getElementById('describe-form');
    const fileInput = document.getElementById('injury-image');
    const textarea = document.getElementById('injury-description');
    
    // Results elements
    const resultsSection = document.getElementById('results');
    const emergencyAlert = document.getElementById('emergency-alert');
    const injuryType = document.getElementById('injury-type');
    const stepsList = document.getElementById('steps-list');
    const emergencyMessage = document.getElementById('emergency-message');

    // Tab switching functionality
    tabBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            const targetTab = btn.getAttribute('data-tab');
            
            // Update active tab button
            tabBtns.forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            
            // Update active tab pane
            tabPanes.forEach(pane => {
                pane.classList.remove('active');
                if (pane.id === targetTab) {
                    pane.classList.add('active');
                }
            });
        });
    });

    // File input change handler
    fileInput.addEventListener('change', () => {
        const file = fileInput.files[0];
        if (file) {
            console.log('File selected:', file.name, 'Size:', file.size, 'Type:', file.type);
            // Update the label to show selected file
            const label = fileInput.nextElementSibling;
            label.textContent = file.name;
            label.style.color = '#10b981';
        }
    });

    // Upload form submission
    uploadForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        if (!fileInput.files[0]) {
            alert('Please select an image file.');
            return;
        }
        
        await processImageUpload();
    });

    // Describe form submission
    describeForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        if (!textarea.value.trim()) {
            alert('Please describe the injury.');
            return;
        }
        
        await processTextDescription();
    });

    async function processImageUpload() {
        try {
            // Show loading state
            const submitBtn = uploadForm.querySelector('button[type="submit"]');
            const originalText = submitBtn.textContent;
            submitBtn.textContent = 'Processing...';
            submitBtn.disabled = true;

            const formData = new FormData();
            formData.append('image', fileInput.files[0]);

            const response = await fetch('/ask', {
                method: 'POST',
                body: formData,
            });

            const result = await response.json();

            if (response.ok) {
                displayResults(result);
            } else {
                throw new Error(result.error || 'Failed to process image');
            }

        } catch (error) {
            console.error('Error:', error);
            alert(error.message || 'Sorry, there was an error processing your image. Please try again.');
        } finally {
            // Reset button state
            const submitBtn = uploadForm.querySelector('button[type="submit"]');
            submitBtn.textContent = 'Get First-Aid';
            submitBtn.disabled = false;
        }
    }

    async function processTextDescription() {
        try {
            // Show loading state
            const submitBtn = describeForm.querySelector('button[type="submit"]');
            const originalText = submitBtn.textContent;
            submitBtn.textContent = 'Processing...';
            submitBtn.disabled = true;

            const response = await fetch('/ask', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    message: textarea.value.trim()
                }),
            });

            const result = await response.json();

            if (response.ok) {
                displayResults(result);
            } else {
                throw new Error(result.error || 'Failed to process description');
            }

        } catch (error) {
            console.error('Error:', error);
            alert(error.message || 'Sorry, there was an error processing your description. Please try again.');
        } finally {
            // Reset button state
            const submitBtn = describeForm.querySelector('button[type="submit"]');
            submitBtn.textContent = 'Get First-Aid';
            submitBtn.disabled = false;
        }
    }

    function displayResults(data) {
        // Clear previous results
        injuryType.textContent = '';
        stepsList.innerHTML = '';
        
        // Update injury type
        injuryType.textContent = data.injury_name || 'Not specified';

        // Add first aid steps
        if (data.first_aid_steps && Array.isArray(data.first_aid_steps)) {
            data.first_aid_steps.forEach(step => {
                const li = document.createElement('li');
                li.textContent = step;
                stepsList.appendChild(li);
            });
        }

        // Handle emergency status based on severity
        if (data.severity === 'severe') {
            emergencyMessage.textContent = 'This condition requires immediate medical attention.';
            emergencyAlert.classList.remove('hidden');
        } else {
            emergencyAlert.classList.add('hidden');
        }

        // Show results
        resultsSection.classList.remove('hidden');
        resultsSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
});
