const fs = require('fs');
let content = fs.readFileSync('frontend/project.js', 'utf8');

// Replace the duplicate create workflow button in the empty state
content = content.replace(
    '<button class="btn-primary" onclick="createNewWorkflow()">+ Create Workflow</button>',
    ''
);

fs.writeFileSync('frontend/project.js', content, 'utf8');
