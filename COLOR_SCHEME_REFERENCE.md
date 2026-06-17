# COLOR SCHEME & DESIGN TOKENS REFERENCE

## LEGACY COLOR SCHEME (frontend/style.css)

### Primary Colors
| Variable | Value | Hex | Purpose |
|----------|-------|-----|---------|
| --primary-color | Electric Green | #10b981 | Main highlights, CTA buttons, active states |
| --orange-primary | Dark Green | #059669 | Active settings, hover states |
| --accent-color | Electric Green | #10b981 | Links, accents |
| --logo-green | Medium Green | #2b8a44 | SVG logo rect fill |
| --logo-dark | Deep Green | #1a5032 | SVG logo circle fill |

### Background Colors
| Variable | Value | Hex | Purpose |
|----------|-------|-----|---------|
| --bg-primary | Soft Green-tint | #f4fbf7 | Page background |
| --bg-secondary | White | #ffffff | Panels, cards, sidebar, header |
| --bg-tertiary | Light Emerald | #ecfdf5 | Sub-panels, empty states, hover |
| --card-bg | White | #ffffff | Card backgrounds |
| --sidebar-bg | White | #ffffff | Sidebar background |

### Text Colors
| Variable | Value | Hex | Purpose |
|----------|-------|-----|---------|
| --text-primary | Matte Black | #000000 | Headings, strong text |
| --text-secondary | Dark Gray | #333333 | Body text |
| --text-muted | Medium Gray | #666666 | Sub-info, captions |

### Status & Feedback
| Variable | Value | Hex | Purpose |
|----------|-------|-----|---------|
| --success-color | Electric Green | #10b981 | Success messages |
| --error-color | Red | #ef4444 | Error messages, destructive actions |
| --border-color | Light Green | #d1fae5 | Borders, dividers |

