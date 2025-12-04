# Web Automation Knowledge Base

## Common Challenges & Solutions

This knowledge base helps you automatically handle common web automation patterns and errors without asking the user for permission.

---

## 1. 🚫 Modals, Pop-ups, and Overlays

### Problem
Modals, overlays, or pop-ups block interaction with the underlying page.

### Common Types
- Cookie consent banners
- Email signup prompts
- Location/notification permission requests
- Marketing offers
- Exit-intent pop-ups
- Age verification dialogs
- Chat widgets

### Automatic Resolution
**ALWAYS attempt to close these automatically using one of these methods:**

1. **Close button (X)**: Look for buttons with:
   - `role="button"` with names like: "Close", "Dismiss", "No thanks", "×", "✕"
   - `aria-label` containing: "close", "dismiss", "cancel"
   
2. **Reject/Decline buttons**:
   - "Reject All", "Decline", "No Thanks", "Maybe Later", "Continue without"
   
3. **Escape key**: Press `Escape` key to close modal
   
4. **Click overlay background**: If modal has a backdrop, click outside the modal

**Example actions:**
```javascript
// Try in this order:
1. browser_press_key({ key: "Escape" })
2. browser_click({ element: "Close button", ref: "[aria-label='Close']" })
3. browser_click({ element: "Reject button", ref: "button:has-text('Reject All')" })
```

### Never Ask User
❌ DON'T: "A modal is blocking the page. Should I close it?"
✅ DO: Automatically close it and continue the workflow

---

## 2. 🍪 Cookie Consent Banners

### Problem
GDPR/privacy consent banners appear on first visit.

### Automatic Resolution
**Priority order:**
1. **Reject All** (preferred for automation)
2. **Accept All** (if no reject option)
3. **Close/Dismiss**

**Common text patterns:**
- "Reject All", "Reject All Cookies"
- "Accept All", "Accept All Cookies"
- "Continue without accepting"
- "Only necessary cookies"

**Example:**
```javascript
// Try reject first
browser_click({ element: "Reject cookies button", ref: "button:has-text('Reject')" })
// Or accept if no reject
browser_click({ element: "Accept cookies button", ref: "button:has-text('Accept All')" })
```

---

## 3. ⏳ Loading States and Spinners

### Problem
Content is still loading; elements not yet available.

### Automatic Resolution
1. **Wait for loading indicator to disappear**:
   ```javascript
   browser_wait_for({ textGone: "Loading..." })
   ```

2. **Wait for expected content**:
   ```javascript
   browser_wait_for({ text: "Search Results" })
   ```

3. **Take snapshot to check state**:
   ```javascript
   browser_snapshot()
   ```

### Common Loading Indicators
- "Loading...", "Please wait..."
- Spinner icons
- Progress bars
- Skeleton screens

### Strategy
- Always wait for loading indicators to disappear before interacting
- If action fails, take snapshot and retry after ensuring page is ready
- Use `browser_wait_for` proactively

---

## 4. 🔄 Dynamic Content & AJAX

### Problem
Content loads dynamically after initial page load.

### Automatic Resolution
1. **Wait for specific element to appear**:
   ```javascript
   browser_wait_for({ text: "Product Name" })
   ```

2. **Take snapshot to verify content loaded**:
   ```javascript
   browser_snapshot()
   ```

3. **Retry if element not found**: Wait 2-3 seconds and retry

### Never
- ❌ Give up after first attempt
- ❌ Ask user if content didn't load yet

---

## 5. 📝 Form Field Variations

### Problem
Login forms use different field names (username vs email, user vs login, etc.).

### Automatic Resolution
When looking for login fields in snapshots:

**Username/Email Field** - Look for any of:
- "username"
- "email" 
- "user"
- "login"
- "account"
- "id"

**Password Field** - Look for:
- "password"
- "pass"
- "pwd"

**Strategy:**
1. Take snapshot of login page
2. Search for textbox with ANY username/email-related name
3. Use the credentials provided (even if field says "username", use the email value)
4. Be flexible with field labels

**Example:**
```javascript
// Progressive uses "username" but credentials have "email"
// ✅ Correct: Use email value in username field
browser_type({ 
  element: "Username field", 
  ref: "[name='username']", 
  text: "user@example.com"  // Use email value
})
```

---

## 6. 📝 Form Validation Errors

### Problem
Form submission fails due to validation.

### Automatic Resolution
1. **Check for error messages** in snapshot
2. **Fill missing required fields**
3. **Correct invalid formats** (email, phone, etc.)
4. **Retry submission**

### Common Patterns
- Red text with "required", "invalid", "error"
- Fields with `aria-invalid="true"`
- Error messages near form fields

---

## 7. 🚀 Rate Limiting & Throttling

### Problem
Too many requests trigger rate limiting.

### Automatic Resolution
1. **Slow down**: Add `browser_wait_for({ time: 2 })` between actions
2. **Retry**: Wait and retry the action
3. **Continue**: Don't treat as fatal error

---

## 8. 🎯 Element Not Found

### Problem
Expected element is not in the accessibility tree.

### Automatic Resolution
**Troubleshooting steps:**

1. **Take fresh snapshot**:
   ```javascript
   browser_snapshot()
   ```

2. **Check if page loaded**: Look for loading indicators

3. **Try alternative selectors**:
   - By text content (case-insensitive)
   - By role
   - By nearby elements

