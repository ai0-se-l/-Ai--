// Функции для кнопок
function nextChapter(currentChapterId) {
    fetch('/next_chapter', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ current_chapter_id: currentChapterId })
    })
    .then(response => response.json())
    .then(data => {
        if (data.chapter_id) {
            window.location.href = `/book/${data.book_id}/chapter/${data.chapter_number}`;
        } else {
            alert(data.message);
        }
    })
    .catch(error => console.error('Ошибка:', error));
}

function previousChapter(currentChapterId) {
    fetch('/previous_chapter', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ current_chapter_id: currentChapterId })
    })
    .then(response => response.json())
    .then(data => {
        if (data.chapter_id) {
            window.location.href = `/book/${data.book_id}/chapter/${data.chapter_number}`;
        } else {
            alert(data.message);
        }
    })
    .catch(error => console.error('Ошибка:', error));
}

function shortenText(chapterId) {
    fetch('/shorten_text', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ chapter_id: chapterId })
    })
    .then(response => response.json())
    .then(data => {
        document.querySelector('.chapter-content p').innerText = data.shortened_text;
    })
    .catch(error => console.error('Ошибка:', error));
}

function showEssence(chapterId) {
    fetch('/show_essence', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ chapter_id: chapterId })
    })
    .then(response => response.json())
    .then(data => {
        alert('Суть: ' + data.essence);
    })
    .catch(error => console.error('Ошибка:', error));
}

function testFunction() {
    fetch('/test_function')
        .then(response => response.json())
        .then(data => {
            alert(data.message);
        })
        .catch(error => console.error('Ошибка:', error));
}

function reportBug() {
    const bugDescription = prompt('Опишите проблему:');
    if (bugDescription) {
        fetch('/report_bug', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ description: bugDescription })
        })
        .then(response => response.json())
        .then(data => {
            alert(data.message);
        })
        .catch(error => console.error('Ошибка:', error));
    }
}

function rate(bookId) {
    const userRating = prompt('Поставьте оценку от 1 до 5:');
    if (userRating) {
        fetch('/rate', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ rating: userRating, book_id: bookId })
        })
        .then(response => response.json())
        .then(data => {
            alert(data.message);
        })
        .catch(error => console.error('Ошибка:', error));
    }
}