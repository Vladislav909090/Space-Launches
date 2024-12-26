document.addEventListener('DOMContentLoaded', function() {
    let activeFileInput = null;
    let clickCount = 0;  // Счётчик кликов

    // Обходим все поля загрузки изображений
    document.querySelectorAll('input[type="file"]').forEach(function(fileInput) {
        fileInput.addEventListener('click', function(event) {
            clickCount++;  // Увеличиваем счётчик при каждом клике

            if (clickCount % 2 === 0) {
                // Если это чётный клик, позволяем открыть проводник
                clickCount = 0;  // Сбрасываем счётчик, чтобы каждый второй клик был чётным
            } else {
                // Если это нечётный клик, предотвращаем открытие проводника
                event.preventDefault();
                fileInput.focus(); // Переводим фокус на поле
                activeFileInput = fileInput; // Делаем поле активным для вставки
            }
        });

        // Слушаем событие фокуса, чтобы активировать поле
        fileInput.addEventListener('focus', function() {
            activeFileInput = fileInput;
        });

        // Слушаем событие потери фокуса, чтобы сбросить активное поле
        fileInput.addEventListener('blur', function() {
            activeFileInput = null;
        });
    });

    // Обработка события вставки
    document.addEventListener('paste', function(event) {
        if (!activeFileInput) return; // Если нет активного поля, выходим

        const items = event.clipboardData.items;
        for (let i = 0; i < items.length; i++) {
            const item = items[i];
            if (item.kind === 'file') {
                const file = item.getAsFile();
                const dataTransfer = new DataTransfer();
                dataTransfer.items.add(file);
                activeFileInput.files = dataTransfer.files;
                break; // Останавливаем цикл после вставки одного изображения
            }
        }
    });
});
