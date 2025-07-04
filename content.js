function createSimpleButton(text, onClick, topPx) {
    const button = document.createElement('button');
    button.textContent = text;
    button.style.position = 'fixed';
    button.style.top = topPx + 'px';
    button.style.right = '20px';
    button.style.zIndex = 10000;
    button.style.padding = '8px 14px';
    button.style.fontSize = '14px';
    button.style.border = 'none';
    button.style.borderRadius = '6px';
    button.style.backgroundColor = 'rgba(255, 67, 67, 0.5)';
    button.style.color = 'white';
    button.style.cursor = 'pointer';
    button.style.boxShadow = '0 2px 4px rgba(0,0,0,0.2)';
    button.style.userSelect = 'none';

    button.onclick = onClick;
    return button;
}

function downloadFile(url, postData, startMsg, finishMsg, failMsg) {
    fetch('http://localhost:6969/ping')
        .then(res => {
            if (!res.ok) throw new Error('Server not available');
            alert(startMsg);

            return fetch(url, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(postData),
            });
        })
        .then(async res => {
            if (!res.ok) {
                alert(failMsg);
                return;
            }

            let filename = 'download';
            console.log('Response Headers:', res.headers);
            const disposition = res.headers.get('Content-Disposition');
            console.log('Content-Disposition:', disposition);
            if (disposition && disposition.includes('filename=')) {
                filename = disposition.split('filename=')[1].replace(/"/g, '');
            }

            const blob = await res.blob();
            const downloadUrl = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = downloadUrl;
            a.download = filename;
            document.body.appendChild(a);
            a.click();
            a.remove();
            window.URL.revokeObjectURL(downloadUrl);
        })
        .catch(() => {
            alert('Could not connect to the server. Is it running?');
        });
}

window.onload = () => {
    const mp4Button = createSimpleButton('Download MP4', () => {
        downloadFile(
            'http://localhost:6969/download/mp4',
            { url: window.location.href },
            'MP4 download started!',
            'MP4 download finished!',
            'Failed to download MP4.'
        );
    }, 80);

    const mp3Button = createSimpleButton('Download MP3', () => {
        downloadFile(
            'http://localhost:6969/download/mp3',
            { url: window.location.href },
            'MP3 download started!',
            'MP3 download finished!',
            'Failed to download MP3.'
        );
    }, 130);

    document.body.appendChild(mp4Button);
    document.body.appendChild(mp3Button);

    const toggleButtons = () => {
        const isFullscreen = document.fullscreenElement !== null;
        const display = isFullscreen ? 'none' : 'block';
        mp4Button.style.display = display;
        mp3Button.style.display = display;
    };

    document.addEventListener('fullscreenchange', toggleButtons);
};
