document.addEventListener('DOMContentLoaded', () => {
    const spotifyUrlInput = document.getElementById('spotify-url');
    const submitBtn = document.getElementById('submit-btn');
    const resultSection = document.getElementById('result-section');
    const artwork = document.getElementById('artwork');
    const title = document.getElementById('title');
    const downloadBtn = document.getElementById('download-btn');
    const newSearchBtn = document.getElementById('new-search-btn');
    const loading = document.getElementById('loading');
    const error = document.getElementById('error');
    const imageResolution = document.getElementById('image-resolution');
    const resolutionWarning = document.getElementById('resolution-warning');

    submitBtn.addEventListener('click', handleSubmit);
    newSearchBtn.addEventListener('click', resetForm);
    artwork.addEventListener('load', checkImageResolution);

    async function handleSubmit() {
        const url = spotifyUrlInput.value.trim();
        
        if (!url) {
            showError('Please enter a Spotify URL');
            return;
        }

        if (!url.includes('spotify.com')) {
            showError('Please enter a valid Spotify URL');
            return;
        }

        showLoading();
        hideError();

        try {
            const response = await fetch('/get_cover', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Accept': 'application/json'
                },
                body: JSON.stringify({ url: url }),
            });

            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.detail || data.error || 'Failed to fetch artwork');
            }

            if (!data.image_url || !data.name) {
                throw new Error('Invalid response from server');
            }

            displayResult(data);
        } catch (err) {
            console.error('Error:', err);
            showError(err.message);
        } finally {
            hideLoading();
        }
    }

    function displayResult(data) {
        artwork.src = data.image_url;
        title.textContent = data.name;
        downloadBtn.href = data.image_url;
        resultSection.classList.remove('hidden');
        imageResolution.textContent = '-';
        resolutionWarning.classList.add('hidden');
    }

    function checkImageResolution() {
        const width = artwork.naturalWidth;
        const height = artwork.naturalHeight;
        imageResolution.textContent = `${width} × ${height} pixels`;
        
        // Show warning if either dimension is less than 640 pixels
        if (width < 640 || height < 640) {
            resolutionWarning.classList.remove('hidden');
        } else {
            resolutionWarning.classList.add('hidden');
        }
    }

    function resetForm() {
        spotifyUrlInput.value = '';
        resultSection.classList.add('hidden');
        hideError();
        imageResolution.textContent = '-';
        resolutionWarning.classList.add('hidden');
    }

    function showLoading() {
        loading.classList.remove('hidden');
        submitBtn.disabled = true;
    }

    function hideLoading() {
        loading.classList.add('hidden');
        submitBtn.disabled = false;
    }

    function showError(message) {
        error.textContent = message;
        error.classList.remove('hidden');
    }

    function hideError() {
        error.classList.add('hidden');
    }
});
