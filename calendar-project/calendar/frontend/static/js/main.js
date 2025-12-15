function handleCredentialResponse(response) {
    fetch('/auth/verify', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({credential: response.credential})
    })
    .then(r => r.json())
    .then(data => {
        alert("Успешный вход! Перенаправляем...");
        window.location.href = `/bookings/?email=${encodeURIComponent(data.email)}`;
    })
    .catch(err => {
        alert("Ошибка входа");
        console.error(err);
    });
}