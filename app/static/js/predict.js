/**
 * CKD Prediction Form Handler
 * Handles form validation, submission, and result display
 */

document.addEventListener('DOMContentLoaded', function() {
    // Get form element
    const form = document.getElementById('predictionForm');
    
    // Add form submission handler
    if (form) {
        form.addEventListener('submit', handleFormSubmit);
    }
});

/**
 * Handle form submission
 * Validates form data, sends to prediction API, and displays results
 */
function handleFormSubmit(e) {
    e.preventDefault();
    
    // Show loading spinner
    showLoadingSpinner();
    
    // Collect form data
    const formData = getFormData();
    
    // Validate form data
    if (!validateFormData(formData)) {
        hideLoadingSpinner();
        alert('Please fill all required fields correctly');
        return;
    }
    
    // Send prediction request to API
    fetch('/api/predict', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(formData)
    })
    .then(async response => {
        if (!response.ok) {
            let message = `HTTP ${response.status} ${response.statusText}`;
            try {
                const body = await response.text();
                if (body) {
                    message += ` - ${body}`;
                }
            } catch (err) {
                console.warn('Unable to read error body:', err);
            }
            throw new Error(message);
        }
        return response.json();
    })
    .then(data => {
        hideLoadingSpinner();
        
        if (data.success) {
            // Display results
            displayResults(data);
        } else {
            console.error('Prediction returned failure:', data);
            alert('Prediction failed: ' + (data.error || 'Server did not return valid result.'));
            const resultContent = document.getElementById('resultContent');
            if (resultContent) {
                resultContent.innerHTML = `<div class="result-card risk-low">` +
                    `<h3 class="result-title">Unable to generate result</h3>` +
                    `<p>Please try again, or contact support if the issue persists.</p>` +
                    `</div>`;
                document.getElementById('resultModal').classList.remove('hidden');
                document.body.classList.add('modal-open-blur');
            }
        }
    })
    .catch(error => {
        hideLoadingSpinner();
        console.error('Error:', error);
        alert('Error submitting form: ' + error.message);
    });
}

/**
 * Collect all form data into an object
 */
function getFormData() {
    const form = document.getElementById('predictionForm');
    const formData = new FormData(form);
    
    const data = {};
    formData.forEach((value, key) => {
        data[key] = value;
    });
    
    return data;
}

/**
 * Validate form data - check for empty fields
 */
function validateFormData(data) {
    const requiredFields = [
        'age',
        'bp', 'sg', 'al', 'su', 'rbc', 'pc', 'pcc', 'ba',
        'bgr', 'bu', 'sc', 'sod', 'pot',
        'hemo', 'pcv', 'wc', 'rc',
        'htn', 'dm', 'cad', 'appet', 'pe', 'ane'
    ];
    
    for (let field of requiredFields) {
        if (!data[field] || data[field].trim() === '') {
            console.log('Missing field:', field);
            return false;
        }
    }
    
    // Validate numeric fields
    const numericFields = ['age', 'bp', 'sg', 'al', 'su', 'bgr', 'bu', 'sc', 'sod', 'pot', 'hemo', 'pcv', 'wc', 'rc'];
    for (let field of numericFields) {
        const value = parseFloat(data[field]);
        if (isNaN(value) || value < 0) {
            console.log('Invalid numeric value for:', field);
            return false;
        }
    }
    
    return true;
}

/**
 * Display prediction results in modal
 */
