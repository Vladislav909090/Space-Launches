// launch_mission_list.js

document.addEventListener('DOMContentLoaded', () => {
    const table = document.getElementById('launchMissionsTable');
    const headers = table.querySelectorAll('th');
    const tbody = table.querySelector('tbody');
    let currentSortedColumn = null;
    let isAscending = true;

    const sortTable = (columnIndex) => {
        const header = headers[columnIndex];
        const columnKey = header.getAttribute('data-column');
        const rows = Array.from(tbody.rows);
        const numericColumns = [];

        rows.sort((a, b) => {
            let cellA = a.cells[columnIndex].innerText.trim();
            let cellB = b.cells[columnIndex].innerText.trim();

            // Обработка пустых значений
            if (!cellA || cellA === "N/A") return 1;
            if (!cellB || cellB === "N/A") return -1;

            // Проверка на числовые значения
            if (numericColumns.includes(columnKey)) {
                cellA = parseFloat(cellA.replace(/[^0-9.-]+/g, ""));
                cellB = parseFloat(cellB.replace(/[^0-9.-]+/g, ""));
                if (isNaN(cellA)) cellA = 0;
                if (isNaN(cellB)) cellB = 0;
                return isAscending ? cellA - cellB : cellB - cellA;
            }

            // Сравнение строк
            return isAscending ? cellA.localeCompare(cellB) : cellB.localeCompare(cellA);
        });

        // Удаление предыдущих сортировок
        if (currentSortedColumn !== null && currentSortedColumn !== columnIndex) {
            headers[currentSortedColumn].classList.remove('asc', 'desc');
            headers[currentSortedColumn].querySelector('.sort-indicator').style.visibility = 'hidden';
        }

        // Применение новой сортировки
        header.classList.toggle('asc', isAscending);
        header.classList.toggle('desc', !isAscending);
        header.querySelector('.sort-indicator').style.visibility = 'visible';

        currentSortedColumn = columnIndex;
        isAscending = !isAscending;

        // Перерисовка таблицы
        rows.forEach(row => tbody.appendChild(row));
    };

    // Добавление обработчиков событий для заголовков таблицы
    headers.forEach((header, index) => {
        header.addEventListener('click', () => sortTable(index));
    });

    // Функция скачивания CSV
    document.getElementById('downloadCsvButton').addEventListener('click', () => {
        const rows = Array.from(table.rows);
        const csvContent = rows.map(row => {
            return Array.from(row.cells).map((cell, index) => {
                // Проверяем, содержит ли ячейка ссылку с классом 'video-link'
                const link = cell.querySelector('a.video-link');
                let text = '';

                if (link) {
                    text = link.href;
                } else {
                    text = cell.innerText.trim();
                }

                // Экранирование кавычек
                text = text.replace(/"/g, '""');

                return `"${text}"`;
            }).join(',');
        }).join('\n');

        const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
        const link = document.createElement('a');
        const url = URL.createObjectURL(blob);
        link.href = url;
        link.download = 'launch_missions.csv';
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        URL.revokeObjectURL(url);
    });
});
