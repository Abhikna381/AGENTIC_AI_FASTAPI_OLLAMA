/**
 * Helper: Returns a full timestamp (e.g., "Mon, Mar 30 | 10:30 AM")
 */
function getFullTimestamp() {
    const now = new Date();
    
    // Options for the date part (e.g., Mon, Mar 30)
    const dateOptions = { weekday: 'short', month: 'short', day: 'numeric' };
    const datePart = now.toLocaleDateString('en-US', dateOptions);

    // Options for the time part (e.g., 10:30 AM)
    const timeOptions = { hour: '2-digit', minute: '2-digit' };
    const timePart = now.toLocaleTimeString('en-US', timeOptions);

    return `${datePart} | ${timePart}`;
}

function addTodo() {
    const input = document.getElementById('todoInput');
    const ul = document.getElementById('todoList');
    const todoText = input.value.trim();

    if (todoText) {
        const fullTime = getFullTimestamp();
        const li = document.createElement('li');

        // Structure the inside of the <li>
        li.innerHTML = `
            <div class="task-info">
                <span class="task-text">${todoText}</span>
                <small class="task-meta">${fullTime}</small>
            </div>
        `;

        // Create the Delete Button
        const delBtn = document.createElement('button');
        delBtn.textContent = 'Delete';
        delBtn.classList.add('delete-btn');
        delBtn.onclick = () => li.remove();

        li.appendChild(delBtn);
        ul.appendChild(li);

        input.value = '';
    }
}