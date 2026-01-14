// static/js/app.js

document.addEventListener('DOMContentLoaded', function() {
    
    // Inicializar tooltips do Bootstrap
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
    
    // Formulário de nova solicitação com validação
    const newRequestForm = document.querySelector('form[action*="create_request"]');
    if (newRequestForm) {
        newRequestForm.addEventListener('submit', function(e) {
            const nameField = this.querySelector('input[name="collaborator_name"]');
            const categoryField = this.querySelector('select[name="category"]');
            
            let isValid = true;
            
            // Validação do nome
            if (!nameField.value.trim()) {
                showError(nameField, 'Por favor, informe o nome do colaborador');
                isValid = false;
            } else {
                clearError(nameField);
            }
            
            // Validação da categoria
            if (!categoryField.value) {
                showError(categoryField, 'Por favor, selecione uma categoria');
                isValid = false;
            } else {
                clearError(categoryField);
            }
            
            if (!isValid) {
                e.preventDefault();
                showToast('Por favor, corrija os campos destacados', 'warning');
            }
        });
    }
    
    // Formatação de datas
    const dateElements = document.querySelectorAll('.date-format');
    dateElements.forEach(element => {
        if (element.textContent) {
            const date = new Date(element.textContent);
            if (!isNaN(date)) {
                element.textContent = formatDate(date);
                element.title = date.toLocaleString();
            }
        }
    });
    
    // Auto-fechar alertas após 5 segundos
    const alerts = document.querySelectorAll('.alert:not(.alert-permanent)');
    alerts.forEach(alert => {
        setTimeout(() => {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        }, 5000);
    });
    
    // Atualizar status com confirmação
    const statusForms = document.querySelectorAll('form[action*="update_checklist"]');
    statusForms.forEach(form => {
        const select = form.querySelector('select[name="status"]');
        const originalValue = select.value;
        
        select.addEventListener('change', function() {
            if (originalValue !== this.value) {
                const itemName = form.querySelector('span').textContent.trim();
                const confirmUpdate = confirm(`Deseja alterar o status de "${itemName}" para "${getStatusText(this.value)}"?`);
                
                if (confirmUpdate) {
                    form.submit();
                } else {
                    this.value = originalValue;
                }
            }
        });
    });
    
    // Filtro de busca nas tabelas
    const searchInput = document.getElementById('searchInput');
    if (searchInput) {
        searchInput.addEventListener('keyup', function() {
            const filter = this.value.toLowerCase();
            const table = this.closest('.table-container').querySelector('tbody');
            const rows = table.querySelectorAll('tr');
            
            rows.forEach(row => {
                const text = row.textContent.toLowerCase();
                row.style.display = text.includes(filter) ? '' : 'none';
            });
        });
    }
    
    // Funções auxiliares
    function showError(element, message) {
        element.classList.add('is-invalid');
        let feedback = element.nextElementSibling;
        if (!feedback || !feedback.classList.contains('invalid-feedback')) {
            feedback = document.createElement('div');
            feedback.className = 'invalid-feedback';
            element.parentNode.insertBefore(feedback, element.nextSibling);
        }
        feedback.textContent = message;
    }
    
    function clearError(element) {
        element.classList.remove('is-invalid');
        const feedback = element.nextElementSibling;
        if (feedback && feedback.classList.contains('invalid-feedback')) {
            feedback.remove();
        }
    }
    
    function formatDate(date) {
        const options = { 
            day: '2-digit', 
            month: '2-digit', 
            year: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        };
        return date.toLocaleDateString('pt-BR', options);
    }
    
    function getStatusText(status) {
        const statusMap = {
            'pending': 'Pendente',
            'doing': 'Em andamento',
            'done': 'Concluído',
            'aguardando': 'Aguardando',
            'em_andamento': 'Em andamento',
            'concluido': 'Concluído'
        };
        return statusMap[status] || status;
    }
    
    function showToast(message, type = 'info') {
        // Criar toast dinâmico
        const toastContainer = document.querySelector('.toast-container') || createToastContainer();
        const toastId = 'toast-' + Date.now();
        
        const toastHTML = `
            <div id="${toastId}" class="toast" role="alert" aria-live="assertive" aria-atomic="true">
                <div class="toast-header bg-${type} text-white">
                    <strong class="me-auto">Notificação</strong>
                    <button type="button" class="btn-close btn-close-white" data-bs-dismiss="toast"></button>
                </div>
                <div class="toast-body">
                    ${message}
                </div>
            </div>
        `;
        
        toastContainer.insertAdjacentHTML('beforeend', toastHTML);
        const toastElement = document.getElementById(toastId);
        const toast = new bootstrap.Toast(toastElement);
        toast.show();
        
        // Remover após ser escondido
        toastElement.addEventListener('hidden.bs.toast', function() {
            this.remove();
        });
    }
    
    function createToastContainer() {
        const container = document.createElement('div');
        container.className = 'toast-container position-fixed top-0 end-0 p-3';
        container.style.zIndex = '1055';
        document.body.appendChild(container);
        return container;
    }
    
    // Habilitar confirmação antes de deletar
    const deleteButtons = document.querySelectorAll('.btn-delete');
    deleteButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            if (!confirm('Tem certeza que deseja excluir este item? Esta ação não pode ser desfeita.')) {
                e.preventDefault();
            }
        });
    });
    initializeProgressBars();
});

function initializeProgressBars() {
    const progressBars = document.querySelectorAll('.progress-bar[data-progress]');
    
    progressBars.forEach(bar => {
        const progress = parseFloat(bar.getAttribute('data-progress'));
        
        // Definir largura
        bar.style.width = `${progress}%`;
        
        // Definir cor baseada no progresso
        if (progress < 30) {
            bar.classList.add('progress-bar-low');
        } else if (progress < 70) {
            bar.classList.add('progress-bar-medium');
        } else {
            bar.classList.add('progress-bar-high');
        }
        
        // Atualizar aria-valuenow
        bar.setAttribute('aria-valuenow', progress);
    });
}