function displayResults(data) {
    const recommendations = data.recommendations;
    const smartSuggestions = Array.isArray(data.smart_suggestions) ? data.smart_suggestions : [];
    const explanation = data.explanation || {};
    const explanationSummary = explanation.summary || 'No additional explanation available.';
    const explanationFactors = Array.isArray(explanation.factors) ? explanation.factors : [];
    const riskClass = data.risk_level === 'High Risk' ? 'risk-high' : 'risk-low';
    const riskIcon = data.risk_level === 'High Risk' ? 'HIGH' : 'LOW';
    const confidence = Number.isFinite(Number(data.confidence)) ? Number(data.confidence).toFixed(2) : data.confidence;
    const highRiskProbability = Number.isFinite(Number(data.high_risk_probability))
        ? Number(data.high_risk_probability).toFixed(2)
        : null;
    
    // Create result HTML
    let html = `
        <div class="result-card ${riskClass}">
            <div style="font-size: 3em; margin-bottom: 15px;">
                ${riskIcon}
            </div>
            <h3 class="result-title">${recommendations.title}</h3>
            <p style="margin-bottom: 20px; font-size: 1.05em; color: #666;">
                ${recommendations.message}
            </p>
            
            <div style="background: rgba(0,0,0,0.05); padding: 15px; border-radius: 6px; margin-bottom: 20px;">
                <p><strong>Confidence Level:</strong> ${confidence}%</p>
                <p><strong>Prediction Result:</strong> ${data.risk_level}</p>
                ${highRiskProbability !== null ? `<p><strong>High Risk Probability:</strong> ${highRiskProbability}%</p>` : ''}
            </div>

            <h4 style="margin-top: 20px; margin-bottom: 10px; color: #333;">Why this result?</h4>
            <p style="color: #555; margin-bottom: 10px; line-height: 1.6;">${explanationSummary}</p>
            <ul style="line-height: 1.8; color: #555; margin-bottom: 20px;">
    `;

    explanationFactors.forEach(factor => {
        html += `<li>${factor}</li>`;
    });

    html += `
            </ul>
            
            <h4 style="margin-top: 25px; margin-bottom: 15px; color: #333;">General Recommendations:</h4>
            <ul style="line-height: 2; color: #555;">
    `;
    
    // Add recommendations
    recommendations.recommendations.forEach(rec => {
        html += `<li>✓ ${rec}</li>`;
    });
    
    html += `
            </ul>

            <h4 style="margin-top: 25px; margin-bottom: 15px; color: #333;">Smart Health Suggestions:</h4>
            <ul style="line-height: 1.9; color: #555;">
    `;

    smartSuggestions.forEach(suggestion => {
        html += `<li>${suggestion}</li>`;
    });

    html += `
            </ul>
            
            <div style="background: #f0f4ff; padding: 15px; border-radius: 6px; margin-top: 20px; border-left: 4px solid #667eea;">
                <p style="margin: 0; color: #555;">
                    <strong>Note:</strong> This prediction is for informational purposes only. 
                    Please consult a qualified healthcare professional for proper diagnosis and treatment.
                </p>
            </div>

            <div style="margin-top: 20px;">
                ${data.pdf_report_url ? `<a href="${data.pdf_report_url}" class="btn btn-outline" target="_blank" rel="noopener noreferrer">Download PDF Report</a>` : ''}
                ${data.show_consult_suggestion ? `<a href="${data.consult_doctor_url}" class="btn btn-primary" style="margin-left: 8px;">Consult a Doctor</a>` : ''}
            </div>
        </div>
    `;
    
    // Fill modal with results
    document.getElementById('resultContent').innerHTML = html;
    
    // Show modal
    document.getElementById('resultModal').classList.remove('hidden');
    document.body.classList.add('modal-open-blur');
    
    // Scroll to modal
    document.getElementById('resultModal').scrollIntoView({ behavior: 'smooth' });
}

/**
 * Close results modal
 */
function closeResultModal() {
    document.getElementById('resultModal').classList.add('hidden');
    document.body.classList.remove('modal-open-blur');
    
    // Optionally reset form
    // document.getElementById('predictionForm').reset();
}

/**
 * Show loading spinner during prediction
 */
function showLoadingSpinner() {
    document.getElementById('loadingSpinner').classList.remove('hidden');
}

/**
 * Hide loading spinner
 */
function hideLoadingSpinner() {
    document.getElementById('loadingSpinner').classList.add('hidden');
}

/**
 * Reset form and results
 */
function resetPredictionForm() {
    document.getElementById('predictionForm').reset();
    closeResultModal();
}

/**
 * Print results
 */
function printResults() {
    window.print();
}

/**
 * Download results as PDF (requires additional library)
 */
function downloadResultsPDF() {
    const resultContent = document.getElementById('resultContent').innerHTML;
    const printWindow = window.open('', '', 'width=800,height=600');
    printWindow.document.write(`
        <html>
            <head>
                <title>CKD Prediction Results</title>
                <style>
                    body { font-family: Arial, sans-serif; margin: 20px; }
                    .result-card { padding: 20px; border: 1px solid #ddd; }
                </style>
            </head>
            <body>${resultContent}</body>
        </html>
    `);
    printWindow.document.close();
    printWindow.print();
}
