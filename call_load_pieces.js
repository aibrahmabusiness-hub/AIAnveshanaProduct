const fs = require('fs');
let content = fs.readFileSync('frontend/project.js', 'utf8');

content = content.replace(
    'document.getElementById(\'workflowModal\').classList.add(\'active\');',
    'document.getElementById(\'workflowModal\').classList.add(\'active\');\n    loadPieces();'
);

fs.writeFileSync('frontend/project.js', content, 'utf8');