4. **Scroll**: Element might be below fold
   ```javascript
   browser_press_key({ key: "PageDown" })
   ```

5. **Wait and retry**: Element might be loading
   ```javascript
   browser_wait_for({ time: 2 })
   browser_snapshot()
   ```

### Never
- ❌ Give up after first failure
- ❌ Ask user immediately

---

## 9. 🛡️ Anti-Bot Detection

### Problem
Website detects automation and shows CAPTCHA or block page.

### Signs
- Text like "unusual traffic", "verify you're human", "CAPTCHA"
- reCAPTCHA widget
- Cloudflare challenge page

### Response
1. **Inform user**: This requires human intervention
2. **Suggest alternatives**: Manual login, different approach
3. **Don't retry repeatedly**: Avoid triggering more blocks

**Example message:**
```
⚠️ The website has detected automation and is showing a CAPTCHA challenge.
This requires human verification and cannot be automated.

Suggestions:
- Run with --extension mode to use your logged-in browser
- Complete CAPTCHA manually in the browser window
- Try again after waiting a few minutes
```

---

## 10. 📱 Responsive Design Changes

### Problem
Elements have different selectors on different screen sizes.

### Automatic Resolution
1. **Try multiple selector patterns**:
   - Mobile menu vs desktop menu
   - Hamburger icon vs full navigation
   - Compressed vs expanded forms

2. **Check viewport**: Use `browser_snapshot()` to see current layout

3. **Resize if needed**:
   ```javascript
   browser_resize({ width: 1920, height: 1080 })
   ```

---

## 11. 🔐 Session Timeouts

### Problem
Session expired during long workflows.

### Automatic Resolution
1. **Detect timeout**: Look for login page or "session expired" messages
2. **Re-login if credentials available**:
   ```javascript
   login_to_site({ site: "rei" })
   ```
3. **Resume workflow** from current step

---

## 12. ⏸️ Manual Steps (MFA, CAPTCHA)

### Problem
Some steps require human interaction (MFA codes, CAPTCHA, manual verification).

### Handling Manual Steps

**For MFA/2FA:**
1. **Complete automation up to MFA**
2. **Report to user** what's needed
3. **Wait with long timeout** (browser_wait_for with 60-120 seconds)
4. **Keep browser open** - Never close during manual steps!
5. **Verify completion** - Check for dashboard/success page after wait

**Example Pattern:**
```javascript
// After login, before MFA
1. browser_snapshot() // See MFA page
2. Report to user: "Please enter MFA code and check 'Remember device'"
3. browser_wait_for({ time: 120 }) // Wait 2 minutes (don't close!)
4. browser_snapshot() // Verify dashboard loaded
5. Continue workflow
```

**Never:**
- ❌ Close browser during manual step
- ❌ Time out too quickly (< 60 seconds)
- ❌ Assume MFA is complete without verification

**Remember:**
- ✅ First-time setup may need manual MFA
- ✅ "Remember this device" prevents future MFA
- ✅ Persistent sessions (PLAYWRIGHT_ISOLATED=false) save device state

---

## 🎯 General Best Practices

### Always Do
✅ **Proactive waiting**: Wait for elements before interacting
✅ **Handle pop-ups automatically**: Close modals/banners without asking
✅ **Retry on failure**: Try 2-3 times before giving up
✅ **Take snapshots**: Get fresh page state when stuck
✅ **Be resilient**: Adapt to unexpected page states
✅ **Wait for manual steps**: Use long timeouts (60-120s) for MFA/CAPTCHA

### Never Do
❌ **Ask for permission** to handle common patterns (modals, cookies, etc.)
❌ **Give up immediately** on first failure
❌ **Assume static page**: Always check for dynamic content
❌ **Ignore errors**: Always attempt recovery
❌ **Close browser during manual steps**: Wait with timeout instead

---

## 🔧 Debugging Workflow

When stuck, follow this sequence:

1. **Take snapshot**: `browser_snapshot()`
2. **Check for blockers**: Modals, loading indicators, errors
3. **Handle blockers**: Close modals, wait for loading
4. **Retry original action**
5. **Try alternative approach**: Different selectors, scrolling
6. **Take another snapshot**: Verify changes
7. **Continue or inform user** (only if truly stuck after retries)

---

## 📊 Success Metrics

A good automation should:
- ✅ Handle 90% of common patterns automatically
- ✅ Recover from transient failures
- ✅ Complete workflows without user intervention
- ✅ Only ask user for truly ambiguous situations

---

## 🚨 When to Ask User

Only ask the user when:
1. **Ambiguous intent**: Multiple valid paths forward
2. **Security/financial**: Confirming purchases, payments
3. **Anti-bot**: CAPTCHA or human verification required
4. **Data input**: User-specific information needed
5. **True error**: All automatic recovery attempts failed

---

## Example: Handling REI Modal

**Bad approach:**
```
"A modal is blocking the page. Should I close it?"
```

**Good approach:**
```javascript
// 1. Detect modal (in snapshot)
// 2. Try Escape key
browser_press_key({ key: "Escape" })

// 3. If still there, try close button
browser_click({ element: "Close modal", ref: "[aria-label='Close']" })

// 4. Continue workflow
// 5. Only report if both failed after retries
```

**Best approach:**
```javascript
// All in one go, with automatic retry
try escape key → try close button → take snapshot → retry workflow step → success!
```

---

*This knowledge base is continuously updated with new patterns and solutions.*

