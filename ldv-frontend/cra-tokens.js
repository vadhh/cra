// CRA Design System v1.0 — Shared Tailwind Config
// Source of truth: uiux/Sydeco_CRA_Design_System_v1.0.md (Appendix A)
// ponytail: CDN-only config; upgrade to build-step Tailwind when needed
tailwind.config = {
  theme: {
    extend: {
      colors: {
        // Core brand (Section 04)
        'navy':       '#14213D',
        'cra-blue':   { 50: '#EFF4FF', 600: '#2F6BFF', 700: '#2355D8' },
        'cra-teal':   '#0E9384',
        // Ink / text
        'ink':        '#101828',
        'ink-secondary': '#475467',
        'ink-muted':  '#667085',
        // Surfaces & borders
        'canvas':     '#F9FAFB',
        'surface':    '#FFFFFF',
        'border-ui':  '#EAECF0',
        'border-ctrl':'#D0D5DD',
        // Risk severity (Section 04)
        'risk-critical':    '#7A271A',
        'risk-critical-bg': '#FEF3F2',
        'risk-high':        '#D92D20',
        'risk-high-fg':     '#B42318',
        'risk-high-bg':     '#FEF3F2',
        'risk-medium':      '#DC6803',
        'risk-medium-fg':   '#B54708',
        'risk-medium-bg':   '#FFFAEB',
        'risk-low':         '#039855',
        'risk-low-fg':      '#027A48',
        'risk-low-bg':      '#ECFDF3',
        // Semantic status
        'st-info':     '#1570EF',
        'st-info-bg':  '#EFF8FF',
        'st-verified': '#0E9384',
        'st-draft':    '#6941C6',
        'st-neutral':  '#667085',
      },
      fontFamily: {
        sans:  ['Inter', 'Arial', 'Liberation Sans', 'sans-serif'],
        serif: ['Source Serif 4', 'Georgia', 'Liberation Serif', 'serif'],
        mono:  ['JetBrains Mono', 'DejaVu Sans Mono', 'monospace'],
      },
      fontSize: {
        'display-lg': ['48px', { lineHeight: '56px', fontWeight: '700' }],
        'h1':         ['36px', { lineHeight: '44px', fontWeight: '700' }],
        'h2':         ['30px', { lineHeight: '38px', fontWeight: '700' }],
        'h3':         ['24px', { lineHeight: '32px', fontWeight: '600' }],
        'h4':         ['20px', { lineHeight: '28px', fontWeight: '600' }],
        'body-lg':    ['18px', { lineHeight: '28px', fontWeight: '400' }],
        'body-md':    ['16px', { lineHeight: '24px', fontWeight: '400' }],
        'body-sm':    ['14px', { lineHeight: '20px', fontWeight: '400' }],
        'cap':        ['12px', { lineHeight: '18px', fontWeight: '500' }],
      },
      borderRadius: {
        sm:   '4px',
        DEFAULT: '8px',
        lg:   '12px',
        xl:   '16px',
        pill: '999px',
      },
      maxWidth: {
        content: '1280px',
      },
      width: {
        nav: '248px',
      },
      boxShadow: {
        '1': '0 1px 2px rgba(16,24,40,0.06)',
        '2': '0 4px 12px rgba(16,24,40,0.10)',
        '3': '0 16px 32px rgba(16,24,40,0.14)',
      },
    },
  },
};
