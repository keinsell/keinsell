/** @type {import('tailwindcss').Config} */
export default {
  content: ['./src/**/*.{astro,html,js,jsx,md,mdx,svelte,ts,tsx,vue}'],
  darkMode: 'class',
  theme: {
    extend: {
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
        mono: ['JetBrains Mono', 'Menlo', 'Monaco', 'Consolas', 'monospace'],
      },
      colors: {
        border: 'hsl(var(--border))',
        input: 'hsl(var(--input))',
        ring: 'hsl(var(--ring))',
        background: 'hsl(var(--background))',
        foreground: 'hsl(var(--foreground))',
        primary: {
          DEFAULT: 'hsl(var(--primary))',
          foreground: 'hsl(var(--primary-foreground))',
        },
        secondary: {
          DEFAULT: 'hsl(var(--secondary))',
          foreground: 'hsl(var(--secondary-foreground))',
        },
        muted: {
          DEFAULT: 'hsl(var(--muted))',
          foreground: 'hsl(var(--muted-foreground))',
        },
        accent: {
          DEFAULT: 'hsl(var(--accent))',
          foreground: 'hsl(var(--accent-foreground))',
        },
        card: {
          DEFAULT: 'hsl(var(--card))',
          foreground: 'hsl(var(--card-foreground))',
        },
      },
      borderRadius: {
        lg: 'var(--radius)',
        md: 'calc(var(--radius) - 2px)',
        sm: 'calc(var(--radius) - 4px)',
      },
      typography: ({ theme }) => ({
        DEFAULT: {
          css: {
            '--tw-prose-body': theme('colors.foreground'),
            '--tw-prose-headings': theme('colors.foreground'),
            '--tw-prose-lead': theme('colors.muted.foreground'),
            '--tw-prose-links': theme('colors.primary.DEFAULT'),
            '--tw-prose-bold': theme('colors.foreground'),
            '--tw-prose-counters': theme('colors.muted.foreground'),
            '--tw-prose-bullets': theme('colors.muted.foreground'),
            '--tw-prose-hr': theme('colors.border'),
            '--tw-prose-quotes': theme('colors.muted.foreground'),
            '--tw-prose-quote-borders': theme('colors.border'),
            '--tw-prose-captions': theme('colors.muted.foreground'),
            '--tw-prose-code': theme('colors.foreground'),
            '--tw-prose-pre-code': theme('colors.foreground'),
            '--tw-prose-pre-bg': theme('colors.muted.DEFAULT'),
            '--tw-prose-th-borders': theme('colors.border'),
            '--tw-prose-td-borders': theme('colors.border'),
            '--tw-prose-invert-body': theme('colors.foreground'),
            '--tw-prose-invert-headings': theme('colors.foreground'),
            '--tw-prose-invert-lead': theme('colors.muted.foreground'),
            '--tw-prose-invert-links': theme('colors.primary.DEFAULT'),
            '--tw-prose-invert-bold': theme('colors.foreground'),
            '--tw-prose-invert-counters': theme('colors.muted.foreground'),
            '--tw-prose-invert-bullets': theme('colors.muted.foreground'),
            '--tw-prose-invert-hr': theme('colors.border'),
            '--tw-prose-invert-quotes': theme('colors.muted.foreground'),
            '--tw-prose-invert-quote-borders': theme('colors.border'),
            '--tw-prose-invert-captions': theme('colors.muted.foreground'),
            '--tw-prose-invert-code': theme('colors.foreground'),
            '--tw-prose-invert-pre-code': theme('colors.foreground'),
            '--tw-prose-invert-pre-bg': theme('colors.muted.DEFAULT'),
            '--tw-prose-invert-th-borders': theme('colors.border'),
            '--tw-prose-invert-td-borders': theme('colors.border'),
            
            // Base typography adjustments
            color: 'hsl(var(--foreground))',
            fontSize: '0.875rem', // 14px
            lineHeight: '1.7',
            maxWidth: '65ch',
            
            // Paragraph styles
            p: {
              marginTop: '1.25em',
              marginBottom: '1.25em',
              color: 'hsl(var(--muted-foreground))',
            },
            
            // Link styles
            a: {
              color: 'hsl(var(--primary))',
              textDecoration: 'underline',
              textDecorationColor: 'hsl(var(--primary) / 0.3)',
              textUnderlineOffset: '0.25rem',
              transition: 'text-decoration-color 150ms',
              '&:hover': {
                textDecorationColor: 'hsl(var(--primary))',
              },
            },
            
            // Heading styles
            h1: {
              fontSize: '1.5rem',
              fontWeight: '600',
              marginTop: '0',
              marginBottom: '0.875em',
              lineHeight: '1.3',
            },
            h2: {
              fontSize: '1.25rem',
              fontWeight: '600',
              marginTop: '1.75em',
              marginBottom: '0.75em',
              lineHeight: '1.4',
            },
            h3: {
              fontSize: '1.125rem',
              fontWeight: '600',
              marginTop: '1.5em',
              marginBottom: '0.5em',
              lineHeight: '1.5',
            },
            h4: {
              fontSize: '1rem',
              fontWeight: '600',
              marginTop: '1.5em',
              marginBottom: '0.5em',
              lineHeight: '1.5',
            },
            
            // Code styles
            code: {
              backgroundColor: 'hsl(var(--muted))',
              padding: '0.125rem 0.375rem',
              borderRadius: '0.25rem',
              fontSize: '0.8125rem',
              fontWeight: '400',
              fontFamily: theme('fontFamily.mono').join(', '),
            },
            'code::before': {
              content: '""',
            },
            'code::after': {
              content: '""',
            },
            
            // Pre styles
            pre: {
              backgroundColor: 'hsl(var(--muted))',
              padding: '1rem',
              borderRadius: '0.5rem',
              fontSize: '0.8125rem',
              lineHeight: '1.6',
              overflowX: 'auto',
            },
            'pre code': {
              backgroundColor: 'transparent',
              padding: '0',
              borderRadius: '0',
              fontSize: 'inherit',
            },
            
            // Blockquote styles
            blockquote: {
              borderLeftWidth: '4px',
              borderLeftColor: 'hsl(var(--border))',
              paddingLeft: '1.5rem',
              fontStyle: 'italic',
              color: 'hsl(var(--muted-foreground))',
              marginTop: '1.5em',
              marginBottom: '1.5em',
            },
            
            // List styles
            ul: {
              marginTop: '1.25em',
              marginBottom: '1.25em',
              paddingLeft: '1.5rem',
            },
            ol: {
              marginTop: '1.25em',
              marginBottom: '1.25em',
              paddingLeft: '1.5rem',
            },
            li: {
              marginTop: '0.5em',
              marginBottom: '0.5em',
            },
            'ul > li::marker': {
              color: 'hsl(var(--muted-foreground))',
            },
            'ol > li::marker': {
              color: 'hsl(var(--muted-foreground))',
            },
            
            // HR styles
            hr: {
              borderColor: 'hsl(var(--border))',
              marginTop: '3em',
              marginBottom: '3em',
            },
            
            // Image styles
            img: {
              marginTop: '2em',
              marginBottom: '2em',
              borderRadius: '0.5rem',
            },
            
            // Table styles
            table: {
              fontSize: '0.875rem',
              lineHeight: '1.5',
            },
            thead: {
              borderBottomColor: 'hsl(var(--border))',
            },
            'thead th': {
              paddingTop: '0.75rem',
              paddingBottom: '0.75rem',
              fontWeight: '600',
            },
            'tbody td': {
              paddingTop: '0.75rem',
              paddingBottom: '0.75rem',
            },
            'tbody tr': {
              borderBottomColor: 'hsl(var(--border))',
            },
          },
        },
        sm: {
          css: {
            fontSize: '0.8125rem',
            h1: {
              fontSize: '1.375rem',
            },
            h2: {
              fontSize: '1.125rem',
            },
            h3: {
              fontSize: '1rem',
            },
            h4: {
              fontSize: '0.9375rem',
            },
          },
        },
      }),
    },
  },
  plugins: [require('@tailwindcss/typography')],
};