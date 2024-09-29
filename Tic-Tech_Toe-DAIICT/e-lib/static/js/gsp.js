let selectedCount = 0;

    function toggleSelect(card) {
        card.classList.toggle('selected');
        selectedCount = document.querySelectorAll('.selection-card.selected').length;
        updateProgress();
    }

    function updateProgress() {
        const progressBar = document.getElementById('progressBar');
        const progressText = document.getElementById('progressText');
        const completeBtn = document.getElementById('completeBtn');

        const progressPercent = (selectedCount / 3) * 100;
        progressBar.style.width = progressPercent + '%';
        progressText.innerText = `${selectedCount} of 3 selected`;

        if (selectedCount >= 3) {
            completeBtn.classList.add('active');
        } else {
            completeBtn.classList.remove('active');
        }
    }

    function completeProfile() {
        if (selectedCount >= 3) {
            alert('Profile completed! Redirecting to your dashboard.');
            // Add redirection to dashboard or main page
        } else {
            alert('Please select at least 3 genres.');
        }
    }