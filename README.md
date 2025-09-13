# Caps Pharmacy
This project is based on data from my pharmacy in Ghana that I am tracking
using R and shinyapp to develop a dashboard 
for my staff and investors to know where we are financially
 
## HTML to PDF Renderer
Generate a print-ready PDF from an HTML template with {placeholders} replaced by values from a JSON file, using Puppeteer.

### Quick start
1. Ensure Node.js 18+ is installed.
2. Install dependencies:
```bash
npm install
```
3. Render:
```bash
npm run render -- data.json template.html output.pdf
```
This creates `output.pdf` in the project root.

### Placeholder rules
- Placeholders use braces: {first_name}, {address_1.city}
- Nested JSON keys are supported via dot notation.
- Missing values render as empty strings.

### Direct CLI
```bash
node render.js <data.json> <template.html> <output.pdf>
```
