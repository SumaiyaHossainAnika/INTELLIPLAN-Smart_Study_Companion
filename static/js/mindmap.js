// Interactive Mind Map Implementation
// Author: GitHub Copilot
// Description: Canvas-based interactive mind mapping tool with drag-and-drop functionality

class MindMapNode {
    constructor(id, text, x = 0, y = 0) {
        this.id = id;
        this.text = text;
        this.x = x;
        this.y = y;
        this.children = [];
        this.parent = null;
        this.isExpanded = true;
        this.color = '#4CAF50';
        this.fontSize = 14;
    }

    addChild(childNode) {
        childNode.parent = this;
        this.children.push(childNode);
    }

    removeChild(childId) {
        this.children = this.children.filter(child => child.id !== childId);
    }

    toggleExpanded() {
        this.isExpanded = !this.isExpanded;
    }
}

class MindMap {
    constructor(canvasId) {
        this.canvas = document.getElementById(canvasId);
        this.ctx = this.canvas.getContext('2d');
        this.root = null;
        this.selectedNode = null;
        this.draggedNode = null;
        this.isDragging = false;
        this.nodeCounter = 0;
        
        this.setupEventListeners();
        this.resizeCanvas();
    }

    setupEventListeners() {
        this.canvas.addEventListener('mousedown', this.onMouseDown.bind(this));
        this.canvas.addEventListener('mousemove', this.onMouseMove.bind(this));
        this.canvas.addEventListener('mouseup', this.onMouseUp.bind(this));
        this.canvas.addEventListener('dblclick', this.onDoubleClick.bind(this));
        window.addEventListener('resize', this.resizeCanvas.bind(this));
    }

    resizeCanvas() {
        this.canvas.width = window.innerWidth - 20;
        this.canvas.height = window.innerHeight - 100;
        this.draw();
    }

    createRootNode(text) {
        this.root = new MindMapNode(
            this.nodeCounter++, 
            text, 
            this.canvas.width / 2, 
            this.canvas.height / 2
        );
        this.root.color = '#2196F3';
        this.root.fontSize = 18;
        this.draw();
    }

    addNode(parentId, text) {
        const parent = this.findNode(this.root, parentId);
        if (parent) {
            const newNode = new MindMapNode(this.nodeCounter++, text);
            parent.addChild(newNode);
            this.positionNode(newNode);
            this.draw();
            return newNode;
        }
        return null;
    }

    findNode(node, id) {
        if (!node) return null;
        if (node.id === id) return node;
        
        for (let child of node.children) {
            const found = this.findNode(child, id);
            if (found) return found;
        }
        return null;
    }

    positionNode(node) {
        if (!node.parent) return;
        
        const parent = node.parent;
        const siblings = parent.children;
        const index = siblings.indexOf(node);
        const angleStep = (2 * Math.PI) / Math.max(siblings.length, 4);
        const radius = 150;
        
        const angle = index * angleStep;
        node.x = parent.x + Math.cos(angle) * radius;
        node.y = parent.y + Math.sin(angle) * radius;
    }

    getNodeAt(x, y) {
        return this.findNodeAt(this.root, x, y);
    }

    findNodeAt(node, x, y) {
        if (!node) return null;
        
        const distance = Math.sqrt((node.x - x) ** 2 + (node.y - y) ** 2);
        if (distance < 22) return node;

        for (let child of node.children) {
            const found = this.findNodeAt(child, x, y);
            if (found) return found;
        }
        return null;
    }

    onMouseDown(event) {
        const rect = this.canvas.getBoundingClientRect();
        const x = event.clientX - rect.left;
        const y = event.clientY - rect.top;
        
        const node = this.getNodeAt(x, y);
        if (node) {
            this.selectedNode = node;
            this.draggedNode = node;
            this.isDragging = true;
            this.draw();
        }
    }

    onMouseMove(event) {
        if (this.isDragging && this.draggedNode) {
            const rect = this.canvas.getBoundingClientRect();
            this.draggedNode.x = event.clientX - rect.left;
            this.draggedNode.y = event.clientY - rect.top;
            this.draw();
        }
    }

    onMouseUp(event) {
        this.isDragging = false;
        this.draggedNode = null;
    }

    onDoubleClick(event) {
        const rect = this.canvas.getBoundingClientRect();
        const x = event.clientX - rect.left;
        const y = event.clientY - rect.top;
        
        const node = this.getNodeAt(x, y);
        if (node) {
            const newText = prompt('Edit node text:', node.text);
            if (newText) {
                node.text = newText;
                this.draw();
            }
        }
    }

    draw() {
        this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);
        
