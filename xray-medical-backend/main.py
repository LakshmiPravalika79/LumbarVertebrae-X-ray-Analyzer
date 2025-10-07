from fastapi import FastAPI, UploadFile, File, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
import uvicorn
import os
import shutil
from pathlib import Path
from typing import List, Optional
import uuid
from datetime import datetime
import json
import asyncio
from contextlib import asynccontextmanager
from dotenv import load_dotenv

# Import analysis modules
from core.realistic_analyzer import RealisticXrayAnalyzer
from gemini_analyzer import GeminiXrayAnalyzer, test_gemini_connection
from enhanced_gemini_analyzer import EnhancedGeminiAnalyzer
from core.database import Database, AnalysisResult
from utils.file_handler import FileHandler
from utils.image_processor import ImageProcessor

# Load environment variables
load_dotenv()


# Application lifespan manager
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Initialize services
    print("🏥 Starting MediScan Pro Backend...")
    
    # Initialize database
    database = Database()
    database.create_tables()
    app.state.database = database
    
    # Initialize analyzer (Enhanced Gemini if API key available, otherwise realistic mock)
    gemini_api_key = os.getenv("GEMINI_API_KEY")
    
    if gemini_api_key and gemini_api_key != "YOUR_GEMINI_API_KEY_HERE":
        print("🤖 Initializing Enhanced Gemini AI analyzer...")
        
        if test_gemini_connection(gemini_api_key):
            app.state.xray_analyzer = EnhancedGeminiAnalyzer(gemini_api_key)
            app.state.analyzer_type = "enhanced_gemini"
            print("✅ Enhanced Gemini AI analyzer ready! (Improved abnormality detection)")
        else:
            print("❌ Gemini connection failed, falling back to realistic mock")
            app.state.xray_analyzer = RealisticXrayAnalyzer()
            app.state.analyzer_type = "realistic_mock"
    else:
        print("⚠️  No Gemini API key found, using realistic mock analyzer")
        app.state.xray_analyzer = RealisticXrayAnalyzer()
        app.state.analyzer_type = "realistic_mock"
    
    # Initialize other services
    app.state.file_handler = FileHandler()
    app.state.image_processor = ImageProcessor()
    
    # Ensure upload directories exist
    os.makedirs("uploads", exist_ok=True)
    os.makedirs("processed", exist_ok=True)
    os.makedirs("reports", exist_ok=True)
    
    print("✅ Backend initialization complete!")
    yield
    
    # Shutdown: Cleanup resources
    print("🔄 Shutting down MediScan Pro Backend...")
    app.state.database.close()
    print("✅ Shutdown complete!")


# Create FastAPI application
app = FastAPI(
    title="MediScan Pro - Lumbar X-ray Analyzer API",
    description="Medical-grade API for lumbar spine X-ray analysis with AI-powered vertebrae detection",
    version="2.1.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    lifespan=lifespan
)

# Configure CORS for medical application security
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],  # React frontend
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

# Mount static files for reports and images
import os
static_dir = os.path.join(os.path.dirname(__file__), "static")
if os.path.exists(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")


# Root endpoint
@app.get("/")
async def root():
    return {
        "message": "MediScan Pro - Lumbar X-ray Analyzer API",
        "version": "2.1.0",
        "status": "operational",
        "features": [
            "Multi-file X-ray upload (up to 25 images)",
            "AI-powered vertebrae detection (L3, L4, L5, Sacrum)",
            "Automated spacing measurements",
            "Abnormality detection and classification",
            "Medical-grade reporting",
            "HIPAA-compliant data handling"
        ]
    }


# Health check endpoint
@app.get("/health")
async def health_check():
    analyzer_type = getattr(app.state, 'analyzer_type', 'unknown')
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "services": {
            "database": "operational",
            "analyzer": "operational",
            "file_handler": "operational"
        },
        "analyzer_type": analyzer_type,
        "ai_enabled": analyzer_type == "gemini"
    }


