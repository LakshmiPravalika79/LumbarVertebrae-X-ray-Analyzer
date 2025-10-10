# Lumbar X-ray Analyzer

A comprehensive medical imaging analysis application for automated lumbar spine assessment. This system analyzes L3, L4, L5 vertebrae and sacrum in X-ray images, providing detailed measurements, abnormality detection, and clinical insights.

## 🎯 Project Overview

The Lumbar X-ray Analyzer is designed to assist medical professionals and researchers in analyzing lumbar spine X-ray images. It provides:

- **Automated Vertebrae Detection**: Identifies L3, L4, L5, and sacrum
- **Spacing Analysis**: Measures inter-vertebral spacing (normal range: 4.0-8.0mm)
- **Intensity Assessment**: Analyzes bone density and detects low intensity regions
- **Fracture Detection**: Uses advanced edge detection for fracture identification
- **Visual Reporting**: Generates annotated images with comprehensive analysis overlays

## 🏗️ Architecture

### Backend (Python FastAPI)
- **Framework**: FastAPI with Python 3.8+
- **Image Processing**: OpenCV, PIL, NumPy, scikit-image
- **Database**: SQLite with SQLAlchemy ORM
- **API**: RESTful endpoints with automatic documentation
- **Analysis Engine**: Computer vision algorithms for medical imaging

### Frontend (React TypeScript)
- **Framework**: React 18 with TypeScript
- **UI Library**: Material-UI (MUI) for professional medical interface
- **State Management**: React hooks and context
- **File Upload**: Drag-and-drop with validation
- **Visualization**: Interactive vertebrae visualization with status indicators

## 🚀 Quick Start

### Prerequisites
- Python 3.8+ with pip
- Node.js 16+ with npm
- 4GB+ RAM (for image processing)

### 1. Backend Setup
```bash
cd xray-medical-backend

# Install dependencies
pip install -r requirements.txt

# Start the backend server
python main.py
```
Backend will be available at: http://localhost:8000

### 2. Frontend Setup
```bash
cd xray-analyzer-frontend

# Install dependencies
npm install

# Start the development server
npm start
```
Frontend will be available at: http://localhost:3001

### 3. Access the Application
- **Web Interface**: http://localhost:3001
- **API Documentation**: http://localhost:8000/docs
- **API Health Check**: http://localhost:8000/health

## 📋 Features

### Core Analysis Capabilities
- ✅ **L3, L4, L5 Vertebrae Detection**: Automatic identification and localization
- ✅ **Sacrum Analysis**: Comprehensive sacral region assessment
- ✅ **Vertebral Spacing**: Inter-vertebral distance measurement
- ✅ **Intensity Analysis**: Bone density assessment with abnormality detection
- ✅ **Fracture Detection**: Edge-based fracture identification with confidence scoring
- ✅ **Visual Annotation**: Automated image annotation with analysis overlays

### User Interface Features
- ✅ **Modern Web Interface**: Professional medical application design
- ✅ **Drag & Drop Upload**: Easy file upload with validation
- ✅ **Real-time Processing**: Live progress tracking during analysis
- ✅ **Comprehensive Reports**: Detailed analysis results with measurements
- ✅ **Analysis History**: View and manage previous analyses
- ✅ **Interactive Visualization**: Color-coded vertebrae status indicators
- ✅ **Responsive Design**: Works on desktop, tablet, and mobile devices

### Technical Features
- ✅ **RESTful API**: Well-documented REST endpoints
- ✅ **File Format Support**: JPEG, PNG, DICOM images
- ✅ **Database Storage**: Persistent analysis results and metadata
- ✅ **Error Handling**: Comprehensive error management and user feedback
- ✅ **Performance Optimization**: Efficient image processing and caching
- ✅ **Security**: Input validation and secure file handling

## 📊 Analysis Parameters

### Normal Value Ranges
| Parameter | Normal Range | Description |
|-----------|--------------|-------------|
| **Inter-vertebral Spacing** | 4.0 - 8.0 mm | Distance between adjacent vertebrae |
| **Bone Intensity** | > 30% | Normalized intensity indicating bone density |
| **Fracture Confidence** | 0.0 - 1.0 | Probability score for fracture detection |
| **Overall Confidence** | 0.5 - 1.0 | System confidence in analysis results |

### Supported File Formats
- **JPEG** (.jpg, .jpeg): Standard image format
- **PNG** (.png): Lossless image format
- **DICOM** (.dcm, .dicom): Medical imaging standard
- **Maximum File Size**: 10MB

## 🔧 API Reference

### Main Endpoints

