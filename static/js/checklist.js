// static/js/checklist.js

document.addEventListener('DOMContentLoaded', function() {
    // Filtros por área
    const filterButtons = document.querySelectorAll('[data-filter]');
    const checklistItems = document.querySelectorAll('.checklist-item');
    
    filterButtons.forEach(button => {
        button.addEventListener('click', function() {
            const filter = this.getAttribute('data-filter');
            
            // Ativar botão clicado
            filterButtons.forEach(btn => btn.classList.remove('active'));
            this.classList.add('active');
            
            // Filtrar itens
            checklistItems.forEach(item => {
                const area = item.getAttribute('data-area');
                
                if (filter === 'all' || area === filter) {
                    item.style.display = 'block';
                } else {
                    item.style.display = 'none';
                }
            });
        });
    });
    
    // Seleção rápida
    const selectAllBtn = document.getElementById('select-all');
    const deselectAllBtn = document.getElementById('deselect-all');
    const selectDefaultBtn = document.getElementById('select-default');
    const checkboxes = document.querySelectorAll('input[name="checklist_items"]');
    
    selectAllBtn.addEventListener('click', function() {
        checkboxes.forEach(checkbox => {
            checkbox.checked = true;
        });
    });
    
    deselectAllBtn.addEventListener('click', function() {
        checkboxes.forEach(checkbox => {
            checkbox.checked = false;
        });
    });
    
    selectDefaultBtn.addEventListener('click', function() {
        checkboxes.forEach(checkbox => {
            // Resetar todos
            checkbox.checked = false;
        });
        
        // Marcar apenas os padrão (isso requer um data-attribute)
        const defaultCheckboxes = document.querySelectorAll('input[data-is-default="true"]');
        defaultCheckboxes.forEach(checkbox => {
            checkbox.checked = true;
        });
    });
    
    // Auto-seleção baseada na categoria
    const categorySelect = document.querySelector('select[name="category"]');
    if (categorySelect) {
        categorySelect.addEventListener('change', function() {
            const selectedCategory = this.value;
            
            checkboxes.forEach(checkbox => {
                const templateCategory = checkbox.getAttribute('data-category');
                
                if (!templateCategory || templateCategory === selectedCategory) {
                    // Mostrar itens relevantes para a categoria
                    checkbox.closest('.checklist-item').style.display = 'block';
                    
                    // Auto-selecionar itens específicos da categoria
                    if (templateCategory === selectedCategory) {
                        checkbox.checked = true;
                    }
                } else {
                    checkbox.closest('.checklist-item').style.display = 'none';
                }
            });
        });
    }
});