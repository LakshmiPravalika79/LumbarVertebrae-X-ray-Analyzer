import React, { useState } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Grid,
  Paper,
  Chip,
  IconButton,
  Divider,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  LinearProgress,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  Button,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Tooltip,
  Avatar,
} from '@mui/material';
import {
  ExpandMore as ExpandMoreIcon,
  ZoomIn as ZoomInIcon,
  Download as DownloadIcon,
  Print as PrintIcon,
  Share as ShareIcon,
  ArrowBack as BackIcon,
  CheckCircle as NormalIcon,
  Warning as WarningIcon,
  Error as AbnormalIcon,
  Rule as MeasurementIcon,
  Visibility as VisibilityIcon,
  Analytics as AnalyticsIcon,
} from '@mui/icons-material';
import { DetailedViewData } from '../types';

interface DetailedResultsProps {
  data: DetailedViewData;
  onBack: () => void;
  onDownloadReport: () => void;
  onPrintReport: () => void;
}

const DetailedResults: React.FC<DetailedResultsProps> = ({
  data,
  onBack,
  onDownloadReport,
  onPrintReport,
}) => {
  const [imageZoomOpen, setImageZoomOpen] = useState(false);
  const [expandedSections, setExpandedSections] = useState<{ [key: string]: boolean }>({
    overview: true,
    vertebrae: false,
    spacing: false,
    abnormalities: false,
    technical: false,
  });

  const handleSectionToggle = (section: string) => {
    setExpandedSections(prev => ({
      ...prev,
      [section]: !prev[section]
    }));
  };

  const getStatusColor = (status: 'normal' | 'abnormal') => {
    return status === 'normal' ? 'success' : 'error';
  };

  const getStatusIcon = (status: 'normal' | 'abnormal') => {
    return status === 'normal' 
      ? <NormalIcon color="success" />
      : <AbnormalIcon color="error" />;
  };

  const getConfidenceColor = (confidence: number) => {
    if (confidence >= 0.8) return 'success';
    if (confidence >= 0.6) return 'warning';
    return 'error';
  };

  const renderSpacingAnalysis = (spacing: typeof data.spacingAnalysis) => (
    <Grid container spacing={3}>
      <Grid item xs={12} md={4}>
        <Paper elevation={1} sx={{ p: 3, textAlign: 'center' }}>
          <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'center', mb: 2 }}>
            <MeasurementIcon sx={{ mr: 1, color: 'primary.main' }} />
            <Typography variant="h6">L3-L4 Spacing</Typography>
          </Box>
          <Typography variant="h4" sx={{ fontWeight: 600, mb: 1 }}>
            {spacing.l3l4.value.toFixed(1)} mm
          </Typography>
          <Chip
            label={spacing.l3l4.status.toUpperCase()}
            color={getStatusColor(spacing.l3l4.status)}
            size="small"
          />
          <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
            Normal range: 4.0-8.0 mm
          </Typography>
          <LinearProgress
            variant="determinate"
            value={Math.min((spacing.l3l4.value / 8.0) * 100, 100)}
            color={getStatusColor(spacing.l3l4.status)}
            sx={{ mt: 2 }}
          />
        </Paper>
      </Grid>
      <Grid item xs={12} md={4}>
        <Paper elevation={1} sx={{ p: 3, textAlign: 'center' }}>
          <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'center', mb: 2 }}>
            <MeasurementIcon sx={{ mr: 1, color: 'primary.main' }} />
            <Typography variant="h6">L4-L5 Spacing</Typography>
          </Box>
          <Typography variant="h4" sx={{ fontWeight: 600, mb: 1 }}>
            {spacing.l4l5.value.toFixed(1)} mm
          </Typography>
          <Chip
            label={spacing.l4l5.status.toUpperCase()}
            color={getStatusColor(spacing.l4l5.status)}
            size="small"
          />
          <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
            Normal range: 4.0-8.0 mm
          </Typography>
          <LinearProgress
            variant="determinate"
            value={Math.min((spacing.l4l5.value / 8.0) * 100, 100)}
            color={getStatusColor(spacing.l4l5.status)}
            sx={{ mt: 2 }}
          />
        </Paper>
      </Grid>
      <Grid item xs={12} md={4}>
        <Paper elevation={1} sx={{ p: 3, textAlign: 'center' }}>
          <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'center', mb: 2 }}>
            <MeasurementIcon sx={{ mr: 1, color: 'primary.main' }} />
            <Typography variant="h6">L5-Sacrum Spacing</Typography>
          </Box>
          <Typography variant="h4" sx={{ fontWeight: 600, mb: 1 }}>
            {spacing.l5Sacrum.value.toFixed(1)} mm
          </Typography>
          <Chip
            label={spacing.l5Sacrum.status.toUpperCase()}
            color={getStatusColor(spacing.l5Sacrum.status)}
            size="small"
          />
          <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
            Normal range: 4.0-8.0 mm
          </Typography>
          <LinearProgress
            variant="determinate"
            value={Math.min((spacing.l5Sacrum.value / 8.0) * 100, 100)}
            color={getStatusColor(spacing.l5Sacrum.status)}
            sx={{ mt: 2 }}
          />
        </Paper>
      </Grid>
    </Grid>
  );

  return (
    <Box>
      {/* Header */}
      <Card elevation={2} sx={{ mb: 3 }}>
        <CardContent>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
              <IconButton onClick={onBack} color="primary">
                <BackIcon />
              </IconButton>
              <Box>
                <Typography variant="h4" component="h1" sx={{ fontWeight: 600 }}>
                  Detailed Analysis Report
                </Typography>
                <Typography variant="subtitle1" color="text.secondary">
                  {data.imageName} • {new Date(data.analysisTime).toLocaleString()}
                </Typography>
              </Box>
            </Box>
            <Box sx={{ display: 'flex', gap: 1 }}>
              <Button
                variant="outlined"
                startIcon={<PrintIcon />}
                onClick={onPrintReport}
                size="small"
              >
                Print
              </Button>
              <Button
                variant="outlined"
                startIcon={<ShareIcon />}
                size="small"
              >
                Share
              </Button>
              <Button
                variant="contained"
                startIcon={<DownloadIcon />}
                onClick={onDownloadReport}
                size="small"
              >
                Download
              </Button>
            </Box>
          </Box>
        </CardContent>
      </Card>

      <Grid container spacing={3}>
        {/* Left Column - Image and Basic Info */}
        <Grid item xs={12} lg={6}>
          {/* X-ray Image */}
          <Card elevation={2} sx={{ mb: 3 }}>
            <CardContent>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
                <Typography variant="h6">X-ray Image</Typography>
                <Tooltip title="Zoom Image">
                  <IconButton onClick={() => setImageZoomOpen(true)}>
                    <ZoomInIcon />
                  </IconButton>
                </Tooltip>
              </Box>
              <Box
                sx={{
                  position: 'relative',
                  width: '100%',
                  height: 400,
                  bgcolor: 'grey.100',
                  borderRadius: 1,
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  cursor: 'pointer',
                }}
                onClick={() => setImageZoomOpen(true)}
              >
                <img
                  src={data.imageUrl}
                  alt={data.imageName}
                  style={{
                    maxWidth: '100%',
                    maxHeight: '100%',
                    objectFit: 'contain',
                  }}
                />
              </Box>
            </CardContent>
          </Card>

          {/* Overall Status */}
          <Card elevation={2}>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Overall Assessment
              </Typography>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 2 }}>
                {getStatusIcon(data.overallStatus)}
                <Chip
                  label={data.overallStatus.toUpperCase()}
                  color={getStatusColor(data.overallStatus)}
                  size="medium"
                  sx={{ fontWeight: 600 }}
                />
                <Typography variant="body1">
                  Confidence: {Math.round(data.confidence * 100)}%
                </Typography>
              </Box>
              <LinearProgress
                variant="determinate"
                value={data.confidence * 100}
                color={getConfidenceColor(data.confidence)}
                sx={{ height: 8, borderRadius: 4 }}
              />
            </CardContent>
          </Card>
        </Grid>

        {/* Right Column - Detailed Analysis */}
        <Grid item xs={12} lg={6}>
          {/* Vertebrae Analysis */}
          <Accordion
            expanded={expandedSections.vertebrae}
            onChange={() => handleSectionToggle('vertebrae')}
            elevation={2}
            sx={{ mb: 2 }}
          >
            <AccordionSummary expandIcon={<ExpandMoreIcon />}>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                <VisibilityIcon color="primary" />
                <Typography variant="h6">Vertebrae Analysis</Typography>
              </Box>
            </AccordionSummary>
            <AccordionDetails>
              <Grid container spacing={2}>
                {Object.entries(data.vertebraeAnalysis).map(([vertebra, analysis]) => (
                  <Grid item xs={6} key={vertebra}>
                    <Paper elevation={1} sx={{ p: 2 }}>
                      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 1 }}>
                        <Typography variant="subtitle1" sx={{ fontWeight: 600 }}>
                          {vertebra.toUpperCase()}
                        </Typography>
                        {getStatusIcon(analysis.status)}
                      </Box>
                      <Typography variant="body2" color="text.secondary" gutterBottom>
                        Integrity: {Math.round(analysis.integrity * 100)}%
                      </Typography>
                      <LinearProgress
                        variant="determinate"
                        value={analysis.integrity * 100}
                        color={getStatusColor(analysis.status)}

                      />
                      {analysis.findings.length > 0 && (
                        <Box sx={{ mt: 1 }}>
                          <Typography variant="caption" color="text.secondary">
                            Findings:
                          </Typography>
                          {analysis.findings.map((finding, index) => (
                            <Typography key={index} variant="caption" display="block">
                              • {finding}
                            </Typography>
                          ))}
                        </Box>
                      )}
                    </Paper>
                  </Grid>
                ))}
              </Grid>
            </AccordionDetails>
          </Accordion>

          {/* Spacing Analysis */}
          <Accordion
            expanded={expandedSections.spacing}
            onChange={() => handleSectionToggle('spacing')}
            elevation={2}
            sx={{ mb: 2 }}
          >
            <AccordionSummary expandIcon={<ExpandMoreIcon />}>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                <MeasurementIcon color="primary" />
                <Typography variant="h6">Spacing Measurements</Typography>
              </Box>
            </AccordionSummary>
            <AccordionDetails>
              {renderSpacingAnalysis(data.spacingAnalysis)}
            </AccordionDetails>
          </Accordion>

          {/* Abnormalities */}
          <Accordion
            expanded={expandedSections.abnormalities}
            onChange={() => handleSectionToggle('abnormalities')}
            elevation={2}
            sx={{ mb: 2 }}
          >
            <AccordionSummary expandIcon={<ExpandMoreIcon />}>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                <WarningIcon color="warning" />
                <Typography variant="h6">
                  Abnormalities ({data.abnormalities.length})
                </Typography>
              </Box>
            </AccordionSummary>
            <AccordionDetails>
              {data.abnormalities.length > 0 ? (
                <List>
                  {data.abnormalities.map((abnormality, index) => (
                    <ListItem key={index} divider={index < data.abnormalities.length - 1}>
                      <ListItemIcon>
                        <Avatar sx={{ bgcolor: 'error.light', width: 32, height: 32 }}>
                          {index + 1}
                        </Avatar>
                      </ListItemIcon>
                      <ListItemText
                        primary={abnormality.type}
                        secondary={
                          <Box>
                            <Typography variant="body2" color="text.secondary">
                              Location: {abnormality.location}
                            </Typography>
                            <Typography variant="body2" color="text.secondary">
                              Severity: {abnormality.severity} • Confidence: {Math.round(abnormality.confidence * 100)}%
                            </Typography>
                            <Typography variant="body2">
                              {abnormality.description}
                            </Typography>
                          </Box>
                        }
                      />
                    </ListItem>
                  ))}
                </List>
              ) : (
                <Box sx={{ textAlign: 'center', py: 3 }}>
                  <NormalIcon color="success" sx={{ fontSize: 48, mb: 2 }} />
                  <Typography variant="h6" color="success.main">
                    No abnormalities detected
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    All vertebrae appear normal
                  </Typography>
                </Box>
              )}
            </AccordionDetails>
          </Accordion>

          {/* Technical Details */}
          <Accordion
            expanded={expandedSections.technical}
            onChange={() => handleSectionToggle('technical')}
            elevation={2}
          >
            <AccordionSummary expandIcon={<ExpandMoreIcon />}>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                <AnalyticsIcon color="primary" />
                <Typography variant="h6">Technical Details</Typography>
              </Box>
            </AccordionSummary>
            <AccordionDetails>
              <Grid container spacing={2}>
                <Grid item xs={6}>
                  <Typography variant="subtitle2" color="text.secondary">
                    Analysis Method
                  </Typography>
                  <Typography variant="body2">
                    {data.technicalDetails.analysisMethod}
                  </Typography>
                </Grid>
                <Grid item xs={6}>
                  <Typography variant="subtitle2" color="text.secondary">
                    Processing Time
                  </Typography>
                  <Typography variant="body2">
                    {data.technicalDetails.processingTime}ms
                  </Typography>
                </Grid>
                <Grid item xs={6}>
                  <Typography variant="subtitle2" color="text.secondary">
                    Image Quality
                  </Typography>
                  <Typography variant="body2">
                    {data.technicalDetails.imageQuality}
                  </Typography>
                </Grid>
                <Grid item xs={6}>
                  <Typography variant="subtitle2" color="text.secondary">
                    Algorithm Version
                  </Typography>
                  <Typography variant="body2">
                    {data.technicalDetails.algorithmVersion}
                  </Typography>
                </Grid>
              </Grid>
            </AccordionDetails>
          </Accordion>
        </Grid>
      </Grid>

      {/* Zoom Dialog */}
      <Dialog
        open={imageZoomOpen}
        onClose={() => setImageZoomOpen(false)}
        maxWidth="lg"
        fullWidth
      >
        <DialogTitle>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <Typography variant="h6">{data.imageName}</Typography>
            <IconButton onClick={() => setImageZoomOpen(false)}>
              <BackIcon />
            </IconButton>
          </Box>
        </DialogTitle>
        <DialogContent>
          <Box
            sx={{
              display: 'flex',
              justifyContent: 'center',
              alignItems: 'center',
              minHeight: 400,
            }}
          >
            <img
              src={data.imageUrl}
              alt={data.imageName}
              style={{
                maxWidth: '100%',
                maxHeight: '70vh',
                objectFit: 'contain',
              }}
            />
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setImageZoomOpen(false)}>Close</Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default DetailedResults;