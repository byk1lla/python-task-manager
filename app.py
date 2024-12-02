from flask import Flask, request, jsonify
import json
import os

app = Flask(__name__)
TASKS_FILE = 'tasks.json'

def load_tasks():
    if os.path.exists(TASKS_FILE):
        with open(TASKS_FILE, 'r') as file:
            try:
                return json.load(file)
            except json.JSONDecodeError:
                return ["Dosya Hatası Mevcut."]  
    return ["Dosya Bulunamadı."]

def save_tasks(tasks):
    with open(TASKS_FILE, 'w') as file:
        json.dump(tasks, file)

@app.route('/tasks', methods=['GET'])
def get_tasks():
    tasks = load_tasks()
    return jsonify(tasks)

@app.route('/tasks', methods=['POST'])
def add_task():
    tasks = load_tasks()
    new_task = request.json.get("task", "").strip()
    if not new_task:
        return jsonify({"error": "Task cannot be empty"}), 400
    tasks.append(new_task)
    save_tasks(tasks)
    return jsonify({"task": new_task}), 201

@app.route('/tasks/<int:task_id>', methods=['PUT'])
def update_task(task_id):
    tasks = load_tasks()
    updated_task = request.json.get("task", "").strip()
    if task_id < 0 or task_id >= len(tasks):
        return jsonify({"error": "Invalid task ID"}), 400
    if not updated_task:
        return jsonify({"error": "Task cannot be empty"}), 400
    tasks[task_id] = updated_task
    save_tasks(tasks)
    return jsonify({"task": updated_task})

@app.route('/tasks/<int:task_id>', methods=['DELETE'])
def delete_task(task_id):
    tasks = load_tasks()
    if task_id < 0 or task_id >= len(tasks):
        return jsonify({"error": "Invalid task ID"}), 400
    deleted_task = tasks.pop(task_id)
    save_tasks(tasks)
    return jsonify({"task": deleted_task})


if __name__ == '__main__':
    if not os.path.exists(TASKS_FILE):
        with open(TASKS_FILE, 'w') as file:
            json.dump([], file)

    @app.route('/')
    def index():
        return '''
        <!doctype html>
<html lang="tr">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1, shrink-to-fit=no">
    <title>Görev Yöneticisi</title>
    <link href="https://cdn.jsdelivr.net/npm/tailwindcss@2.2.19/dist/tailwind.min.css" rel="stylesheet">
    <script src="https://cdnjs.cloudflare.com/ajax/libs/jquery/3.7.1/jquery.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/sweetalert2@11"></script>
</head>
<body class="bg-gray-100">
    <div class="container mx-auto mt-5">
        <h1 class="text-3xl font-bold mb-5">Görev Yöneticisi</h1>
        <form id="task-form" class="flex mb-3">
            <input type="text" id="task-input" class="flex-grow p-2 border border-gray-300 rounded-l" placeholder="Yeni bir görev girin">
            <button type="submit" class="bg-blue-500 text-white p-2 rounded-r">Ekle</button>
        </form>
        <ul id="tasks-list" class="bg-white shadow-md rounded p-4"></ul>
    </div>
    <script>
        $(document).ready(function() {
            function loadTasks() {
                $.get('/tasks', function(data) {
                    $('#tasks-list').empty();
                    if (Array.isArray(data)) {
                        data.forEach(function(task, index) {
                            $('#tasks-list').append(`
                                <li class="flex justify-between items-center border-b py-2">
                                    <span>${task}</span>
                                    <div>
                                        <button class="bg-yellow-500 text-white px-2 py-1 rounded edit-task" data-id="${index}">Düzenle</button>
                                        <button class="bg-red-500 text-white px-2 py-1 rounded delete-task" data-id="${index}">Sil</button>
                                    </div>
                                </li>
                            `);
                        });
                    }
                });
            }

            $('#task-form').submit(function(event) {
                event.preventDefault();
                const task = $('#task-input').val().trim();
                if (!task) {
                    Swal.fire({
                        icon: 'error',
                        title: 'Hata',
                        text: 'Görev boş olamaz!',
                        toast: true,
                        position: 'top-end',
                        showConfirmButton: false,
                        timer: 3000
                    });
                    return;
                }
                $.ajax({
                    url: '/tasks',
                    method: 'POST',
                    contentType: 'application/json',
                    data: JSON.stringify({ task }),
                    success: function() {
                        $('#task-input').val('');
                        loadTasks();
                        Swal.fire({
                            icon: 'success',
                            title: 'Görev eklendi!',
                            toast: true,
                            position: 'top-end',
                            showConfirmButton: false,
                            timer: 3000
                        });
                    }
                });
            });

            $(document).on('click', '.delete-task', function() {
                const taskId = $(this).data('id');
                $.ajax({
                    url: `/tasks/${taskId}`,
                    method: 'DELETE',
                    success: function() {
                        loadTasks();
                        Swal.fire({
                            icon: 'success',
                            title: 'Görev silindi!',
                            toast: true,
                            position: 'top-end',
                            showConfirmButton: false,
                            timer: 3000
                        });
                    }
                });
            });

            $(document).on('click', '.edit-task', function() {
                const taskId = $(this).data('id');
                const taskText = $(this).closest('li').find('span').text();
                Swal.fire({
                    title: 'Görevi Düzenle',
                    input: 'text',
                    inputValue: taskText,
                    showCancelButton: true,
                    cancelButtonText: 'İptal',
                    confirmButtonText: 'Kaydet',
                    preConfirm: (newTask) => {
                        if (!newTask) {
                            Swal.showValidationMessage('Görev boş olamaz!');
                        }
                        return newTask;
                    }
                }).then((result) => {
                    if (result.isConfirmed) {
                        $.ajax({
                            url: `/tasks/${taskId}`,
                            method: 'PUT',
                            contentType: 'application/json',
                            data: JSON.stringify({ task: result.value }),
                            success: function() {
                                loadTasks();
                                Swal.fire({
                                    icon: 'success',
                                    title: 'Görev güncellendi!',
                                    toast: true,
                                    position: 'top-end',
                                    showConfirmButton: false,
                                    timer: 3000
                                });
                            }
                        });
                    }
                });
            });

            loadTasks();
        });
    </script>
</body>
</html>
        '''

    app.run(debug=True)
