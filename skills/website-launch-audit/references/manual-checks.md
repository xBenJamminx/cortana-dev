# Additional Manual Checks

Automated checks catch common issues, but these require manual verification:

## Pre-Launch Checklist

### Security
- [ ] HTTPS enforced in production
- [ ] Security headers configured (CSP, HSTS, X-Frame-Options)
- [ ] Authentication flows tested
- [ ] Rate limiting on API routes
- [ ] Input validation on all forms
- [ ] CORS configured correctly

### Performance
- [ ] Images optimized and using next/image or similar
- [ ] Lazy loading for below-fold content
- [ ] Bundle size acceptable (check with `npm run build`)
- [ ] No render-blocking resources
- [ ] Caching headers configured

### Cross-Browser
- [ ] Tested in Chrome, Firefox, Safari, Edge
- [ ] Mobile responsive at all breakpoints
- [ ] Touch interactions work on mobile

### Content
- [ ] All placeholder text replaced
- [ ] Lorem ipsum removed
- [ ] Contact information correct
- [ ] Legal pages present (Privacy Policy, Terms)
- [ ] 404 page exists and is styled

### Analytics & Monitoring
- [ ] Analytics installed and tracking
- [ ] Error tracking configured (Sentry, etc.)
- [ ] Performance monitoring set up

### React Native Specific
- [ ] Tested on physical iOS device
- [ ] Tested on physical Android device
- [ ] App store assets prepared (screenshots, descriptions)
- [ ] Push notifications configured and tested
- [ ] Deep links work correctly
- [ ] Offline behavior acceptable

## Running Lighthouse

For detailed performance/accessibility scoring:

```bash
npx lighthouse http://localhost:3000 --output html --output-path ./lighthouse-report.html
```

## Checking Bundle Size

```bash
# Next.js
npm run build
# Check .next/analyze if @next/bundle-analyzer is installed

# React (Create React App)
npm run build
npx source-map-explorer 'build/static/js/*.js'
```
