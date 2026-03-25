/**
 * Dashboard JavaScript
 * Handles dashboard interactions and animations
 */

document.addEventListener('DOMContentLoaded', function() {
    // Initialize dashboard
    initDashboard();
    
    // Add hover effects to cards
    setupCardInteractions();
});

/**
 * Initialize dashboard
 */
function initDashboard() {
    console.log('Dashboard initialized');
    
    // Add any initialization logic here
    setupTooltips();
}

/**
 * Setup card hover interactions
 */
function setupCardInteractions() {
    const actionCards = document.querySelectorAll('.action-card');
    
    actionCards.forEach(card => {
        card.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-8px)';
        });
        
        card.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(0)';
        });
    });
}

/**
 * Setup tooltips for informational elements
 */
function setupTooltips() {
    // Placeholder for tooltip implementation
    const infoElements = document.querySelectorAll('[data-tooltip]');
    
    infoElements.forEach(element => {
        const tooltip = element.getAttribute('data-tooltip');
        element.title = tooltip;
    });
}

/**
 * Format date for display
 */
function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'long',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    });
}

/**
 * Show alert notification
 */
function showAlert(message, type = 'info') {
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type}`;
    alertDiv.textContent = message;
    alertDiv.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        padding: 15px 20px;
        border-radius: 6px;
        background: ${type === 'success' ? '#d4edda' : type === 'error' ? '#f8d7da' : '#d1ecf1'};
        color: ${type === 'success' ? '#155724' : type === 'error' ? '#721c24' : '#0c5460'};
        z-index: 10000;
        animation: slideIn 0.3s ease-out;
    `;
    
    document.body.appendChild(alertDiv);
    
    // Auto-remove after 5 seconds
    setTimeout(() => {
        alertDiv.style.animation = 'slideOut 0.3s ease-out';
        setTimeout(() => alertDiv.remove(), 300);
    }, 5000);
}

/**
 * Logout user
 */
function logout() {
    if (confirm('Are you sure you want to logout?')) {
        window.location.href = '/logout';
    }
}

/**
 * Show CKD information modal
 */
function showCKDInfo() {
    const infoHTML = `
        <div style="padding: 20px;">
            <h2 style="color: #667eea; margin-bottom: 20px;">About Chronic Kidney Disease (CKD)</h2>
            
            <div style="background: #f9f9f9; padding: 15px; border-radius: 8px; margin-bottom: 20px;">
                <h3>What is CKD?</h3>
                <p>Chronic Kidney Disease (CKD) is a condition characterized by gradual loss of kidney function over time. 
                The kidneys filter waste products and excess water from the blood to form urine. When kidney function is reduced, 
                dangerous levels of fluid and waste can accumulate in the body.</p>
            </div>

            <div style="background: #f9f9f9; padding: 15px; border-radius: 8px; margin-bottom: 20px;">
                <h3>CKD Stages</h3>
                <ul style="line-height: 2;">
                    <li><strong>Stage 1:</strong> Normal kidney function (GFR ≥ 90)</li>
                    <li><strong>Stage 2:</strong> Mildly reduced (GFR 60-89)</li>
                    <li><strong>Stage 3a:</strong> Moderately reduced (GFR 45-59)</li>
                    <li><strong>Stage 3b:</strong> Moderately reduced (GFR 30-44)</li>
                    <li><strong>Stage 4:</strong> Severely reduced (GFR 15-29)</li>
                    <li><strong>Stage 5:</strong> Kidney failure (GFR < 15)</li>
                </ul>
            </div>

            <div style="background: #f9f9f9; padding: 15px; border-radius: 8px; margin-bottom: 20px;">
                <h3>Risk Factors</h3>
                <ul style="line-height: 2;">
                    <li>Diabetes</li>
                    <li>High blood pressure</li>
                    <li>Obesity</li>
                    <li>Family history of kidney disease</li>
                    <li>Age (older adults)</li>
                    <li>Certain medications</li>
                    <li>Smoking</li>
                </ul>
            </div>

            <div style="background: #f9f9f9; padding: 15px; border-radius: 8px; margin-bottom: 20px;">
                <h3>Prevention & Management</h3>
                <ul style="line-height: 2;">
                    <li>Control blood pressure</li>
                    <li>Manage diabetes effectively</li>
                    <li>Maintain healthy weight</li>
                    <li>Regular exercise</li>
                    <li>Healthy diet (low sodium)</li>
                    <li>Avoid smoking</li>
                    <li>Regular medical check-ups</li>
                    <li>Monitor kidney function tests</li>
                </ul>
            </div>

            <div style="background: #fff5f5; padding: 15px; border-radius: 8px; border-left: 4px solid #dc3545;">
                <strong>⚠️ Important:</strong> Early detection and management of CKD can slow or prevent disease progression. 
                Consult a healthcare professional for proper diagnosis and treatment.
            </div>
        </div>
    `;
    
    // Create and show modal
    const modal = document.createElement('div');
    modal.style.cssText = `
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: rgba(0, 0, 0, 0.5);
        display: flex;
        justify-content: center;
        align-items: center;
        z-index: 10000;
        animation: fadeIn 0.3s ease-out;
    `;
    
    const content = document.createElement('div');
    content.style.cssText = `
        background: white;
        border-radius: 12px;
        max-width: 600px;
        width: 90%;
        max-height: 90vh;
        overflow-y: auto;
        padding: 30px;
        box-shadow: 0 10px 40px rgba(0, 0, 0, 0.3);
        animation: slideUp 0.3s ease-out;
    `;
    
    content.innerHTML = infoHTML + `
        <div style="text-align: center; margin-top: 20px;">
            <button onclick="this.closest('[style*=fixed]').remove()" 
                    style="padding: 10px 30px; background: #667eea; color: white; border: none; border-radius: 6px; cursor: pointer; font-size: 1em;">
                Close
            </button>
        </div>
    `;
    
    // Apply blur to the dashboard background while modal is active.
    document.body.classList.add('modal-open-blur');

    modal.appendChild(content);
    document.body.appendChild(modal);

    function closeModal() {
        if (modal && modal.parentNode) {
            modal.parentNode.removeChild(modal);
        }
        document.body.classList.remove('modal-open-blur');
    }

    const closeBtn = content.querySelector('button');
    if (closeBtn) {
        closeBtn.addEventListener('click', closeModal);
    }

    modal.addEventListener('click', (event) => {
        if (event.target === modal) {
            closeModal();
        }
    });
}
