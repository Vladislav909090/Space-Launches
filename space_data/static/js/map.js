// map.js

document.addEventListener('DOMContentLoaded', () => {
    // Инициализация карты
    var map = L.map('map').setView([20, 0], 2);

    // Слои карт
    var osmLayer = L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: 'Данные © <a href="https://www.openstreetmap.org/">OpenStreetMap</a> contributors'
    }).addTo(map);

    var satelliteLayer = L.tileLayer('https://{s}.google.com/vt/lyrs=s&x={x}&y={y}&z={z}', {
        attribution: 'Данные © Google',
        subdomains: ['mt0', 'mt1', 'mt2', 'mt3']
    });

    // Контроль слоёв
    var baseMaps = {
        "OpenStreetMap": osmLayer,
        "Спутник": satelliteLayer
    };
    L.control.layers(baseMaps).addTo(map);

    // Настраиваем параметры кластера
    var clusterOptions = {
        disableClusteringAtZoom: 7,  // Отключаем кластеризацию на уровне зума 7 и выше
        maxClusterRadius: 50        // Уменьшаем радиус кластеризации для более раннего раскрытия
    };

    // Кластеризация
    var markers = L.markerClusterGroup(clusterOptions);

    // Иконки для статусов
    function getIcon(status) {
        var color;
        switch(status) {
            case 'Active':
                color = 'green';
                break;
            case 'Abandoned':
                color = 'red';
                break;
            case 'Under Construction':
                color = 'gray';
                break;
            default:
                color = 'blue';
        }

        return L.circleMarker([0, 0], {
            radius: 8,
            fillColor: color,
            color: '#fff',
            weight: 1,
            opacity: 1,
            fillOpacity: 0.8
        });
    }

    // Данные стартовых площадок (предполагается, что launchPads определен глобально)
    if (typeof launchPads !== 'undefined') {
        launchPads.forEach(function(pad) {
            if (pad.latitude !== null && pad.longitude !== null) {
                var marker = getIcon(pad.status).setLatLng([pad.latitude, pad.longitude]);
                marker.bindPopup("<b>" + pad.name + "</b><br>" + pad.description + "<br><b>Статус:</b> " + pad.status);
                markers.addLayer(marker);
            }
        });
        map.addLayer(markers);
    }

    // Добавляем легенду
    var legend = L.control({position: 'bottomright'});

    legend.onAdd = function(map) {
        var div = L.DomUtil.create('div', 'legend');
        div.innerHTML += '<div><span class="legend-color-box" style="background: green;"></span> Действующая</div>';
        div.innerHTML += '<div><span class="legend-color-box" style="background: red;"></span> Заброшена</div>';
        div.innerHTML += '<div><span class="legend-color-box" style="background: gray;"></span> Строится</div>';
        return div;
    };

    legend.addTo(map);
});