# Get analyzer information
@app.get("/api/analyzer/info")
async def get_analyzer_info():
    """Get information about the current analyzer"""
    analyzer_type = getattr(app.state, 'analyzer_type', 'unknown')
    
    if analyzer_type == "enhanced_gemini":
        return {
            "type": "enhanced_gemini",
            "name": "Enhanced Gemini AI Analyzer",
            "description": "Real AI-powered analysis with improved abnormality detection",
            "capabilities": [
                "Advanced abnormality detection",
                "Detailed medical analysis",
                "Clinical recommendations", 
                "Safety-focused classification",
                "Comprehensive pathology assessment"
            ],
            "accuracy": "Very High (Enhanced for abnormality detection)",
            "status": "active",
            "enhancement": "Specialized prompts for accurate abnormal X-ray detection"
        }
    elif analyzer_type == "gemini":
        return {
            "type": "gemini",
            "name": "Google Gemini AI",
            "description": "Real AI-powered medical image analysis",
            "capabilities": [
                "Vertebrae detection and analysis",
                "Abnormality detection",
                "Medical measurements",
                "Clinical impressions",
                "Treatment recommendations"
            ],
            "accuracy": "High (AI-powered)",
            "status": "active"
        }
    else:
        return {
            "type": "realistic_mock",
            "name": "Realistic Mock Analyzer", 
            "description": "Advanced simulation for demonstration purposes",
            "capabilities": [
                "Simulated vertebrae analysis",
                "Mock abnormality detection",
                "Sample measurements",
                "Demo clinical impressions"
            ],
            "accuracy": "Simulated (for demonstration)",
            "status": "active",
            "note": "Add GEMINI_API_KEY to .env file to enable real AI analysis"
        }


# Upload multiple X-ray images
@app.post("/api/upload")
async def upload_xrays(
    background_tasks: BackgroundTasks,
    files: List[UploadFile] = File(...)
):
    """
    Upload multiple X-ray images for analysis (maximum 25 files)
    """
    if len(files) > 25:
        raise HTTPException(
            status_code=400, 
            detail="Maximum 25 files allowed per upload batch"
        )
    
    if not files or files[0].filename == '':
        raise HTTPException(status_code=400, detail="No files provided")
    
    results = []
    
    for file in files:
        # Validate file type
        if not app.state.file_handler.validate_image_file(file):
            results.append({
                "filename": file.filename,
                "status": "error",
                "error": "Invalid file type. Only JPEG, PNG, and DICOM files are allowed."
            })
            continue
        
        try:
            # Generate unique ID for this upload
            upload_id = str(uuid.uuid4())
            
            # Save uploaded file
            file_path = await app.state.file_handler.save_upload(file, upload_id)
            
            # Create database record
            analysis_record = AnalysisResult(
                id=upload_id,
                filename=file.filename,
                file_path=str(file_path),
                status="uploaded",
                uploaded_at=datetime.now()
            )
            
            app.state.database.create_analysis(analysis_record)
            
            # Schedule background analysis
            background_tasks.add_task(analyze_xray_background, upload_id, file_path)
            
            results.append({
                "id": upload_id,
                "filename": file.filename,
                "status": "uploaded",
                "message": "File uploaded successfully, analysis in progress"
            })
            
        except Exception as e:
            results.append({
                "filename": file.filename,
                "status": "error",
                "error": str(e)
            })
    
    return {"results": results}


