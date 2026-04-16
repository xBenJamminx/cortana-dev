const fs = require('fs');
const path = require('path');

const html = fs.readFileSync(path.join(__dirname, 'v6_reference.html'), 'utf8');

// Extract <style> block content
const styleMatch = html.match(/<style>([\s\S]*?)<\/style>/);
const cssContent = styleMatch[1].replace(/\s+/g, ' ').trim().replace(/'/g, "\\'");

// Build CSS injection script
const cssScript = `(function(){var s=document.createElement('style');s.textContent='${cssContent}';document.head.appendChild(s);})();`;

// Extract everything inside <div id="v6-root"> ... </div>
// Find the opening tag
const rootOpenMatch = html.match(/<div id="v6-root"[^>]*>/);
const rootOpenIdx = html.indexOf(rootOpenMatch[0]);
const innerStart = rootOpenIdx + rootOpenMatch[0].length;

// Find the closing </div> - it's the last </div> in the file
const lastDivClose = html.lastIndexOf('</div>');
const innerHtml = html.substring(innerStart, lastDivClose);

// Minify: collapse whitespace to single spaces, trim
const minified = innerHtml.replace(/\s+/g, ' ').trim();

// Escape for JS string (single quotes)
const escaped = minified.replace(/\\/g, '\\\\').replace(/'/g, "\\'");

// Split into chunks for accumulator pattern
const MAX_CHUNK = 1950;
const scripts = [];

// Script 1: CSS (header)
scripts.push({ name: 'v6css', code: cssScript, location: 'header' });

// Calculate overhead for each script type
// First HTML script: window._v6='CHUNK';
// Middle HTML scripts: window._v6+='CHUNK';
// Last HTML script: window._v6+='CHUNK';(function(){var r=document.getElementById('v6-root');if(r)r.innerHTML=window._v6;})();

const initPrefix = "window._v6='";
const initSuffix = "';";
const contPrefix = "window._v6+='";
const contSuffix = "';";
const finalSuffix = "';(function(){var r=document.getElementById('v6-root');if(r)r.innerHTML=window._v6;})();";

// Split escaped HTML into chunks
let remaining = escaped;
let chunkIndex = 0;
const htmlChunks = [];

while (remaining.length > 0) {
  let maxContent;
  if (chunkIndex === 0) {
    // First chunk
    maxContent = MAX_CHUNK - initPrefix.length - initSuffix.length;
  } else {
    // Reserve space for potential final suffix
    maxContent = MAX_CHUNK - contPrefix.length - finalSuffix.length;
  }

  // Don't split in the middle of an escape sequence
  let cutPoint = Math.min(maxContent, remaining.length);
  // Check if we're cutting in the middle of an escape like \'
  if (cutPoint < remaining.length) {
    // Look back a couple chars to avoid splitting escape sequences
    if (remaining[cutPoint - 1] === '\\') {
      cutPoint--;
    }
  }

  htmlChunks.push(remaining.substring(0, cutPoint));
  remaining = remaining.substring(cutPoint);
  chunkIndex++;
}

// Now build scripts from chunks
for (let i = 0; i < htmlChunks.length; i++) {
  const chunk = htmlChunks[i];
  let code;

  if (i === 0 && htmlChunks.length === 1) {
    // Only one chunk - init and inject
    code = `window._v6='${chunk}';(function(){var r=document.getElementById('v6-root');if(r)r.innerHTML=window._v6;})();`;
  } else if (i === 0) {
    // First of multiple
    code = `window._v6='${chunk}';`;
  } else if (i === htmlChunks.length - 1) {
    // Last chunk - append and inject
    code = `window._v6+='${chunk}';(function(){var r=document.getElementById('v6-root');if(r)r.innerHTML=window._v6;})();`;
  } else {
    // Middle chunk
    code = `window._v6+='${chunk}';`;
  }

  const name = `v6h${i + 1}`;
  scripts.push({ name, code, location: 'footer' });
}

// Validate all scripts are under 1950 chars (with some buffer for 2000 Webflow limit)
for (const s of scripts) {
  if (s.code.length > 2000) {
    console.error(`WARNING: Script ${s.name} is ${s.code.length} chars (over 2000 limit)`);
  } else {
    console.log(`${s.name}: ${s.code.length} chars [${s.location}]`);
  }
}

// Save
const outputPath = path.join(__dirname, 'v6_scripts.json');
fs.writeFileSync(outputPath, JSON.stringify(scripts, null, 2));
console.log(`\nSaved ${scripts.length} scripts to ${outputPath}`);