#### Upload Image
```http
POST /api/v1/upload
Content-Type: multipart/form-data

Response: {
  "file_id": "uuid",
  "filename": "image.jpg",
  "file_size": 2048576,
  "uploaded_at": "2025-09-28T10:30:00Z"
}
```

#### Analyze Image
```http
POST /api/v1/analyze/{file_id}

Response: {
  "analysis_id": "uuid",
  "file_id": "uuid",
  "vertebrae_analysis": [...],
  "overall_status": "normal|abnormal",
  "abnormalities_detected": [...],
  "analysis_confidence": 0.85,
  "processing_time": 2.5
}
```

#### Get Analysis Results
```http
GET /api/v1/analysis/{analysis_id}

Response: AnalysisResult
```

### Complete API documentation available at: http://localhost:8000/docs

## 📈 Analysis Workflow

1. **Image Upload**: User uploads X-ray image via web interface
2. **Preprocessing**: Image normalization, noise reduction, contrast enhancement
3. **Vertebrae Detection**: AI-powered identification of L3, L4, L5, and sacrum
4. **Measurement Extraction**: Spacing, intensity, and morphological analysis
5. **Abnormality Detection**: Comparison against normal ranges
6. **Fracture Analysis**: Edge detection and pattern recognition
7. **Report Generation**: Comprehensive analysis with visual annotations
8. **Results Storage**: Persistent storage for future reference

## 🎨 User Interface

### Main Pages
- **Home Page**: Project overview and quick start options
- **Analysis Page**: File upload and real-time analysis interface
- **Results Dashboard**: Comprehensive analysis visualization
- **History Page**: Previous analysis management
- **About Page**: Technical specifications and medical disclaimer

### Key Components
- **FileUpload**: Drag-and-drop interface with validation
- **AnalysisResults**: Detailed results with interactive tables
- **VertebraeVisualization**: Visual representation of spine structure
- **StatusIndicators**: Color-coded health status displays

## 🔬 Technical Implementation

### Backend Architecture
```
xray-medical-backend/
├── main.py              # FastAPI application entry point
├── gemini_analyzer.py   # Gemini AI integration for analysis
├── core/                # Core business logic modules
├── utils/               # Utility functions and helpers
├── mediscan_pro.db      # SQLite database
└── uploads/             # File storage directory
```

### Frontend Architecture
```
xray-medical-app/
├── src/
│   ├── components/      # Reusable UI components
│   ├── pages/          # Route-level components
│   ├── services/       # API client and utilities
│   ├── types/          # TypeScript definitions
│   └── config.ts       # Configuration settings
└── public/             # Static assets
```

## 🧪 Testing

### Backend Testing
```bash
cd xray-medical-backend
python -m pytest tests/
```

### Frontend Testing
```bash
cd xray-medical-app
npm test
```

## 📚 Documentation

### Available Documentation
- **API Documentation**: Automatic OpenAPI/Swagger docs at `/docs`
- **Backend README**: Detailed backend setup and development guide
- **Frontend README**: React application documentation
- **Technical Specifications**: Analysis algorithms and parameters
- **User Guide**: Step-by-step usage instructions

## ⚠️ Medical Disclaimer

**IMPORTANT**: This application is designed for educational and research purposes only. 

- Results should always be verified by qualified medical professionals
- Not intended for clinical diagnosis or treatment decisions
- Always consult healthcare providers for medical advice
- Algorithm accuracy may vary based on image quality and conditions
- No warranty is provided for medical or diagnostic accuracy

## 🔒 Security & Privacy

- **Local Processing**: All analysis performed locally, no cloud dependencies
- **Data Privacy**: Images and results stored locally on your system
- **Secure Upload**: File validation and sanitization
- **No External Transmission**: Patient data never leaves your environment

## 🛠️ Development

### Development Setup
1. Clone the repository
2. Follow backend setup instructions
3. Follow frontend setup instructions
4. Use provided development scripts

### Contributing Guidelines
- Follow code style conventions
- Add tests for new features
- Update documentation
- Submit pull requests for review

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 📞 Support

For technical support and questions:
- Check the troubleshooting sections in component READMEs
- Review API documentation
- Submit issues on the project repository

## 🚀 Future Enhancements

Planned features for future releases:
- Advanced AI models for improved accuracy
- Support for additional vertebrae (L1, L2)
- Integration with PACS systems
- Multi-language support
- Enhanced reporting formats
- Batch processing capabilities

---

**Version**: 1.0.0  
**Last Updated**: September 28, 2025  
**Compatibility**: Python 3.8+, Node.js 16+
