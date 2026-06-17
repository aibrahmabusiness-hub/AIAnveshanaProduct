const autocompleteLogic = `
// ==========================================
// @ Autocomplete Logic
// ==========================================
let acDropdown = document.getElementById('autocompleteDropdown');
let acCurrentInput = null;
let acOptions = [];
let acSelectedIndex = -1;
let acQuery = '';

// Listen for input on the document, but only act on text inputs or textareas inside workflow configuration
document.addEventListener('input', (e) => {
    if (!e.target.matches('input[type="text"], textarea')) return;
    
    // Check if the input is inside the workflow editor modal (e.g. step settings)
    const modal = e.target.closest('#stepSettingsModal');
    if (!modal) return;
    
    const val = e.target.value;
    const cursorPos = e.target.selectionStart;
    
    // Check if we are typing after an '@'
    const textBeforeCursor = val.substring(0, cursorPos);
    const atIndex = textBeforeCursor.lastIndexOf('@');
    
    if (atIndex !== -1) {
        // Ensure the '@' is either at the beginning or preceded by a space/newline/bracket
        const prevChar = atIndex > 0 ? textBeforeCursor[atIndex - 1] : ' ';
        if (/[\\s\\{\\[\\(]/.test(prevChar)) {
            acQuery = textBeforeCursor.substring(atIndex + 1);
            if (!acQuery.includes(' ')) {
                acCurrentInput = e.target;
                showAutocomplete(e.target, acQuery);
                return;
            }
        }
    }
    
    hideAutocomplete();
});

document.addEventListener('keydown', (e) => {
    if (!acDropdown || acDropdown.style.display === 'none') return;
    
    if (e.key === 'ArrowDown') {
        e.preventDefault();
        acSelectedIndex = Math.min(acSelectedIndex + 1, acOptions.length - 1);
        updateAutocompleteSelection();
    } else if (e.key === 'ArrowUp') {
        e.preventDefault();
        acSelectedIndex = Math.max(acSelectedIndex - 1, 0);
        updateAutocompleteSelection();
    } else if (e.key === 'Enter') {
        e.preventDefault();
        if (acSelectedIndex >= 0 && acSelectedIndex < acOptions.length) {
            selectAutocompleteOption(acOptions[acSelectedIndex]);
        }
    } else if (e.key === 'Escape') {
        hideAutocomplete();
    }
});

document.addEventListener('click', (e) => {
    if (acDropdown && !acDropdown.contains(e.target) && e.target !== acCurrentInput) {
        hideAutocomplete();
    }
});

function getAvailableVariables() {
    let vars = [];
    // Try to get from NODE_SCHEMAS or the rendered canvas
    
    const nodesOnCanvas = document.querySelectorAll('.canvas-node');
    nodesOnCanvas.forEach(node => {
        const titleEl = node.querySelector('.node-title');
        const stepName = titleEl ? titleEl.textContent : (node.dataset.id || 'step');
        // create a valid reference name
        const refName = stepName.toLowerCase().replace(/[^a-z0-9_]/g, '_');
        
        vars.push({ step: stepName, val: \`{{\${refName}}}\` });
        vars.push({ step: stepName + ' (Body)', val: \`{{\${refName}.body}}\` });
    });
    
    // Add some common predefined variables if no nodes are found (or just always)
    if (vars.length === 0) {
        vars.push({ step: 'Webhook Trigger (Body)', val: '{{trigger.body}}' });
        vars.push({ step: 'Webhook Trigger (Headers)', val: '{{trigger.headers}}' });
        vars.push({ step: 'Manual Trigger (Data)', val: '{{trigger.data}}' });
    }
    
    return vars;
}

function showAutocomplete(inputElement, query) {
    if (!acDropdown) {
        acDropdown = document.getElementById('autocompleteDropdown');
        if (!acDropdown) return;
    }

    let allVars = getAvailableVariables();
    acOptions = allVars.filter(v => v.step.toLowerCase().includes(query.toLowerCase()) || v.val.toLowerCase().includes(query.toLowerCase()));
    
    if (acOptions.length === 0) {
        hideAutocomplete();
        return;
    }
    
    acSelectedIndex = 0;
    
    const rect = inputElement.getBoundingClientRect();
    
    // Position below the input
    acDropdown.style.top = (rect.bottom + window.scrollY + 5) + 'px';
    acDropdown.style.left = (rect.left + window.scrollX) + 'px';
    acDropdown.style.width = Math.max(rect.width, 250) + 'px';
    
    renderAutocomplete();
    acDropdown.style.display = 'block';
}

function renderAutocomplete() {
    acDropdown.innerHTML = acOptions.map((opt, idx) => \`
        <div class="autocomplete-item \${idx === acSelectedIndex ? 'selected' : ''}" data-index="\${idx}">
            <div class="autocomplete-item-step">\${opt.step}</div>
            <div class="autocomplete-item-var">\${opt.val}</div>
        </div>
    \`).join('');
    
    acDropdown.querySelectorAll('.autocomplete-item').forEach(item => {
        item.addEventListener('click', () => {
            selectAutocompleteOption(acOptions[parseInt(item.dataset.index)]);
        });
        item.addEventListener('mouseover', () => {
            acSelectedIndex = parseInt(item.dataset.index);
            updateAutocompleteSelection();
        });
    });
}

function updateAutocompleteSelection() {
    const items = acDropdown.querySelectorAll('.autocomplete-item');
    items.forEach((item, idx) => {
        if (idx === acSelectedIndex) {
            item.classList.add('selected');
            item.scrollIntoView({ block: 'nearest' });
        } else {
            item.classList.remove('selected');
        }
    });
}

function selectAutocompleteOption(option) {
    if (!acCurrentInput) return;
    
    const val = acCurrentInput.value;
    const cursorPos = acCurrentInput.selectionStart;
    
    const textBeforeCursor = val.substring(0, cursorPos);
    const atIndex = textBeforeCursor.lastIndexOf('@');
    
    if (atIndex !== -1) {
        const textAfterCursor = val.substring(cursorPos);
        const newText = textBeforeCursor.substring(0, atIndex) + option.val + textAfterCursor;
        
        acCurrentInput.value = newText;
        
        // Restore cursor position
        const newCursorPos = atIndex + option.val.length;
        acCurrentInput.setSelectionRange(newCursorPos, newCursorPos);
        
        // Trigger input event to update model if necessary
        acCurrentInput.dispatchEvent(new Event('input', { bubbles: true }));
    }
    
    hideAutocomplete();
}

function hideAutocomplete() {
    if (acDropdown) acDropdown.style.display = 'none';
    acCurrentInput = null;
}
`;

const fs = require('fs');
let content = fs.readFileSync('C:/Users/Admin/Documents/Agentic AI/frontend/project.js', 'utf-8');
if (!content.includes('Autocomplete Logic')) {
    content += '\n' + autocompleteLogic;
    fs.writeFileSync('C:/Users/Admin/Documents/Agentic AI/frontend/project.js', content, 'utf-8');
}
