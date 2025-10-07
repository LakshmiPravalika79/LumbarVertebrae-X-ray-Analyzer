import { createTheme, ThemeOptions } from '@mui/material/styles';

// Medical color palette - professional and accessible
export const medicalColors = {
  primary: {
    main: '#1976d2', // Medical blue
    light: '#42a5f5',
    dark: '#1565c0',
    contrastText: '#ffffff',
  },
  secondary: {
    main: '#2e7d32', // Medical green
    light: '#4caf50',
    dark: '#1b5e20',
    contrastText: '#ffffff',
  },
  success: {
    main: '#2e7d32', // Healthy green
    light: '#4caf50',
    dark: '#1b5e20',
  },
  warning: {
    main: '#ed6c02', // Caution orange
    light: '#ff9800',
    dark: '#e65100',
  },
  error: {
    main: '#d32f2f', // Alert red
    light: '#f44336',
    dark: '#c62828',
  },
  info: {
    main: '#0288d1', // Information blue
    light: '#03a9f4',
    dark: '#01579b',
  },
  background: {
    default: '#f8fafc', // Clean medical white
    paper: '#ffffff',
    elevated: '#f1f5f9',
  },
  text: {
    primary: '#1e293b',
    secondary: '#64748b',
    disabled: '#94a3b8',
  },
  divider: '#e2e8f0',
  grey: {
    50: '#f8fafc',
    100: '#f1f5f9',
    200: '#e2e8f0',
    300: '#cbd5e1',
    400: '#94a3b8',
    500: '#64748b',
    600: '#475569',
    700: '#334155',
    800: '#1e293b',
    900: '#0f172a',
  },
};

// Professional medical typography
const medicalTypography = {
  fontFamily: '"Inter", "Roboto", "Helvetica", "Arial", sans-serif',
  h1: {
    fontSize: '2.5rem',
    fontWeight: 700,
    lineHeight: 1.2,
    letterSpacing: '-0.01562em',
  },
  h2: {
    fontSize: '2rem',
    fontWeight: 600,
    lineHeight: 1.3,
    letterSpacing: '-0.00833em',
  },
  h3: {
    fontSize: '1.75rem',
    fontWeight: 600,
    lineHeight: 1.4,
  },
  h4: {
    fontSize: '1.5rem',
    fontWeight: 600,
    lineHeight: 1.4,
  },
  h5: {
    fontSize: '1.25rem',
    fontWeight: 500,
    lineHeight: 1.5,
  },
  h6: {
    fontSize: '1.125rem',
    fontWeight: 500,
    lineHeight: 1.5,
  },
  subtitle1: {
    fontSize: '1rem',
    fontWeight: 500,
    lineHeight: 1.6,
  },
  subtitle2: {
    fontSize: '0.875rem',
    fontWeight: 500,
    lineHeight: 1.6,
  },
  body1: {
    fontSize: '1rem',
    fontWeight: 400,
    lineHeight: 1.6,
  },
  body2: {
    fontSize: '0.875rem',
    fontWeight: 400,
    lineHeight: 1.6,
  },
  caption: {
    fontSize: '0.75rem',
    fontWeight: 400,
    lineHeight: 1.4,
  },
  button: {
    fontSize: '0.875rem',
    fontWeight: 500,
    textTransform: 'none' as const,
  },
  overline: {
    fontSize: '0.75rem',
    fontWeight: 500,
    textTransform: 'uppercase' as const,
    letterSpacing: '0.1em',
  },
};

// Medical component styling
const medicalComponents = {
  MuiCard: {
    styleOverrides: {
      root: {
        boxShadow: '0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px 0 rgba(0, 0, 0, 0.06)',
        borderRadius: '12px',
        border: '1px solid #e2e8f0',
        '&:hover': {
          boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)',
        },
      },
    },
  },
  MuiButton: {
    styleOverrides: {
      root: {
        borderRadius: '8px',
        textTransform: 'none' as const,
        fontWeight: 500,
        padding: '10px 20px',
        boxShadow: 'none',
        '&:hover': {
          boxShadow: '0 2px 4px rgba(0, 0, 0, 0.1)',
        },
      },
      contained: {
        '&:hover': {
          boxShadow: '0 4px 8px rgba(0, 0, 0, 0.15)',
        },
      },
    },
  },
  MuiChip: {
    styleOverrides: {
      root: {
        borderRadius: '6px',
        fontWeight: 500,
      },
    },
  },
  MuiPaper: {
    styleOverrides: {
      root: {
        backgroundImage: 'none',
      },
      elevation1: {
        boxShadow: '0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px 0 rgba(0, 0, 0, 0.06)',
      },
      elevation2: {
        boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)',
      },
    },
  },
  MuiTableHead: {
    styleOverrides: {
      root: {
        backgroundColor: '#f8fafc',
        '& .MuiTableCell-head': {
          fontWeight: 600,
          color: '#374151',
          borderBottom: '2px solid #e5e7eb',
        },
      },
    },
  },
  MuiTableRow: {
    styleOverrides: {
      root: {
        '&:nth-of-type(odd)': {
          backgroundColor: '#fafbfc',
        },
        '&:hover': {
          backgroundColor: '#f1f5f9',
        },
      },
    },
  },
};

// Create the medical theme
export const medicalTheme = createTheme({
  palette: medicalColors,
  typography: medicalTypography,
  components: medicalComponents,
  shape: {
    borderRadius: 8,
  },
  spacing: 8,
} as ThemeOptions);

// Status color mapping for consistent usage
export const statusColors = {
  normal: medicalColors.success.main,
  abnormal: medicalColors.error.main,
  pending: medicalColors.info.main,
  analyzing: medicalColors.warning.main,
  completed: medicalColors.success.main,
  error: medicalColors.error.main,
};

// Medical-specific measurements and constants
export const medicalConstants = {
  normalSpacingRange: {
    min: 4.0,
    max: 8.0,
  },
  normalIntensityThreshold: 0.3,
  maxFileSize: 10 * 1024 * 1024, // 10MB
  maxFiles: 25,
  supportedFormats: ['.jpg', '.jpeg', '.png', '.dicom', '.dcm'],
  vertebraeLabels: ['L3', 'L4', 'L5', 'Sacrum'] as const,
};