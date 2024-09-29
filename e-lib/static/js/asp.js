let selectedCount = 0;

    function toggleSelect(card) {
        card.classList.toggle('selected');
        selectedCount = document.querySelectorAll('.selection-card.selected').length;
        updateProgress();
    }

    function updateProgress() {
        const progressBar = document.getElementById('progressBar');
        const progressText = document.getElementById('progressText');
        const continueBtn = document.getElementById('continueBtn');

        const progressPercent = (selectedCount / 3) * 100;
        progressBar.style.width = progressPercent + '%';
        progressText.innerText = `${selectedCount} of 3 selected`;

        if (selectedCount >= 3) {
            continueBtn.classList.add('active');
        } else {
            continueBtn.classList.remove('active');
        }
    }

    function continueToGenres() {
        if (selectedCount >= 3) {
            window.location.href = 'genres.html';  // Redirect to the Genres page
        } else {
            alert('Please select at least 3 authors.');
        }
    }