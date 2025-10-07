from sqlalchemy import create_engine, Column, String, Integer, Float, DateTime, Text, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from datetime import datetime
import json
import logging
from typing import Dict, List, Optional, Any
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

Base = declarative_base()

class AnalysisResult(Base):
    """
    Database model for X-ray analysis results
    """
    __tablename__ = "analysis_results"
    
    id = Column(String, primary_key=True)
    filename = Column(String, nullable=False)
    file_path = Column(String, nullable=False)
    status = Column(String, nullable=False)  # uploaded, analyzing, completed, error
    uploaded_at = Column(DateTime, default=datetime.now)
    analyzed_at = Column(DateTime, nullable=True)
    
    # Analysis results (stored as JSON)
    overall_status = Column(String, nullable=True)  # normal, abnormal
    confidence = Column(Float, nullable=True)
    vertebrae_analysis = Column(Text, nullable=True)  # JSON string
    spacing_measurements = Column(Text, nullable=True)  # JSON string
    abnormalities = Column(Text, nullable=True)  # JSON string
    processing_time = Column(Float, nullable=True)  # milliseconds
    analysis_metadata = Column(Text, nullable=True)  # JSON string
    
    # Error handling
    error_message = Column(Text, nullable=True)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for API responses"""
        return {
            "id": self.id,
            "filename": self.filename,
            "file_path": self.file_path,
            "status": self.status,
            "uploaded_at": self.uploaded_at.isoformat() if self.uploaded_at else None,
            "analyzed_at": self.analyzed_at.isoformat() if self.analyzed_at else None,
            "overall_status": self.overall_status,
            "confidence": self.confidence,
            "vertebrae_analysis": json.loads(self.vertebrae_analysis) if self.vertebrae_analysis else None,
            "spacing_measurements": json.loads(self.spacing_measurements) if self.spacing_measurements else None,
            "abnormalities": json.loads(self.abnormalities) if self.abnormalities else None,
            "processing_time": self.processing_time,
            "analysis_metadata": json.loads(self.analysis_metadata) if self.analysis_metadata else None,
            "error_message": self.error_message
        }


class Database:
    """
    Database manager for medical X-ray analysis system
    """
    
    def __init__(self, db_path: str = "mediscan_pro.db"):
        """
        Initialize database connection
        """
        self.db_path = db_path
        self.engine = create_engine(f"sqlite:///{db_path}", echo=False)
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
        
        logger.info(f"🗄️ Database initialized: {db_path}")
    
    def create_tables(self):
        """
        Create all database tables
        """
        Base.metadata.create_all(bind=self.engine)
        logger.info("✅ Database tables created successfully")
    
    def get_session(self) -> Session:
        """
        Get database session
        """
        return self.SessionLocal()
    
    def create_analysis(self, analysis: AnalysisResult) -> bool:
        """
        Create new analysis record
        """
        try:
            with self.get_session() as session:
                session.add(analysis)
                session.commit()
                logger.info(f"📝 Created analysis record: {analysis.id}")
                return True
        except Exception as e:
            logger.error(f"❌ Failed to create analysis: {str(e)}")
            return False
    
    def get_analysis_by_id(self, analysis_id: str) -> Optional[Dict[str, Any]]:
        """
        Get analysis by ID
        """
        try:
            with self.get_session() as session:
                analysis = session.query(AnalysisResult).filter(
                    AnalysisResult.id == analysis_id
                ).first()
                
                if analysis:
                    return analysis.to_dict()
                return None
        except Exception as e:
            logger.error(f"❌ Failed to get analysis {analysis_id}: {str(e)}")
            return None
    
    def get_all_analyses(self) -> List[Dict[str, Any]]:
        """
        Get all analysis records
        """
        try:
            with self.get_session() as session:
                analyses = session.query(AnalysisResult).order_by(
                    AnalysisResult.uploaded_at.desc()
                ).all()
                
                return [analysis.to_dict() for analysis in analyses]
        except Exception as e:
            logger.error(f"❌ Failed to get all analyses: {str(e)}")
            return []
    
    def update_analysis_status(self, analysis_id: str, status: str) -> bool:
        """
        Update analysis status
        """
        try:
            with self.get_session() as session:
                analysis = session.query(AnalysisResult).filter(
                    AnalysisResult.id == analysis_id
                ).first()
                
                if analysis:
                    analysis.status = status
                    if status == "analyzing":
                        analysis.analyzed_at = datetime.now()
                    session.commit()
                    logger.info(f"📊 Updated analysis {analysis_id} status: {status}")
                    return True
                return False
        except Exception as e:
            logger.error(f"❌ Failed to update analysis status: {str(e)}")
            return False
    
    def update_analysis_results(self, analysis_id: str, results: Any) -> bool:
        """
        Update analysis with results (supports both object and dict formats)
        """
        try:
            with self.get_session() as session:
                analysis = session.query(AnalysisResult).filter(
                    AnalysisResult.id == analysis_id
                ).first()
                
                if analysis:
                    # Handle enhanced Gemini analyzer dictionary format
                    if isinstance(results, dict):
                        analysis.overall_status = results.get('status', 'unknown')
                        analysis.confidence = results.get('confidence', 0.0)
                        analysis.processing_time = results.get('processing_time', 0.0)
                        
                        # Store enhanced analyzer results
                        analysis.vertebrae_analysis = json.dumps({
                            "findings": results.get('findings', []),
                            "detailed_analysis": results.get('detailed_analysis', ''),
                            "analyzer_type": results.get('analyzer_type', 'enhanced_gemini')
                        })
                        
                        analysis.spacing_measurements = json.dumps({
                            "recommendations": results.get('recommendations', []),
                            "clinical_significance": results.get('clinical_significance', '')
                        })
                        
                        analysis.abnormalities = json.dumps(results.get('abnormalities', []))
                        analysis.analysis_metadata = json.dumps({
                            "success": results.get('success', False),
                            "analyzer_type": results.get('analyzer_type', 'enhanced_gemini'),
                            "raw_response": results.get('raw_response', '')
                        })
                        
                    else:
                        # Handle legacy XrayAnalysisResult object format
                        analysis.overall_status = results.overall_status
                        analysis.confidence = results.confidence
                        analysis.processing_time = results.processing_time
                        
                        # Convert complex objects to JSON
                        vertebrae_data = []
                        for vertebra in results.vertebrae:
                            vertebrae_data.append({
                                "vertebra_type": vertebra.vertebra_type,
                                "bounding_box": vertebra.bounding_box,
                                "confidence": vertebra.confidence,
                                "intensity": vertebra.intensity,
                                "status": vertebra.status,
                                "abnormalities": vertebra.abnormalities
                            })
                        
                        spacing_data = []
                        for spacing in results.spacing_measurements:
                            spacing_data.append({
                                "vertebra_pair": spacing.vertebra_pair,
                                "distance": spacing.distance,
                                "status": spacing.status,
                                "confidence": spacing.confidence
                            })
                        
                        analysis.vertebrae_analysis = json.dumps(vertebrae_data)
                        analysis.spacing_measurements = json.dumps(spacing_data)
                        analysis.abnormalities = json.dumps(results.abnormalities)
                        analysis.analysis_metadata = json.dumps(results.analysis_metadata)
                    
                    analysis.analyzed_at = datetime.now()
                    session.commit()
                    logger.info(f"📈 Updated analysis results for {analysis_id}")
                    return True
                return False
        except Exception as e:
            logger.error(f"❌ Failed to update analysis results: {str(e)}")
            return False
    
    def update_analysis_error(self, analysis_id: str, error_message: str) -> bool:
        """
        Update analysis with error message
        """
        try:
            with self.get_session() as session:
                analysis = session.query(AnalysisResult).filter(
                    AnalysisResult.id == analysis_id
                ).first()
                
                if analysis:
                    analysis.error_message = error_message
                    analysis.analyzed_at = datetime.now()
                    session.commit()
                    logger.info(f"🚨 Updated analysis error for {analysis_id}")
                    return True
                return False
        except Exception as e:
            logger.error(f"❌ Failed to update analysis error: {str(e)}")
            return False
    
    def get_analysis_status(self, analysis_id: str) -> Optional[str]:
        """
        Get analysis status
        """
        try:
            with self.get_session() as session:
                analysis = session.query(AnalysisResult).filter(
                    AnalysisResult.id == analysis_id
                ).first()
                
                return analysis.status if analysis else None
        except Exception as e:
            logger.error(f"❌ Failed to get analysis status: {str(e)}")
            return None
    
    def delete_analysis(self, analysis_id: str) -> bool:
        """
        Delete analysis record
        """
        try:
            with self.get_session() as session:
                analysis = session.query(AnalysisResult).filter(
                    AnalysisResult.id == analysis_id
                ).first()
                
                if analysis:
                    session.delete(analysis)
                    session.commit()
                    logger.info(f"🗑️ Deleted analysis: {analysis_id}")
                    return True
                return False
        except Exception as e:
            logger.error(f"❌ Failed to delete analysis: {str(e)}")
            return False
    
    def get_analyses_by_status(self, status: str) -> List[Dict[str, Any]]:
        """
        Get analyses by status
        """
        try:
            with self.get_session() as session:
                analyses = session.query(AnalysisResult).filter(
                    AnalysisResult.status == status
                ).order_by(AnalysisResult.uploaded_at.desc()).all()
                
                return [analysis.to_dict() for analysis in analyses]
        except Exception as e:
            logger.error(f"❌ Failed to get analyses by status: {str(e)}")
            return []
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get database statistics
        """
        try:
            with self.get_session() as session:
                total_analyses = session.query(AnalysisResult).count()
                completed_analyses = session.query(AnalysisResult).filter(
                    AnalysisResult.status == "completed"
                ).count()
                error_analyses = session.query(AnalysisResult).filter(
                    AnalysisResult.status == "error"
                ).count()
                
                normal_results = session.query(AnalysisResult).filter(
                    AnalysisResult.overall_status == "normal"
                ).count()
                abnormal_results = session.query(AnalysisResult).filter(
                    AnalysisResult.overall_status == "abnormal"
                ).count()
                
                return {
                    "total_analyses": total_analyses,
                    "completed_analyses": completed_analyses,
                    "error_analyses": error_analyses,
                    "normal_results": normal_results,
                    "abnormal_results": abnormal_results,
                    "success_rate": (completed_analyses / total_analyses * 100) if total_analyses > 0 else 0
                }
        except Exception as e:
            logger.error(f"❌ Failed to get statistics: {str(e)}")
            return {}
    
    def close(self):
        """
        Close database connection
        """
        self.engine.dispose()
        logger.info("🔒 Database connection closed")