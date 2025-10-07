export interface UploadedFile {
  id: string;
  name: string;
  size: number;
  type: string;
  file: File;
  preview?: string;
  uploadTime: string;
  status: 'uploading' | 'completed' | 'error';
  progress: number;
  error?: string;
}

export interface XRayImage {
  id: string;
  file: File;
  preview: string;
  name: string;
  size: number;
  uploadedAt: Date;
  status: 'pending' | 'analyzing' | 'completed' | 'error';
  analysis?: XRayAnalysis;
}

export interface XRayAnalysis {
  id: string;
  imageId: string;
  vertebrae: VertebraeAnalysis[];
  overallStatus: 'normal' | 'abnormal';
  abnormalities: string[];
  confidence: number;
  processingTime: number;
  analysisDate: Date;
  measurements: Measurements;
}

export interface VertebraeAnalysis {
  vertebra: 'L3' | 'L4' | 'L5' | 'Sacrum';
  intensity: number;
  intensityStatus: 'normal' | 'abnormal';
  spacing: {
    above?: number;
    below?: number;
    status: 'normal' | 'abnormal';
  };
  fracture: {
    detected: boolean;
    confidence: number;
  };
  position: {
    x: number;
    y: number;
    width: number;
    height: number;
  };
}

export interface Measurements {
  l3l4Spacing: number;
  l4l5Spacing: number;
  l5SacrumSpacing: number;
  averageIntensity: number;
  normalSpacingRange: {
    min: number;
    max: number;
  };
}

export interface UploadProgress {
  imageId: string;
  progress: number;
  stage: 'uploading' | 'analyzing' | 'complete';
  message?: string;
}

export interface MedicalTheme {
  colors: {
    primary: string;
    secondary: string;
    success: string;
    warning: string;
    error: string;
    info: string;
    background: string;
    surface: string;
    text: {
      primary: string;
      secondary: string;
      disabled: string;
    };
  };
  spacing: {
    xs: number;
    sm: number;
    md: number;
    lg: number;
    xl: number;
  };
}

export interface TableViewData {
  id: string;
  imageName: string;
  uploadTime: string;
  overallStatus: 'normal' | 'abnormal';
  l3Status: 'normal' | 'abnormal';
  l4Status: 'normal' | 'abnormal';
  l5Status: 'normal' | 'abnormal';
  sacrumStatus: 'normal' | 'abnormal';
  l3l4Spacing: number;
  l4l5Spacing: number;
  l5SacrumSpacing: number;
  confidence: number;
  abnormalities: string[];
}

export interface DetailedViewData {
  id: string;
  imageName: string;
  imageUrl: string;
  analysisTime: string;
  overallStatus: 'normal' | 'abnormal';
  confidence: number;
  vertebraeAnalysis: {
    [key: string]: {
      status: 'normal' | 'abnormal';
      integrity: number;
      findings: string[];
    };
  };
  spacingAnalysis: {
    l3l4: {
      value: number;
      status: 'normal' | 'abnormal';
    };
    l4l5: {
      value: number;
      status: 'normal' | 'abnormal';
    };
    l5Sacrum: {
      value: number;
      status: 'normal' | 'abnormal';
    };
  };
  abnormalities: Array<{
    type: string;
    location: string;
    severity: string;
    confidence: number;
    description: string;
  }>;
  technicalDetails: {
    analysisMethod: string;
    processingTime: number;
    imageQuality: string;
    algorithmVersion: string;
  };
}