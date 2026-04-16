const vm = require('vm');
const fs = require('fs');
const path = require('path');
const dir = path.join(__dirname, 'scripts');

const files = fs.readdirSync(dir).filter(f => f.endsWith('.js'));
let found = false;
for (const file of files) {
  const code = fs.readFileSync(path.join(dir, file), 'utf8');
  try {
    new vm.Script(code);
    console.log('OK: ' + file);
  } catch (e) {
    console.log('SYNTAX ERROR: ' + file + ' --- ' + e.message);
    found = true;
  }
}
if (!found) console.log('All scripts passed syntax check.');
