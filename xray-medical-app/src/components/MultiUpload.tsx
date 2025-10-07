import React, { useCallback, useState } from 'react';
import { useDropzone } from 'react-dropzone';
import {
  Box,
  Paper,
  Typography,
  Button,
  LinearProgress,
  Alert,
  Grid,
  Card,
  CardMedia,
  CardContent,
  IconButton,
  Chip,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  ListItemSecondaryAction,
} from '@mui/material';
import {
  CloudUpload as UploadIcon,
  Delete as DeleteIcon,
  CheckCircle as CheckIcon,
  Error as ErrorIcon,
  Warning as WarningIcon,
  PhotoLibrary as PhotoIcon,
  InsertDriveFile as FileIcon,
  Visibility as ViewIcon,
} from '@mui/icons-material';
import { motion, AnimatePresence } from 'framer-motion';
import { XRayImage, UploadProgress } from '../types';

interface MultiUploadProps {
  onFilesUploaded: (files: XRayImage[]) => void;
  maxFiles?: number;
  maxFileSize?: number;
  acceptedFormats?: string[];
  isUploading?: boolean;
  uploadProgress?: UploadProgress[];
}

const MultiUpload: React.FC<MultiUploadProps> = ({
  onFilesUploaded,
  maxFiles = 25,
  maxFileSize = 10 * 1024 * 1024, // 10MB
  acceptedFormats = ['.jpg', '.jpeg', '.png', '.dicom', '.dcm'],
  isUploading = false,
  uploadProgress = [],
}) => {
  const [uploadedFiles, setUploadedFiles] = useState<XRayImage[]>([]);
  const [errors, setErrors] = useState<string[]>([]);

  const validateFile = (file: File): string | null => {
    // Check file size
    if (file.size > maxFileSize) {
      return `File "${file.name}" exceeds maximum size of ${Math.round(maxFileSize / (1024 * 1024))}MB`;
    }

    // Check file type
    const fileExtension = '.' + file.name.split('.').pop()?.toLowerCase();
    if (!acceptedFormats.includes(fileExtension)) {
      return `File "${file.name}" has unsupported format. Supported: ${acceptedFormats.join(', ')}`;
    }

    return null;
  };

  const onDrop = useCallback((acceptedFiles: File[]) => {
    const newErrors: string[] = [];
    const validFiles: XRayImage[] = [];

    // Check total file count
    if (uploadedFiles.length + acceptedFiles.length > maxFiles) {
      newErrors.push(`Maximum ${maxFiles} files allowed. Please remove some files first.`);
      setErrors(newErrors);
      return;
    }

    acceptedFiles.forEach((file) => {
      const error = validateFile(file);
      if (error) {
        newErrors.push(error);
      } else {
        const xrayImage: XRayImage = {
          id: `${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
          file,
          preview: URL.createObjectURL(file),
          name: file.name,
          size: file.size,
          uploadedAt: new Date(),
          status: 'pending',
        };
        validFiles.push(xrayImage);
      }
    });

    if (newErrors.length > 0) {
      setErrors(newErrors);
    } else {
      setErrors([]);
    }

    if (validFiles.length > 0) {
      const updatedFiles = [...uploadedFiles, ...validFiles];
      setUploadedFiles(updatedFiles);
      onFilesUploaded(updatedFiles);
    }
  }, [uploadedFiles, maxFiles, maxFileSize, acceptedFormats, onFilesUploaded]);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'image/jpeg': ['.jpg', '.jpeg'],
      'image/png': ['.png'],
      'application/dicom': ['.dcm', '.dicom'],
    },
    multiple: true,
    maxFiles: maxFiles - uploadedFiles.length,
    disabled: isUploading,
  });

  const removeFile = (fileId: string) => {
    const updatedFiles = uploadedFiles.filter((file) => file.id !== fileId);
    setUploadedFiles(updatedFiles);
    onFilesUploaded(updatedFiles);
    
    // Clear errors when files are removed
    if (errors.length > 0) {
      setErrors([]);
    }
  };

  const clearAllFiles = () => {
    setUploadedFiles([]);
    setErrors([]);
    onFilesUploaded([]);
  };

  const formatFileSize = (bytes: number): string => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  const getStatusIcon = (status: XRayImage['status']) => {
    switch (status) {
      case 'completed':
        return <CheckIcon color="success" />;
      case 'error':
        return <ErrorIcon color="error" />;
      case 'analyzing':
        return <WarningIcon color="warning" />;
      default:
        return <PhotoIcon color="primary" />;
    }
  };

  const getStatusColor = (status: XRayImage['status']) => {
    switch (status) {
      case 'completed':
        return 'success';
      case 'error':
        return 'error';
      case 'analyzing':
        return 'warning';
      default:
        return 'default';
    }
  };

  return (
    <Box>
      {/* Upload Zone */}
      <Paper
        {...getRootProps()}
        elevation={2}
        sx={{
          p: 4,
          textAlign: 'center',
          cursor: isUploading ? 'not-allowed' : 'pointer',
          border: '2px dashed',
          borderColor: isDragActive ? 'primary.main' : 'grey.300',
          backgroundColor: isDragActive ? 'action.hover' : 'background.paper',
          transition: 'all 0.3s ease',
          opacity: isUploading ? 0.6 : 1,
          '&:hover': {
            borderColor: isUploading ? 'grey.300' : 'primary.main',
            backgroundColor: isUploading ? 'background.paper' : 'action.hover',
            transform: isUploading ? 'none' : 'translateY(-2px)',
          },
        }}
      >
        <input {...getInputProps()} />
        <motion.div
          animate={{ scale: isDragActive ? 1.05 : 1 }}
          transition={{ duration: 0.2 }}
        >
          <UploadIcon sx={{ fontSize: 64, color: 'primary.main', mb: 2 }} />
          <Typography variant="h5" gutterBottom>
            {isDragActive ? 'Drop X-ray images here' : 'Upload X-ray Images'}
          </Typography>
          <Typography variant="body1" color="text.secondary" sx={{ mb: 2 }}>
            Drag and drop up to {maxFiles} X-ray images, or click to browse
          </Typography>
          <Box sx={{ display: 'flex', justifyContent: 'center', gap: 2, flexWrap: 'wrap', mb: 2 }}>
            <Chip label={`Max ${maxFiles} files`} size="small" variant="outlined" />
            <Chip label={`Max ${Math.round(maxFileSize / (1024 * 1024))}MB each`} size="small" variant="outlined" />
            <Chip label="JPEG, PNG, DICOM" size="small" variant="outlined" />
          </Box>
          <Button variant="contained" disabled={isUploading} sx={{ mt: 1 }}>
            {isUploading ? 'Processing...' : 'Choose Files'}
          </Button>
        </motion.div>
      </Paper>

      {/* Error Messages */}
      <AnimatePresence>
        {errors.length > 0 && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            exit={{ opacity: 0, height: 0 }}
          >
            <Alert severity="error" sx={{ mt: 2 }} onClose={() => setErrors([])}>
              <Typography variant="subtitle2" gutterBottom>
                Upload Errors:
              </Typography>
              <List dense>
                {errors.map((error, index) => (
                  <ListItem key={index} sx={{ py: 0 }}>
                    <ListItemText primary={error} />
                  </ListItem>
                ))}
              </List>
            </Alert>
          </motion.div>
        )}
      </AnimatePresence>

      {/* File Count and Actions */}
      {uploadedFiles.length > 0 && (
        <Box sx={{ mt: 3, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <Typography variant="h6">
            Uploaded Files ({uploadedFiles.length}/{maxFiles})
          </Typography>
          <Button
            variant="outlined"
            color="error"
            onClick={clearAllFiles}
            disabled={isUploading}
            size="small"
          >
            Clear All
          </Button>
        </Box>
      )}

      {/* Upload Progress */}
      {isUploading && uploadProgress.length > 0 && (
        <Box sx={{ mt: 2 }}>
          <Typography variant="subtitle2" gutterBottom>
            Analysis Progress
          </Typography>
          {uploadProgress.map((progress) => (
            <Box key={progress.imageId} sx={{ mb: 1 }}>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 0.5 }}>
                <Typography variant="body2">
                  {uploadedFiles.find(f => f.id === progress.imageId)?.name || 'Unknown'}
                </Typography>
                <Typography variant="body2">{progress.progress}%</Typography>
              </Box>
              <LinearProgress
                variant="determinate"
                value={progress.progress}
                sx={{ height: 6, borderRadius: 3 }}
              />
              {progress.message && (
                <Typography variant="caption" color="text.secondary">
                  {progress.message}
                </Typography>
              )}
            </Box>
          ))}
        </Box>
      )}

      {/* File Grid */}
      {uploadedFiles.length > 0 && (
        <Grid container spacing={2} sx={{ mt: 2 }}>
          {uploadedFiles.map((file) => (
            <Grid item xs={12} sm={6} md={4} lg={3} key={file.id}>
              <motion.div
                initial={{ opacity: 0, scale: 0.9 }}
                animate={{ opacity: 1, scale: 1 }}
                exit={{ opacity: 0, scale: 0.9 }}
                transition={{ duration: 0.3 }}
              >
                <Card
                  sx={{
                    height: '100%',
                    display: 'flex',
                    flexDirection: 'column',
                    position: 'relative',
                    '&:hover': {
                      transform: 'translateY(-4px)',
                      boxShadow: 4,
                    },
                    transition: 'all 0.3s ease',
                  }}
                >
                  {/* Image Preview */}
                  <CardMedia
                    component="img"
                    height="150"
                    image={file.preview}
                    alt={file.name}
                    sx={{
                      objectFit: 'cover',
                      backgroundColor: 'grey.100',
                    }}
                  />

                  {/* Status Badge */}
                  <Chip
                    icon={getStatusIcon(file.status)}
                    label={file.status.toUpperCase()}
                    color={getStatusColor(file.status) as any}
                    size="small"
                    sx={{
                      position: 'absolute',
                      top: 8,
                      right: 8,
                      backgroundColor: 'rgba(255, 255, 255, 0.9)',
                    }}
                  />

                  <CardContent sx={{ flexGrow: 1, pb: 1 }}>
                    <Typography variant="subtitle2" noWrap title={file.name}>
                      {file.name}
                    </Typography>
                    <Typography variant="caption" color="text.secondary" display="block">
                      {formatFileSize(file.size)}
                    </Typography>
                    <Typography variant="caption" color="text.secondary" display="block">
                      {file.uploadedAt.toLocaleTimeString()}
                    </Typography>
                  </CardContent>

                  {/* Actions */}
                  <Box sx={{ p: 1, pt: 0, display: 'flex', justifyContent: 'flex-end', gap: 1 }}>
                    <IconButton
                      size="small"
                      onClick={() => window.open(file.preview, '_blank')}
                      title="View Image"
                    >
                      <ViewIcon fontSize="small" />
                    </IconButton>
                    <IconButton
                      size="small"
                      onClick={() => removeFile(file.id)}
                      disabled={isUploading}
                      color="error"
                      title="Remove File"
                    >
                      <DeleteIcon fontSize="small" />
                    </IconButton>
                  </Box>
                </Card>
              </motion.div>
            </Grid>
          ))}
        </Grid>
      )}

      {/* Empty State */}
      {uploadedFiles.length === 0 && !isUploading && (
        <Box sx={{ textAlign: 'center', py: 4, color: 'text.secondary' }}>
          <PhotoIcon sx={{ fontSize: 48, mb: 2 }} />
          <Typography variant="body1">
            No images uploaded yet. Start by uploading your X-ray images above.
          </Typography>
        </Box>
      )}
    </Box>
  );
};

export default MultiUpload;