        if (this.root) {
            this.drawConnections(this.root);
            this.drawNode(this.root);
        }
    }

    drawConnections(node) {
        if (!node.isExpanded) return;
        
        for (let child of node.children) {
            this.ctx.beginPath();
            this.ctx.moveTo(node.x, node.y);
            this.ctx.lineTo(child.x, child.y);
            this.ctx.strokeStyle = '#666';
            this.ctx.lineWidth = 2;
            this.ctx.stroke();
            
            this.drawConnections(child);
        }
    }

    drawNode(node) {
        // Draw node circle
        this.ctx.beginPath();
        this.ctx.arc(node.x, node.y, 18, 0, 2 * Math.PI);
        this.ctx.fillStyle = node === this.selectedNode ? '#FF5722' : node.color;
        this.ctx.fill();
        this.ctx.strokeStyle = '#333';
        this.ctx.lineWidth = 2;
        this.ctx.stroke();
        
        // Draw node text
        this.ctx.fillStyle = 'white';
        this.ctx.font = `${node.fontSize}px Arial`;
        this.ctx.textAlign = 'center';
        this.ctx.textBaseline = 'middle';
        this.ctx.fillText(node.text, node.x, node.y);
        
        // Draw children if expanded
        if (node.isExpanded) {
            for (let child of node.children) {
                this.drawNode(child);
            }
        }
    }

    exportToJSON() {
        return JSON.stringify(this.serializeNode(this.root), null, 2);
    }

    serializeNode(node) {
        if (!node) return null;
        
        return {
            id: node.id,
            text: node.text,
            x: node.x,
            y: node.y,
            color: node.color,
            fontSize: node.fontSize,
            isExpanded: node.isExpanded,
            children: node.children.map(child => this.serializeNode(child))
        };
    }

    importFromJSON(jsonString) {
        try {
            const data = JSON.parse(jsonString);
            this.root = this.deserializeNode(data);
            this.draw();
        } catch (error) {
            console.error('Error importing mind map:', error);
        }
    }

    deserializeNode(data) {
        if (!data) return null;
        
        const node = new MindMapNode(data.id, data.text, data.x, data.y);
        node.color = data.color;
        node.fontSize = data.fontSize;
        node.isExpanded = data.isExpanded;
        
        for (let childData of data.children || []) {
            const child = this.deserializeNode(childData);
            if (child) {
                node.addChild(child);
            }
        }
        
        this.nodeCounter = Math.max(this.nodeCounter, data.id + 1);
        return node;
    }
}

// Global mind map instance
let mindMap;

// Initialize mind map when DOM is loaded
window.onload = function() {
    mindMap = new MindMap('mindMapCanvas');
};

// Mind map control functions
function createRoot() {
    const text = document.getElementById('nodeText').value.trim();
    if (text) {
        mindMap.createRootNode(text);
        document.getElementById('nodeText').value = '';
    } else {
        alert('Please enter text for the root node');
    }
}

function addChildNode() {
    const text = document.getElementById('nodeText').value.trim();
    if (!text) {
        alert('Please enter text for the new node');
        return;
    }
    
    if (!mindMap.selectedNode) {
        alert('Please select a parent node first');
        return;
    }
    
    mindMap.addNode(mindMap.selectedNode.id, text);
    document.getElementById('nodeText').value = '';
}

function deleteNode() {
    if (!mindMap.selectedNode) {
        alert('Please select a node to delete');
        return;
    }
    
    if (mindMap.selectedNode === mindMap.root) {
        alert('Cannot delete the root node');
        return;
    }
    
    const parent = mindMap.selectedNode.parent;
    if (parent) {
        parent.removeChild(mindMap.selectedNode.id);
        mindMap.selectedNode = null;
        mindMap.draw();
    }
}

function exportMindMap() {
    if (!mindMap.root) {
        alert('No mind map to export');
        return;
    }
    
    const jsonData = mindMap.exportToJSON();
    const blob = new Blob([jsonData], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'mindmap.json';
    a.click();
    URL.revokeObjectURL(url);
}

function importMindMap() {
    const input = document.createElement('input');
    input.type = 'file';
    input.accept = '.json';
    input.onchange = function(event) {
        const file = event.target.files[0];
        if (file) {
            const reader = new FileReader();
            reader.onload = function(e) {
                mindMap.importFromJSON(e.target.result);
            };
            reader.readAsText(file);
        }
    };
    input.click();
}

function clearCanvas() {
    if (confirm('Are you sure you want to clear the entire mind map?')) {
        mindMap.root = null;
        mindMap.selectedNode = null;
        mindMap.nodeCounter = 0;
        mindMap.draw();
    }
}
