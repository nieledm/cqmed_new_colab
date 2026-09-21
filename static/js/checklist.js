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

    if (selectDefaultBtn) {
        selectDefaultBtn.addEventListener('click', function() {
            checkboxes.forEach(checkbox => {
                const isDefault = checkbox.getAttribute('data-is-default') === 'true';
                checkbox.checked = isDefault;
                
                // Disparar o evento change caso haja scripts de hierarquia escutando (grupos e subitens)
                checkbox.dispatchEvent(new Event('change'));
            });
        });
    }
        
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

// ##################################
// Parte nova
// ##################################
document.addEventListener("DOMContentLoaded", function () {
    const parentCheckboxes = document.querySelectorAll('.parent-checkbox, .group-checkbox');
    const childCheckboxes = document.querySelectorAll('.child-checkbox, .subitem-checkbox');

    // 1. Quando clicar no PAI: se tiver filhos, marca/desmarca todos os filhos dele
    parentCheckboxes.forEach(parentCb => {
        parentCb.addEventListener('change', function () {
            const parentId = this.getAttribute('data-parent-id') || this.getAttribute('data-group-id');
            const children = document.querySelectorAll(`[data-parent-ref="${parentId}"], [data-parent="${parentId}"]`);
            
            // Só altera se o pai realmente tiver filhos associados
            if (children.length > 0) {
                children.forEach(childCb => {
                    childCb.checked = this.checked;
                });
            }
        });
    });

    // 2. Quando clicar em um FILHO: atualiza o estado do pai
    childCheckboxes.forEach(childCb => {
        childCb.addEventListener('change', function () {
            const parentId = this.getAttribute('data-parent-ref') || this.getAttribute('data-parent');
            if (parentId) {
                updateParentState(parentId);
            }
        });
    });

    // Função para atualizar o Pai com base nos filhos
    function updateParentState(parentId) {
        const parentCb = document.querySelector(`[data-parent-id="${parentId}"], [data-group-id="${parentId}"]`);
        if (!parentCb) return;

        const children = document.querySelectorAll(`[data-parent-ref="${parentId}"], [data-parent="${parentId}"]`);

        // IMPORTANTE: Se o pai NÃO tem filhos, não altera o estado dele!
        if (children.length === 0) return;

        // Se tiver pelo menos 1 filho marcado, marca o pai. Se 0, desmarca.
        const anyChecked = Array.from(children).some(child => child.checked);
        parentCb.checked = anyChecked;
    }

    // 3. Executa ao carregar a página apenas para os pais QUE POSSUEM filhos
    parentCheckboxes.forEach(parentCb => {
        const parentId = parentCb.getAttribute('data-parent-id') || parentCb.getAttribute('data-group-id');
        if (parentId) {
            const children = document.querySelectorAll(`[data-parent-ref="${parentId}"], [data-parent="${parentId}"]`);
            // Só roda a atualização automática inicial se existirem filhos cadastrados
            if (children.length > 0) {
                updateParentState(parentId);
            }
        }
    });
});