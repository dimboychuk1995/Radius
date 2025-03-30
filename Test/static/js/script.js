// Получаем элементы
var modal = document.getElementById("addTruckModal");
var addTruckBtn = document.getElementById("addTruckBtn");
var span = document.getElementsByClassName("close")[0];
var truckTable = document.querySelector("table");  // Получаем таблицу
var modalTitle = document.getElementById("modal-title");
var truckForm = document.getElementById("truckForm");
var saveButton = document.getElementById("save-button");

// Когда пользователь нажимает на кнопку "Добавить грузовик", открываем модальное окно для добавления
addTruckBtn.onclick = function() {
    modalTitle.textContent = "Добавить новый грузовик";
    truckForm.action = "/add_truck";
    document.getElementById("year").value = "";
    document.getElementById("make").value = "";
    document.getElementById("model").value = "";
    document.getElementById("mileage").value = "";
    document.getElementById("vin").value = "";
    document.getElementById("truck_id").value = ""; // Clear truck ID
    saveButton.textContent = "Сохранить";
    modal.style.display = "block";
}



// Функция для открытия модального окна для редактирования
function openEditModal(truckId) {
    var truckRow = document.querySelector('tr[data-truck-id="' + truckId + '"]'); // Находим строку по ID
    if (!truckRow) return;

    var year = truckRow.cells[0].textContent;
    var make = truckRow.cells[1].textContent;
    var model = truckRow.cells[2].textContent;
    var mileage = truckRow.cells[3].textContent;
    var vin = truckRow.cells[4].textContent;

    document.getElementById("year").value = year;
    document.getElementById("make").value = make;
    document.getElementById("model").value = model;
    document.getElementById("mileage").value = mileage;
    document.getElementById("vin").value = vin;
    document.getElementById("truck_id").value = truckId;

    modalTitle.textContent = "Редактировать грузовик";
    truckForm.action = "/edit_truck/" + truckId;
    saveButton.textContent = "Сохранить изменения";
    modal.style.display = "block";
}

// Функция для удаления грузовика
function deleteTruck(truckId) {
    if (confirm("Вы уверены, что хотите удалить этот грузовик?")) {
        fetch('/delete_truck/' + truckId, {
            method: 'POST'
        })
        .then(response => response.json()) // Получаем JSON ответ
        .then(data => {
            if (data.success) {
                // Удаляем строку из таблицы
                var truckRow = document.querySelector('tr[data-truck-id="' + truckId + '"]');
                if (truckRow) {
                    truckRow.remove();
                }
                modal.style.display = "none"; // Hide modal after successful deletion

            } else {
                alert('Ошибка удаления грузовика.');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('Произошла ошибка при удалении грузовика.');
        });
    }
}



// Делегирование событий для кнопок "Редактировать" и "Удалить"
truckTable.addEventListener('click', function(event) {
    var target = event.target;
    if (target.classList.contains('edit-btn')) {
        var truckId = target.getAttribute('data-truck-id');
        openEditModal(truckId);
    } else if (target.classList.contains('delete-btn')) {
        var truckId = target.getAttribute('data-truck-id');
        deleteTruck(truckId);
    }
});


// Когда пользователь нажимает на <span> (x), закрываем модальное окно
span.onclick = function() {
    modal.style.display = "none";
}

// Когда пользователь щелкает в любом месте за пределами модального окна, закрываем его
window.onclick = function(event) {
    if (event.target == modal) {
        modal.style.display = "none";
    }
}