# Background task for X-ray analysis
async def analyze_xray_background(upload_id: str, file_path: Path):
    """
    Background task to analyze X-ray image
    """
    try:
        # Update status to analyzing
        app.state.database.update_analysis_status(upload_id, "analyzing")
        
        # Check which analyzer type we're using
        analyzer_type = getattr(app.state, 'analyzer_type', 'realistic_mock')
        
        if analyzer_type == "enhanced_gemini":
            # For Enhanced Gemini analyzer, pass the file path directly
            analysis_results = await app.state.xray_analyzer.analyze_xray(
                str(file_path)
            )
        elif analyzer_type == "gemini":
            # For Gemini, read raw image bytes
            with open(file_path, 'rb') as f:
                image_data = f.read()
            
            # Perform Gemini analysis
            analysis_results = await app.state.xray_analyzer.analyze_xray(
                image_data, 
                file_path.name
            )
        else:
            # For mock analyzer, use processed image
            processed_image = await app.state.image_processor.preprocess_xray(file_path)
            analysis_results = await app.state.xray_analyzer.analyze_image(processed_image)
        
        # Update database with results
        app.state.database.update_analysis_results(upload_id, analysis_results)
        
        # Update status to completed
        app.state.database.update_analysis_status(upload_id, "completed")
        
        print(f"✅ Analysis completed for {upload_id} using {analyzer_type}")
        
    except Exception as e:
        print(f"❌ Analysis failed for {upload_id}: {str(e)}")
        app.state.database.update_analysis_status(upload_id, "error")
        app.state.database.update_analysis_error(upload_id, str(e))


# Get analysis results for table view
@app.get("/api/results")
async def get_analysis_results():
    """
    Get all analysis results for table view
    """
    try:
        results = app.state.database.get_all_analyses()
        return {"results": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Get detailed analysis for specific image
@app.get("/api/results/{analysis_id}")
async def get_detailed_analysis(analysis_id: str):
    """
    Get detailed analysis results for a specific image
    """
    try:
        result = app.state.database.get_analysis_by_id(analysis_id)
        if not result:
            raise HTTPException(status_code=404, detail="Analysis not found")
        
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Get analysis status
@app.get("/api/status/{analysis_id}")
async def get_analysis_status(analysis_id: str):
    """
    Get the current status of an analysis
    """
    try:
        status = app.state.database.get_analysis_status(analysis_id)
        if not status:
            raise HTTPException(status_code=404, detail="Analysis not found")
        
        return {"id": analysis_id, "status": status}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Get batch status for multiple analyses
@app.post("/api/batch-status")
async def get_batch_status(analysis_ids: List[str]):
    """
    Get status for multiple analyses
    """
    try:
        results = []
        for analysis_id in analysis_ids:
            status = app.state.database.get_analysis_status(analysis_id)
            results.append({
                "id": analysis_id,
                "status": status or "not_found"
            })
        
        return {"results": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Delete analysis
@app.delete("/api/results/{analysis_id}")
async def delete_analysis(analysis_id: str):
    """
    Delete an analysis and its associated files
    """
    try:
        # Get analysis record
        result = app.state.database.get_analysis_by_id(analysis_id)
        if not result:
            raise HTTPException(status_code=404, detail="Analysis not found")
        
        # Delete associated files
        if result.get('file_path'):
            file_path = Path(result['file_path'])
            if file_path.exists():
                file_path.unlink()
        
        # Delete from database
        app.state.database.delete_analysis(analysis_id)
        
        return {"message": "Analysis deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Export analysis results
@app.get("/api/export")
async def export_results(format: str = "csv"):
    """
    Export all analysis results in specified format
    """
    try:
        results = app.state.database.get_all_analyses()
        
        if format.lower() == "csv":
            csv_content = app.state.file_handler.export_to_csv(results)
            return JSONResponse(
                content={"data": csv_content, "format": "csv"},
                headers={"Content-Type": "application/json"}
            )
        elif format.lower() == "json":
            return {"data": results, "format": "json"}
        else:
            raise HTTPException(status_code=400, detail="Unsupported export format")
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Generate medical report
@app.get("/api/report/{analysis_id}")
async def generate_report(analysis_id: str, format: str = "pdf"):
    """
    Generate a medical report for specific analysis
    """
    try:
        result = app.state.database.get_analysis_by_id(analysis_id)
        if not result:
            raise HTTPException(status_code=404, detail="Analysis not found")
        
        # Generate report (placeholder for actual implementation)
        report_data = {
            "patient_id": analysis_id,
            "analysis_date": result.get('analyzed_at'),
            "findings": result.get('analysis_results', {}),
            "generated_at": datetime.now().isoformat()
        }
        
        return {"report": report_data, "format": format}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    print("🏥 Starting MediScan Pro Backend Server...")
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )