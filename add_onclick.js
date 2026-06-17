const fs = require('fs');
let content = fs.readFileSync('frontend/project.html', 'utf8');

content = content.replace(
    '<button class="btn-primary" id="createNewWorkflowBtn">+ Create Workflow</button>',
    '<button class="btn-primary" id="createNewWorkflowBtn" onclick="createNewWorkflow()">+ Create Workflow</button>'
);

fs.writeFileSync('frontend/project.html', content, 'utf8');
