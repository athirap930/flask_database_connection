// Auto-detect backend URL for Docker
const getApiBase = () => {
    // In Docker, frontend can access backend by service name
    if (window.location.hostname === 'localhost') {
        return 'http://localhost:5000/api';  // Local development
    } else {
        return '/api';  // Docker production (same host, different port)
    }
};

const API_BASE = getApiBase();
let editingItemId = null;
let itemsVisible = false;

// Toggle items visibility
function toggleItems() {
    const container = document.getElementById('items-container');
    const button = document.getElementById('toggle-items-btn');
    
    if (!itemsVisible) {
        // Show items
        container.style.display = 'block';
        button.textContent = 'Hide Items';
        button.className = 'hide-btn';
        itemsVisible = true;
        
        // Load items when showing for the first time
        loadItems();
    } else {
        // Hide items
        container.style.display = 'none';
        button.textContent = 'Show Items';
        button.className = '';
        itemsVisible = false;
    }
}

// Get hii message - calls Flask API
async function getHii() {
    try {
        const response = await fetch(`${API_BASE}/hii`);
        const text = await response.text();
        
        document.getElementById('hii').innerHTML = `
            <div class="healthy">
                <strong>Message from backend:</strong> "${text}"
            </div>
        `;
    } catch (error) {
        document.getElementById('hii').innerHTML = `
            <div class="error">
                Failed to get message: ${error.message}<br>
                Make sure the Flask backend is running on port 5000
            </div>
        `;
    }
}

// Load items from Flask API
async function loadItems() {
    try {
        const response = await fetch(`${API_BASE}/items`);
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        const items = await response.json();
        
        // Show item count
        const countElement = document.createElement('div');
        countElement.className = 'items-count';
        countElement.innerHTML = `<strong>Total Items in PostgreSQL:</strong> ${items.length}`;
        
        // Check if count element already exists, if not add it
        let existingCount = document.getElementById('items-count');
        if (existingCount) {
            existingCount.remove();
        }
        countElement.id = 'items-count';
        document.getElementById('items').parentNode.insertBefore(countElement, document.getElementById('items'));
        
        // Render items
        document.getElementById('items').innerHTML = items.map(item => 
            editingItemId === item.id ? renderEditForm(item) : renderItem(item)
        ).join('');
        
    } catch (error) {
        document.getElementById('items').innerHTML = `
            <div class="error">
                Error loading items: ${error.message}<br>
                Make sure the Flask backend is running and PostgreSQL database is initialized
            </div>
        `;
    }
}

// Render item display
function renderItem(item) {
    return `
        <div class="item">
            <strong>${item.name}</strong>
            <p>${item.description || 'No description'}</p>
            <div>
                <button onclick="startEdit(${item.id})">Edit</button>
                <button onclick="deleteItem(${item.id})" style="background: #dc3545;">Delete</button>
            </div>
        </div>
    `;
}

// Render edit form
function renderEditForm(item) {
    return `
        <div class="edit-form">
            <h4>Editing Item</h4>
            <input id="edit-name-${item.id}" value="${item.name}" placeholder="Name">
            <input id="edit-desc-${item.id}" value="${item.description}" placeholder="Description">
            <br>
            <button onclick="saveEdit(${item.id})" style="background: #28a745;">Save</button>
            <button onclick="cancelEdit()">Cancel</button>
        </div>
    `;
}

// Start editing
function startEdit(id) {
    editingItemId = id;
    loadItems();
}

// Cancel editing
function cancelEdit() {
    editingItemId = null;
    loadItems();
}

// Save edited item
async function saveEdit(id) {
    try {
        const name = document.getElementById(`edit-name-${id}`).value;
        const desc = document.getElementById(`edit-desc-${id}`).value;
        
        if (!name) {
            alert('Item name is required!');
            return;
        }
        
        const response = await fetch(`${API_BASE}/items/${id}`, {
            method: 'PUT',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({name, description: desc})
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        editingItemId = null;
        loadItems();
    } catch (error) {
        alert('Error updating item: ' + error.message);
    }
}

// Add new item
async function addItem() {
    try {
        const name = document.getElementById('name').value;
        const desc = document.getElementById('desc').value;
        
        if (!name) {
            alert('Item name is required!');
            return;
        }
        
        const response = await fetch(`${API_BASE}/items`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({
                name: name,
                description: desc
            })
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        // Clear form
        document.getElementById('name').value = '';
        document.getElementById('desc').value = '';
        
        // Reload items if they are visible
        if (itemsVisible) {
            loadItems();
        }
        
        // Show success message
        alert('Item added successfully to PostgreSQL!');
        
    } catch (error) {
        alert('Error adding item: ' + error.message);
    }
}

// Delete item
async function deleteItem(id) {
    if (confirm('Are you sure you want to delete this item from PostgreSQL?')) {
        try {
            const response = await fetch(`${API_BASE}/items/${id}`, {method: 'DELETE'});
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            loadItems();
        } catch (error) {
            alert('Error deleting item: ' + error.message);
        }
    }
}