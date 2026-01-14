document.addEventListener('DOMContentLoaded', function() {
    // Quando clicar em um grupo, selecionar/deselecionar todos os subitens
    const groupCheckboxes = document.querySelectorAll('.group-checkbox');
    groupCheckboxes.forEach(group => {
        group.addEventListener('change', function() {
            const groupId = this.getAttribute('data-group-id');
            const subitems = document.querySelectorAll(`.subitem-checkbox[data-parent="${groupId}"]`);
            
            subitems.forEach(subitem => {
                subitem.checked = this.checked;
            });
        });
    });
    
    // Quando todos os subitens forem selecionados, marcar o grupo
    const subitemCheckboxes = document.querySelectorAll('.subitem-checkbox');
    subitemCheckboxes.forEach(subitem => {
        subitem.addEventListener('change', function() {
            const parentId = this.getAttribute('data-parent');
            const parentCheckbox = document.querySelector(`.group-checkbox[data-group-id="${parentId}"]`);
            const subitems = document.querySelectorAll(`.subitem-checkbox[data-parent="${parentId}"]`);
            
            // Verificar se todos os subitens estão selecionados
            const allChecked = Array.from(subitems).every(item => item.checked);
            // Verificar se algum subitem está selecionado
            const anyChecked = Array.from(subitems).some(item => item.checked);
            
            parentCheckbox.checked = allChecked;
            parentCheckbox.indeterminate = anyChecked && !allChecked;
        });
    });
    
    // Expandir/recolher grupos
    document.querySelectorAll('.checklist-group .form-check-label').forEach(label => {
        label.style.cursor = 'pointer';
        label.addEventListener('click', function(e) {
            if (e.target.tagName === 'INPUT') return;
            
            const group = this.closest('.checklist-group');
            const subitems = group.querySelector('.subitems');
            const icon = this.querySelector('i');
            
            if (subitems.style.display === 'none') {
                subitems.style.display = 'block';
                icon.className = 'fas fa-folder-open me-1';
            } else {
                subitems.style.display = 'none';
                icon.className = 'fas fa-folder me-1';
            }
        });
    });
});