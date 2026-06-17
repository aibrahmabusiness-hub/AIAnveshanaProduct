const fs = require('fs');
const extraCode = fs.readFileSync('add_load_pieces.js', 'utf8');
let content = fs.readFileSync('frontend/project.js', 'utf8');
content += '\n' + extraCode;
fs.writeFileSync('frontend/project.js', content, 'utf8');
