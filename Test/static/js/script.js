// Получаем элементы для грузовиков
var truckModal = document.getElementById("addTruckModal");
var addTruckBtn = document.getElementById("addTruckBtn");
var truckSpan = document.querySelectorAll("#addTruckModal .close")[0];
var truckTable = document.querySelector("#trucks-table"); // Добавьте id="trucks-table" в trucks.html
var truckModalTitle = document.getElementById("modal-title");
var truckForm = document.getElementById("truckForm");
var truckSaveButton = document.getElementById("save-button");

// Получаем элементы для водителей
var driverModal = document.getElementById("addDriverModal");
var addDriverBtn = document.getElementById("addDriverBtn");
var driverSpan = document.querySelectorAll("#addDriverModal .close")[0];
var driverTable = document.querySelector("#drivers-table"); // Добавьте id="drivers-table" в drivers.html
var driverModalTitle = document.getElementById("modal-title");
var driverForm = document.getElementById("driverForm");
var driverSaveButton = document.getElementById("save-button");

// Функции для грузовиков
if (addTruckBtn) {
    addTruckBtn.onclick = function () {
        truckModalTitle.textContent = "Добавить новый грузовик";
        truckForm.action = "/add_truck";
        document.getElementById("year").value = "";
        document.getElementById("make").value = "";
        document.getElementById("model").value = "";
        document.getElementById("mileage").value = "";
        document.getElementById("vin").value = "";
        document.getElementById("file").value = "";
        document.getElementById("type").value = "";
        document.getElementById("truck_id").value = "";
        truckSaveButton.textContent = "Сохранить";
        truckModal.style.display = "block";
    };
}

function openEditTruckModal(truckId) {
    var truckRow = document.querySelector('tr[data-truck-id="' + truckId + '"]');
    if (!truckRow) return;

    var year = truckRow.cells[0].textContent;
    var make = truckRow.cells[1].textContent;
    var model = truckRow.cells[2].textContent;
    var mileage = truckRow.cells[3].textContent;
    var vin = truckRow.cells[4].textContent;
    var file = truckRow.cells[5].querySelector('a') ? truckRow.cells[5].querySelector('a').href : ""; // Получаем URL файла
    var type = truckRow.cells[6].textContent; // Get truck type

    document.getElementById("year").value = year;
    document.getElementById("make").value = make;
    document.getElementById("model").value = model;
    document.getElementById("mileage").value = mileage;
    document.getElementById("vin").value = vin;
    document.getElementById("file").value = ""; // Очищаем поле файла при редактировании
    document.getElementById("existing_file").value = file; // Сохраняем URL существующего файла
    document.getElementById("type").value = type; // Set selected truck type
    document.getElementById("truck_id").value = truckId;

    truckModalTitle.textContent = "Редактировать грузовик";
    truckForm.action = "/edit_truck/" + truckId;
    truckSaveButton.textContent = "Сохранить изменения";
    truckModal.style.display = "block";
}

function deleteTruck(truckId) {
    if (confirm("Вы уверены, что хотите удалить этот грузовик?")) {
        fetch('/delete_truck/' + truckId, {
            method: 'POST'
        })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    var truckRow = document.querySelector('tr[data-truck-id="' + truckId + '"]');
                    if (truckRow) {
                        truckRow.remove();
                    }
                    truckModal.style.display = "none";
                } else {
                    alert('Ошибка удаления грузовика: ' + data.error);
                }
            })
            .catch(error => {
                console.error('Error:', error);
                alert('Произошла ошибка при удалении грузовика.');
            });
    }
}

if (truckTable) {
    truckTable.addEventListener('click', function (event) {
        var target = event.target;
        if (target.classList.contains('edit-btn')) {
            var truckId = target.getAttribute('data-truck-id');
            openEditTruckModal(truckId);
        } else if (target.classList.contains('delete-btn')) {
            var truckId = target.getAttribute('data-truck-id');
            deleteTruck(truckId);
        }
    });
}

if (truckSpan) {
    truckSpan.onclick = function () {
        truckModal.style.display = "none";
    };
}

// Функции для водителей
if (addDriverBtn) {
    addDriverBtn.onclick = function () {
        driverModalTitle.textContent = "Добавить нового водителя";
        driverForm.action = "/add_driver";
        document.getElementById("name").value = "";
        document.getElementById("license_number").value = "";
        document.getElementById("contact_number").value = "";
        document.getElementById("driver_id").value = "";
        driverSaveButton.textContent = "Сохранить";
        driverModal.style.display = "block";
    };
}

function openEditDriverModal(driverId) {
    var driverRow = document.querySelector('tr[data-driver-id="' + driverId + '"]');
    if (!driverRow) return;

    var name = driverRow.cells[0].textContent;
    var licenseNumber = driverRow.cells[1].textContent;
    var contactNumber = driverRow.cells[2].textContent;

    document.getElementById("name").value = name;
    document.getElementById("license_number").value = licenseNumber;
    document.getElementById("contact_number").value = contactNumber;
    document.getElementById("driver_id").value = driverId;

    driverModalTitle.textContent = "Редактировать водителя";
    driverForm.action = "/edit_driver/" + driverId;
    driverSaveButton.textContent = "Сохранить изменения";
    driverModal.style.display = "block";
}

function deleteDriver(driverId) {
    if (confirm("Вы уверены, что хотите удалить этого водителя?")) {
        fetch('/delete_driver/' + driverId, {
            method: 'POST'
        })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    var driverRow = document.querySelector('tr[data-driver-id="' + driverId + '"]');
                    if (driverRow) {
                        driverRow.remove();
                    }
                    driverModal.style.display = "none";
                } else {
                    alert('Ошибка удаления водителя: ' + data.error);
                }
            })
            .catch(error => {
                console.error('Error:', error);
                alert('Произошла ошибка при удалении водителя.');
            });
    }
}

if (driverTable) {
    driverTable.addEventListener('click', function (event) {
        var target = event.target;
        if (target.classList.contains('edit-btn')) {
            var driverId = target.getAttribute('data-driver-id');
            openEditDriverModal(driverId);
        } else if (target.classList.contains('delete-btn')) {
            var driverId = target.getAttribute('data-driver-id');
            deleteDriver(driverId);
        }
    });
}

if (driverSpan) {
    driverSpan.onclick = function () {
        driverModal.style.display = "none";
    };
}