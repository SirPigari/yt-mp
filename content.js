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
    button.style.backgroundColor = '#FF0000';
    button.style.color = 'white';
    button.style.cursor = 'pointer';
    button.style.boxShadow = '0 2px 4px rgba(0,0,0,0.2)';
    button.style.userSelect = 'none';

    button.onclick = onClick;
    return button;
}

function downloadFile(url, postData, startMsg, finishMsg, failMsg) {
    fetch('http://localhost:5000/ping')
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

            alert(finishMsg);
        })
        .catch(() => {
            alert('Could not connect to the server. Is it running?');
        });
}

window.onload = () => {
    const mp4Button = createSimpleButton('Download MP4', () => {
        downloadFile(
            'http://localhost:5000/download/mp4',
            { url: window.location.href },
            'MP4 download started!',
            'MP4 download finished!',
            'Failed to download MP4.'
        );
    }, 80);

    const mp3Button = createSimpleButton('Download MP3', () => {
        downloadFile(
            'http://localhost:5000/download/mp3',
            { url: window.location.href },
            'MP3 download started!',
            'MP3 download finished!',
            'Failed to download MP3.'
        );
    }, 130);

    document.body.appendChild(mp4Button);
    document.body.appendChild(mp3Button);
};
