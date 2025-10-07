import React, { useState, useCallback } from 'react';
import { ThemeProvider, CssBaseline, Box } from '@mui/material';
import { medicalTheme } from './theme/medicalTheme';
import Navigation from './components/Navigation';
import MultiUpload from './components/MultiUpload';
import ResultsTable from './components/ResultsTable';
import DetailedResults from './components/DetailedResults';
import { UploadedFile, XRayImage, TableViewData, DetailedViewData } from './types';

type ViewMode = 'upload' | 'table' | 'detailed';

const App: React.FC = () => {
  const [currentView, setCurrentView] = useState<ViewMode>('upload');
  const [uploadedFiles, setUploadedFiles] = useState<XRayImage[]>([]);
  const [tableData, setTableData] = useState<TableViewData[]>([]);
  const [selectedDetailData, setSelectedDetailData] = useState<DetailedViewData | null>(null);

  const handleFilesUploaded = useCallback((files: XRayImage[]) => {
    setUploadedFiles(files);
    
    // Simulate analysis results for demonstration
    const analysisResults: TableViewData[] = files.map((file, index) => ({
      id: `analysis-${index}`,
      imageName: file.name,
      uploadTime: file.uploadedAt.toLocaleString(),
      overallStatus: Math.random() > 0.3 ? 'normal' : 'abnormal',
      l3Status: Math.random() > 0.2 ? 'normal' : 'abnormal',
      l4Status: Math.random() > 0.2 ? 'normal' : 'abnormal',
      l5Status: Math.random() > 0.2 ? 'normal' : 'abnormal',
      sacrumStatus: Math.random() > 0.2 ? 'normal' : 'abnormal',
      l3l4Spacing: 4.0 + Math.random() * 4.0, // 4-8mm range
      l4l5Spacing: 4.0 + Math.random() * 4.0,
      l5SacrumSpacing: 4.0 + Math.random() * 4.0,
      confidence: 0.6 + Math.random() * 0.4, // 60-100%
      abnormalities: Math.random() > 0.5 
        ? [] 
        : ['Disc space narrowing', 'Mild compression'].slice(0, Math.floor(Math.random() * 2) + 1),
    }));

    setTableData(analysisResults);
    setCurrentView('table');
  }, []);

  const handleViewDetails = useCallback((id: string) => {
    const tableItem = tableData.find(item => item.id === id);
    const uploadedFile = uploadedFiles.find(file => file.name === tableItem?.imageName);
    
    if (tableItem && uploadedFile) {
      // Create detailed view data
      const detailedData: DetailedViewData = {
        id: tableItem.id,
        imageName: tableItem.imageName,
        imageUrl: uploadedFile.preview || '',
        analysisTime: tableItem.uploadTime,
        overallStatus: tableItem.overallStatus,
        confidence: tableItem.confidence,
        vertebraeAnalysis: {
          l3: {
            status: tableItem.l3Status,
            integrity: 0.8 + Math.random() * 0.2,
            findings: tableItem.l3Status === 'abnormal' ? ['Mild degeneration'] : [],
          },
          l4: {
            status: tableItem.l4Status,
            integrity: 0.8 + Math.random() * 0.2,
            findings: tableItem.l4Status === 'abnormal' ? ['Disc space narrowing'] : [],
          },
          l5: {
            status: tableItem.l5Status,
            integrity: 0.8 + Math.random() * 0.2,
            findings: tableItem.l5Status === 'abnormal' ? ['Compression'] : [],
          },
          sacrum: {
            status: tableItem.sacrumStatus,
            integrity: 0.8 + Math.random() * 0.2,
            findings: tableItem.sacrumStatus === 'abnormal' ? ['Irregularities'] : [],
          },
        },
        spacingAnalysis: {
          l3l4: {
            value: tableItem.l3l4Spacing,
            status: tableItem.l3l4Spacing >= 4.0 && tableItem.l3l4Spacing <= 8.0 ? 'normal' : 'abnormal',
          },
          l4l5: {
            value: tableItem.l4l5Spacing,
            status: tableItem.l4l5Spacing >= 4.0 && tableItem.l4l5Spacing <= 8.0 ? 'normal' : 'abnormal',
          },
          l5Sacrum: {
            value: tableItem.l5SacrumSpacing,
            status: tableItem.l5SacrumSpacing >= 4.0 && tableItem.l5SacrumSpacing <= 8.0 ? 'normal' : 'abnormal',
          },
        },
        abnormalities: tableItem.abnormalities.map((abnormality, index) => ({
          type: abnormality,
          location: ['L3', 'L4', 'L5', 'Sacrum'][Math.floor(Math.random() * 4)],
          severity: ['Mild', 'Moderate', 'Severe'][Math.floor(Math.random() * 3)],
          confidence: 0.7 + Math.random() * 0.3,
          description: `${abnormality} detected with automated analysis`,
        })),
        technicalDetails: {
          analysisMethod: 'AI-Enhanced Image Processing',
          processingTime: 1500 + Math.floor(Math.random() * 1000),
          imageQuality: 'High',
          algorithmVersion: 'v2.1.0',
        },
      };

      setSelectedDetailData(detailedData);
      setCurrentView('detailed');
    }
  }, [tableData, uploadedFiles]);

  const handleBackToTable = useCallback(() => {
    setCurrentView('table');
    setSelectedDetailData(null);
  }, []);

  const handleBackToUpload = useCallback(() => {
    setCurrentView('upload');
    setTableData([]);
    setUploadedFiles([]);
    setSelectedDetailData(null);
  }, []);

  const handleExportData = useCallback(() => {
    const csvContent = [
      ['Image Name', 'Upload Time', 'Overall Status', 'L3', 'L4', 'L5', 'Sacrum', 'L3-L4 Spacing', 'L4-L5 Spacing', 'L5-Sacrum Spacing', 'Confidence', 'Abnormalities'].join(','),
      ...tableData.map(row => [
        row.imageName,
        new Date(row.uploadTime).toISOString(),
        row.overallStatus,
        row.l3Status,
        row.l4Status,
        row.l5Status,
        row.sacrumStatus,
        row.l3l4Spacing.toFixed(1),
        row.l4l5Spacing.toFixed(1),
        row.l5SacrumSpacing.toFixed(1),
        (row.confidence * 100).toFixed(1),
        row.abnormalities.join('; ')
      ].join(','))
    ].join('\n');

    const blob = new Blob([csvContent], { type: 'text/csv' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `xray-analysis-results-${new Date().toISOString().split('T')[0]}.csv`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
  }, [tableData]);

  const handleDownloadReport = useCallback(() => {
    if (selectedDetailData) {
      // In a real app, this would generate a PDF report
      console.log('Downloading report for:', selectedDetailData.imageName);
      alert('Report download functionality would be implemented here');
    }
  }, [selectedDetailData]);

  const handlePrintReport = useCallback(() => {
    if (selectedDetailData) {
      window.print();
    }
  }, [selectedDetailData]);

  return (
    <ThemeProvider theme={medicalTheme}>
      <CssBaseline />
      <Box sx={{ minHeight: '100vh', bgcolor: 'background.default' }}>
        <Navigation 
          currentView={currentView}
          onBackToUpload={handleBackToUpload}
          onBackToTable={handleBackToTable}
          hasResults={tableData.length > 0}
        />
        
        <Box sx={{ p: 3 }}>
          {currentView === 'upload' && (
            <MultiUpload 
              onFilesUploaded={handleFilesUploaded}
              maxFiles={25}
            />
          )}
          
          {currentView === 'table' && (
            <ResultsTable
              data={tableData}
              onViewDetails={handleViewDetails}
              onExportData={handleExportData}
            />
          )}
          
          {currentView === 'detailed' && selectedDetailData && (
            <DetailedResults
              data={selectedDetailData}
              onBack={handleBackToTable}
              onDownloadReport={handleDownloadReport}
              onPrintReport={handlePrintReport}
            />
          )}
        </Box>
      </Box>
    </ThemeProvider>
  );
};

export default App;