### Gradients
| Variable | Value | Purpose |
|----------|-------|---------|
| --accent-gradient | linear-gradient(135deg, #10b981 0%, #059669 100%) | Green gradient for buttons, avatars |
| --orange-gradient | linear-gradient(135deg, #059669 0%, #047857 100%) | Dark green gradient |

### Glows & Effects
| Variable | Value | Purpose |
|----------|-------|---------|
| --accent-glow | 0 4px 14px rgba(16, 185, 129, 0.15) | Shadow around green elements |
| --border-glow | rgba(16, 185, 129, 0.2) | Green tint in border shadows |
| --accent-light | rgba(16, 185, 129, 0.06) | Light green background tint |
| --success-light | rgba(16, 185, 129, 0.08) | Success message background |
| --error-light | rgba(239, 68, 68, 0.08) | Error message background |

### Shadows
| Variable | Value | Purpose |
|----------|-------|---------|
| --shadow-sm | 0 1px 2px 0 rgba(0, 0, 0, 0.05) | Subtle shadows |
| --shadow-md | 0 4px 6px -1px rgba(0, 0, 0, 0.05), 0 2px 4px -2px rgba(0, 0, 0, 0.05) | Medium shadows |
| --shadow-lg | 0 10px 15px -3px rgba(0, 0, 0, 0.05), 0 4px 6px -4px rgba(0, 0, 0, 0.05) | Large shadows |
| --shadow-xl | 0 20px 25px -5px rgba(0, 0, 0, 0.08), 0 8px 10px -6px rgba(0, 0, 0, 0.08) | Extra large shadows |

---

## REACT COLOR SCHEME (v2/frontend/src/index.css)

### Light Mode (Root/Default)
| Variable | HSL Value | RGB Equivalent | Purpose |
|----------|-----------|-----------------|---------|
| --background | 0 0% 100% | #ffffff | Page background |
| --foreground | 222.2 84% 4.9% | #1e293b | Primary text |
| --primary | 222.2 47.4% 11.2% | #1e40af | CTA, accents |
| --primary-foreground | 210 40% 98% | #f8fafc | Text on primary |
| --secondary | 210 40% 96.1% | #f1f5f9 | Secondary backgrounds |
| --secondary-foreground | 222.2 47.4% 11.2% | #1e40af | Text on secondary |
| --muted | 210 40% 96.1% | #f1f5f9 | Disabled states |
| --muted-foreground | 215.4 16.3% 46.9% | #64748b | Secondary text |
| --accent | 210 40% 96.1% | #f1f5f9 | Accent backgrounds |
| --accent-foreground | 222.2 47.4% 11.2% | #1e40af | Accent text |
| --destructive | 0 84.2% 60.2% | #ef4444 | Error/delete |
| --destructive-foreground | 210 40% 98% | #f8fafc | Text on destructive |
| --border | 214.3 31.8% 91.4% | #e2e8f0 | Borders, dividers |
| --input | 214.3 31.8% 91.4% | #e2e8f0 | Input borders |
| --ring | 222.2 84% 4.9% | #1e293b | Focus ring |
| --card | 0 0% 100% | #ffffff | Card backgrounds |
| --card-foreground | 222.2 84% 4.9% | #1e293b | Card text |
| --popover | 0 0% 100% | #ffffff | Popover backgrounds |
| --popover-foreground | 222.2 84% 4.9% | #1e293b | Popover text |

### Dark Mode
| Variable | HSL Value | RGB Equivalent | Purpose |
|----------|-----------|-----------------|---------|
| --background | 222.2 84% 4.9% | #1e293b | Page background (dark) |
| --foreground | 210 40% 98% | #f8fafc | Primary text (light) |
| --primary | 210 40% 98% | #f8fafc | CTA (inverted) |
| --primary-foreground | 222.2 47.4% 11.2% | #1e40af | Text on primary |
| --secondary | 217.2 32.6% 17.5% | #334155 | Secondary backgrounds |
| --secondary-foreground | 210 40% 98% | #f8fafc | Text on secondary |
| --muted | 217.2 32.6% 17.5% | #334155 | Disabled states |
| --muted-foreground | 215 20.2% 65.1% | #94a3b8 | Secondary text |
| --border | 217.2 32.6% 17.5% | #334155 | Borders |
| --input | 217.2 32.6% 17.5% | #334155 | Input borders |
| --ring | 212.7 26.8% 83.9% | #cbd5e1 | Focus ring |
| --card | 222.2 84% 4.9% | #1e293b | Card backgrounds |
| --card-foreground | 210 40% 98% | #f8fafc | Card text |

### Radius
| Variable | Value | Used for |
|----------|-------|----------|
| --radius | 0.5rem (8px) | Base border radius |
| --radius-lg | var(--radius) | Large elements |
| --radius-md | calc(var(--radius) - 2px) | Medium elements |
| --radius-sm | calc(var(--radius) - 4px) | Small elements |

---

## COMPARISON & RECOMMENDATIONS

### Visual Differences
| Aspect | Legacy | React | Recommendation |
|--------|--------|-------|-----------------|
| Primary Color | Bright Green (#10b981) | Dark Navy (#1e40af) | Choose one consistent approach |
| Background | Light green-tint (#f4fbf7) | White (#ffffff) | React is cleaner, modern trend |
| Text | Black/Dark Gray | Slate family (#1e293b) | React's slate is softer on eyes |
| Accent Light | Green (#ecfdf5) | Light Gray (#f1f5f9) | React is more neutral |
| Error Color | Red (#ef4444) | Red (#ef4444) | IDENTICAL - keep as is |
| Borders | Light Green (#d1fae5) | Light Gray (#e2e8f0) | React is more versatile |

### Design System Maturity
| Aspect | Legacy | React |
|--------|--------|-------|
| Total CSS Variables | 29 | 20+ (with dark mode) |
| Color Consistency | Theme-based | Tailwind Design System |
| Accessibility | No A11y tokens | Includes contrast-aware palette |
| Dark Mode Support | Not documented | Full support |
| Scalability | Manual maintenance | Tailwind-maintained |

### Migration Strategy Options

**Option 1: Embrace React's Neutral Scheme**
- Keep current React colors
- Update legacy green to slate/navy
- Faster implementation
- Modern, professional look

**Option 2: Custom Tailwind Theme (Keep Green)**
- Override Tailwind defaults
- Restore green (#10b981) as primary
- Requires theme customization
- Maintains brand continuity

**Option 3: Hybrid Approach**
- Keep React's neutral base
- Use green (#10b981) as accent/highlight
- Best of both worlds
- Moderate implementation effort

### Key CSS Variables to Define
```css
:root {
  /* Core Colors */
  --primary: #10b981;          /* Green - legacy brand */
  --primary-light: #ecfdf5;    /* Light green background */
  --primary-dark: #059669;     /* Dark green active state */
  
  /* Neutral Palette */
  --gray-900: #1e1e1e;         /* Text */
  --gray-700: #3f3f3f;         /* Secondary text */
  --gray-500: #737373;         /* Muted text */
  --gray-100: #f5f5f5;         /* Light backgrounds */
  --gray-50: #fafafa;          /* Very light backgrounds */
  
  /* Status Colors */
  --success: #10b981;          /* Green */
  --error: #ef4444;            /* Red */
  --warning: #f59e0b;          /* Amber */
  --info: #3b82f6;             /* Blue */
}
```

---

## Implementation Guidance

### For New Components
1. Use Tailwind classes as primary styling method
2. Define custom theme in `tailwind.config.js` for brand colors
3. Reserve CSS variables only for dynamic theming
4. Prefer semantic color names (primary, success) over hex values

### For Refactoring
1. Convert legacy CSS variables to Tailwind equivalents
2. Extract brand colors to theme config
3. Test dark mode compatibility
4. Update design tokens document

---

## Current Tailwind Theme Config Recommendation

```javascript
module.exports = {
  theme: {
    extend: {
      colors: {
        primary: {
          DEFAULT: '#10b981',    // Green for brand continuity
          light: '#ecfdf5',
          dark: '#059669',
        },
        // Keep other colors as Tailwind defaults
      }
    }
  }
}
```
