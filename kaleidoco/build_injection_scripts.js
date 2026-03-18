// Converts a reference HTML into chunked Webflow injection scripts
// Uses global string accumulation pattern to safely split HTML
// Usage: node build_injection_scripts.js v4

const fs = require('fs');
const version = process.argv[2] || 'v4';
const html = fs.readFileSync(`${version}_reference.html`, 'utf8');

// Minify HTML - remove comments, collapse whitespace, but preserve attribute values
function minifyHTML(str) {
  return str
    .replace(/<!--[\s\S]*?-->/g, '')  // remove HTML comments
    .replace(/\r?\n\s*/g, ' ')        // collapse newlines + indent
    .replace(/\s{2,}/g, ' ')          // collapse multiple spaces
    .trim();
}

// Escape for JS single-quoted string
function escJS(str) {
  return str
    .replace(/\\/g, '\\\\')
    .replace(/'/g, "\\'");
}

// Extract CSS from first <style> block
function extractCSS(html) {
  const m = html.match(/<style>([\s\S]*?)<\/style>/);
  return m ? m[1] : '';
}

// Extract the root div content (everything from the root div opening to last </div>)
function extractBody(html) {
  // Find the opening root div
  const startMatch = html.match(/<div id="v\d+-root"[^>]*>/);
  if (!startMatch) return html;
  const start = html.indexOf(startMatch[0]) + startMatch[0].length;
  // Find the last </div> before any trailing <script>
  const bodyPart = html.slice(start);
  // Remove any trailing <script> blocks
  const withoutTrailingScript = bodyPart.replace(/<script[\s\S]*?<\/script>\s*$/, '').trim();
  // Find the last </div>
  const lastDiv = withoutTrailingScript.lastIndexOf('</div>');
  return lastDiv >= 0 ? withoutTrailingScript.slice(0, lastDiv) : withoutTrailingScript;
}

// Extract trailing script blocks (for carousel JS etc)
function extractTrailingScript(html) {
  const m = html.match(/<script>([\s\S]*?)<\/script>\s*$/);
  return m ? m[1].trim() : '';
}

// Build injection scripts
const css = extractCSS(html);
const bodyHTML = extractBody(html);
const minBody = minifyHTML(bodyHTML);
const glVar = `_${version}`;

const allScripts = [];
const BUDGET = 1800;

// Script 1: CSS injection (header)
if (css) {
  const minCSS = css.replace(/\r?\n\s*/g, ' ').replace(/\s{2,}/g, ' ').trim();
  const cssEscaped = escJS(minCSS);
  const cssScript = `(function(){var s=document.createElement('style');s.textContent='${cssEscaped}';document.head.appendChild(s);})();`;
  if (cssScript.length > BUDGET) {
    console.warn(`WARNING: CSS script is ${cssScript.length} chars, over budget!`);
  }
  allScripts.push({ name: `${version}css`, code: cssScript, location: 'header' });
}

// Scripts 2+: body HTML split into chunks via global accumulator
const escaped = escJS(minBody);
const chunks = [];
let pos = 0;
while (pos < escaped.length) {
  // Find a safe split point near BUDGET - 60 chars (room for wrapper)
  const maxChunk = BUDGET - 60;
  let end = Math.min(pos + maxChunk, escaped.length);
  // Walk back to find a safe character boundary (not in middle of escape sequence)
  // Ensure we don't split after a backslash
  while (end > pos && escaped[end-1] === '\\' && end < escaped.length) end++;
  chunks.push(escaped.slice(pos, end));
  pos = end;
}

// First chunk: initialize variable
const firstChunk = chunks[0];
const initScript = `window.${glVar}=window.${glVar}||'';window.${glVar}+='${firstChunk}';`;
allScripts.push({ name: `${version}h1`, code: initScript, location: 'footer' });

// Middle chunks: append
for (let i = 1; i < chunks.length - 1; i++) {
  const code = `window.${glVar}+='${chunks[i]}';`;
  allScripts.push({ name: `${version}h${i+1}`, code, location: 'footer' });
}

// Extract and prepare any trailing JS (e.g. carousel init)
const trailingJS = extractTrailingScript(html);

// Last chunk: append AND inject (+ optionally run trailing JS after DOM ready)
const injectFn = trailingJS
  ? `(function(){var r=document.getElementById('${version}-root');if(!r){r=document.createElement('div');r.id='${version}-root';document.body.appendChild(r);}r.innerHTML=window.${glVar};delete window.${glVar};${trailingJS.replace(/\s+/g,' ').trim()}})();`
  : `(function(){var r=document.getElementById('${version}-root');if(!r){r=document.createElement('div');r.id='${version}-root';document.body.appendChild(r);}r.innerHTML=window.${glVar};delete window.${glVar};})();`;

if (chunks.length > 1) {
  const lastChunk = chunks[chunks.length - 1];
  const finalScript = `window.${glVar}+='${lastChunk}';${injectFn}`;
  allScripts.push({ name: `${version}h${chunks.length}`, code: finalScript, location: 'footer' });
} else {
  // Only one chunk — inject directly
  const finalScript = `(function(){var r=document.getElementById('${version}-root');if(!r){r=document.createElement('div');r.id='${version}-root';document.body.appendChild(r);}r.innerHTML='${firstChunk}';${trailingJS ? trailingJS.replace(/\s+/g,' ').trim() : ''}})();`;
  allScripts[allScripts.length - 1].code = finalScript;
}

// Output
console.log(`Generated ${allScripts.length} scripts for ${version}:`);
let totalChars = 0;
allScripts.forEach((s, i) => {
  totalChars += s.code.length;
  const over = s.code.length > BUDGET ? ' *** OVER BUDGET ***' : '';
  console.log(`  Script ${i+1}: ${s.name} (${s.location}, ${s.code.length} chars)${over}`);
  if (s.code.length > BUDGET) {
    console.log(`    Code starts: ${s.code.substring(0, 100)}`);
  }
});
console.log(`Total: ${totalChars} chars across ${allScripts.length} scripts`);
console.log(`Body HTML (minified): ${minBody.length} chars`);

// Write to JSON file
fs.writeFileSync(`${version}_scripts.json`, JSON.stringify(allScripts, null, 2));
console.log(`Written to ${version}_scripts.json`);
