const fs = require('fs');
const scripts = require('./v5_scripts.json');

const fixed = scripts.map(sc => {
  let code = sc.code;
  // After JSON parse, code contains literal \' around font names
  // Replace \'Dosis\' and \'Titillium Web\' with unquoted versions
  code = code.replace(/\\'Dosis\\'/g, 'Dosis');
  code = code.replace(/\\'Titillium Web\\'/g, 'Titillium Web');
  return {...sc, code};
});

let issues = 0;
fixed.forEach(sc => {
  const rem = (sc.code.match(/\\'[A-Za-z]/g) || []).length;
  if (rem) { console.log('STILL HAS:', sc.name, rem); issues++; }
});

if (issues === 0) {
  console.log('All font quote escapes removed.');
  fs.writeFileSync('./v5_scripts_fixed.json', JSON.stringify(fixed, null, 2));
  console.log('Written v5_scripts_fixed.json');
  // Show sample
  const orig = scripts.find(s=>s.name==='v5h1');
  const fix = fixed.find(s=>s.name==='v5h1');
  const idx = orig.code.indexOf("Dosis");
  console.log('Before:', orig.code.substring(idx-15, idx+15));
  const idx2 = fix.code.indexOf("Dosis");
  console.log('After: ', fix.code.substring(idx2-15, idx2+15));
}
