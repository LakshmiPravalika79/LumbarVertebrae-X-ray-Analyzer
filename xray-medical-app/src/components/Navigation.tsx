import React from 'react';
import {
  AppBar,
  Toolbar,
  Typography,
  IconButton,
  Box,
  Breadcrumbs,
  Link,
  Chip,
} from '@mui/material';
import {
  ArrowBack as BackIcon,
  Home as HomeIcon,
  TableChart as TableIcon,
  Visibility as DetailIcon,
  LocalHospital as MedicalIcon,
} from '@mui/icons-material';

interface NavigationProps {
  currentView: 'upload' | 'table' | 'detailed';
  onBackToUpload: () => void;
  onBackToTable: () => void;
  hasResults: boolean;
}

const Navigation: React.FC<NavigationProps> = ({
  currentView,
  onBackToUpload,
  onBackToTable,
  hasResults,
}) => {
  const getBreadcrumbs = () => {
    const breadcrumbs = [
      <Link
        key="upload"
        color="inherit"
        href="#"
        onClick={(e) => {
          e.preventDefault();
          onBackToUpload();
        }}
        sx={{
          display: 'flex',
          alignItems: 'center',
          textDecoration: 'none',
          '&:hover': { textDecoration: 'underline' }
        }}
      >
        <HomeIcon sx={{ mr: 0.5, fontSize: 20 }} />
        Upload X-rays
      </Link>
    ];

    if (hasResults) {
      breadcrumbs.push(
        <Link
          key="results"
          color={currentView === 'table' ? 'primary' : 'inherit'}
          href="#"
          onClick={(e) => {
            e.preventDefault();
            if (currentView !== 'table') onBackToTable();
          }}
          sx={{
            display: 'flex',
            alignItems: 'center',
            textDecoration: 'none',
            '&:hover': { textDecoration: 'underline' }
          }}
        >
          <TableIcon sx={{ mr: 0.5, fontSize: 20 }} />
          Results Table
        </Link>
      );
    }

    if (currentView === 'detailed') {
      breadcrumbs.push(
        <Typography
          key="detailed"
          color="primary"
          sx={{
            display: 'flex',
            alignItems: 'center',
          }}
        >
          <DetailIcon sx={{ mr: 0.5, fontSize: 20 }} />
          Detailed View
        </Typography>
      );
    }

    return breadcrumbs;
  };

  const getViewTitle = () => {
    switch (currentView) {
      case 'upload':
        return 'Upload X-ray Images';
      case 'table':
        return 'Analysis Results';
      case 'detailed':
        return 'Detailed Analysis';
      default:
        return 'Lumbar Spine X-ray Analyzer';
    }
  };

  const getViewDescription = () => {
    switch (currentView) {
      case 'upload':
        return 'Upload up to 25 lumbar spine X-ray images for automated analysis';
      case 'table':
        return 'Review analysis results for all uploaded X-ray images';
      case 'detailed':
        return 'Comprehensive analysis report with detailed findings';
      default:
        return '';
    }
  };

  return (
    <AppBar 
      position="static" 
      elevation={2}
      sx={{ 
        bgcolor: 'primary.main',
        borderBottom: '1px solid',
        borderColor: 'divider'
      }}
    >
      <Toolbar sx={{ minHeight: { xs: 56, sm: 64 } }}>
        <Box sx={{ display: 'flex', alignItems: 'center', mr: 3 }}>
          <MedicalIcon sx={{ fontSize: 32, mr: 1 }} />
          <Typography
            variant="h6"
            component="div"
            sx={{ 
              fontWeight: 600,
              fontSize: { xs: '1.1rem', sm: '1.25rem' }
            }}
          >
            MediScan Pro
          </Typography>
          <Chip
            label="Medical Grade"
            size="small"
            sx={{
              ml: 2,
              bgcolor: 'success.light',
              color: 'success.contrastText',
              fontWeight: 500,
              fontSize: '0.75rem'
            }}
          />
        </Box>

        <Box sx={{ flexGrow: 1 }} />

        {(currentView !== 'upload' || hasResults) && (
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            {currentView === 'detailed' && (
              <IconButton
                color="inherit"
                onClick={onBackToTable}
                sx={{ mr: 1 }}
                title="Back to Results Table"
              >
                <BackIcon />
              </IconButton>
            )}
            {currentView === 'table' && (
              <IconButton
                color="inherit"
                onClick={onBackToUpload}
                sx={{ mr: 1 }}
                title="Back to Upload"
              >
                <BackIcon />
              </IconButton>
            )}
          </Box>
        )}
      </Toolbar>

      {/* Secondary Header with Breadcrumbs and View Info */}
      <Box
        sx={{
          bgcolor: 'background.paper',
          borderTop: '1px solid',
          borderColor: 'divider',
          px: 3,
          py: 2,
        }}
      >
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 1 }}>
          <Box>
            <Breadcrumbs
              aria-label="navigation"
              sx={{ mb: 1 }}
              separator="›"
            >
              {getBreadcrumbs()}
            </Breadcrumbs>
            <Typography
              variant="h4"
              component="h1"
              sx={{
                fontWeight: 600,
                color: 'text.primary',
                mb: 0.5,
                fontSize: { xs: '1.5rem', sm: '2rem', md: '2.125rem' }
              }}
            >
              {getViewTitle()}
            </Typography>
            <Typography
              variant="body1"
              color="text.secondary"
              sx={{ fontSize: { xs: '0.875rem', sm: '1rem' } }}
            >
              {getViewDescription()}
            </Typography>
          </Box>

          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <Chip
              icon={<MedicalIcon />}
              label="AI-Powered"
              color="primary"
              variant="outlined"
              size="small"
            />
            <Chip
              label="HIPAA Compliant"
              color="success"
              variant="outlined"
              size="small"
            />
          </Box>
        </Box>
      </Box>
    </AppBar>
  );
};

export default Navigation;