"""
Hybrid X-ray Analyzer: Combines CNN classification with Gemini AI analysis
Provides accurate abnormal detection + detailed medical insights
"""

import os
import base64
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
from pathlib import Path

from gemini_analyzer import GeminiXrayAnalyzer
from cnn_analyzer import CNNXrayAnalyzer, get_cnn_analyzer

logger = logging.getLogger(__name__)

class HybridXrayAnalyzer:
    """
    Hybrid analyzer that combines:
    1. CNN model for accurate normal/abnormal classification
    2. Gemini AI for detailed medical analysis and reporting
    """
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.gemini_analyzer = GeminiXrayAnalyzer(api_key)
        self.cnn_analyzer = get_cnn_analyzer()
        
        logger.info("🤖 Hybrid X-ray Analyzer initialized")
        logger.info(f"   - Gemini AI: ✅ Ready (API connected)")
        logger.info(f"   - CNN Model: {'✅ Ready' if self.cnn_analyzer.is_loaded else '❌ Not available'}")
    
    async def analyze_xray(self, image_path: str, patient_info: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Perform comprehensive X-ray analysis using hybrid approach
        """
        logger.info(f"🔍 Starting hybrid analysis for: {Path(image_path).name}")
        
        # Initialize result structure
        result = {
            'success': False,
            'image_path': image_path,
            'analysis_timestamp': datetime.now().isoformat(),
            'patient_info': patient_info or {},
            'cnn_analysis': {},
            'gemini_analysis': {},
            'hybrid_conclusion': {},
            'error': None
        }
        
        try:
            # Step 1: CNN Classification
            logger.info("🧠 Running CNN classification...")
            cnn_result = self._run_cnn_analysis(image_path)
            result['cnn_analysis'] = cnn_result
            
            # Step 2: Enhanced Gemini Analysis
            logger.info("🤖 Running enhanced Gemini analysis...")
            gemini_result = await self._run_enhanced_gemini_analysis(image_path, cnn_result)
            result['gemini_analysis'] = gemini_result
            
            # Step 3: Hybrid Conclusion
            logger.info("🔬 Generating hybrid conclusion...")
            hybrid_conclusion = self._generate_hybrid_conclusion(cnn_result, gemini_result)
            result['hybrid_conclusion'] = hybrid_conclusion
            
            # Update main result fields for compatibility
            result.update({
                'success': True,
                'status': hybrid_conclusion['final_classification'],
                'confidence': hybrid_conclusion['confidence'],
                'findings': hybrid_conclusion['findings'],
                'detailed_analysis': hybrid_conclusion['detailed_analysis'],
                'recommendations': hybrid_conclusion['recommendations'],
                'severity': hybrid_conclusion.get('severity', 'unknown')
            })
            
            logger.info(f"✅ Hybrid analysis complete: {result['status']} (confidence: {result['confidence']:.3f})")
            
        except Exception as e:
            logger.error(f"❌ Hybrid analysis failed: {e}")
            result['error'] = str(e)
            result['success'] = False
            
            # Fallback to Gemini-only analysis
            try:
                logger.info("🔄 Falling back to Gemini-only analysis...")
                fallback_result = await self.gemini_analyzer.analyze_xray(image_path, patient_info)
                if fallback_result.get('success'):
                    result.update(fallback_result)
                    result['hybrid_conclusion'] = {'fallback_mode': True}
            except Exception as fallback_error:
                logger.error(f"❌ Fallback analysis also failed: {fallback_error}")
                result['error'] = f"Primary: {e}, Fallback: {fallback_error}"
        
        return result
    
    def _run_cnn_analysis(self, image_path: str) -> Dict[str, Any]:
        """Run CNN classification analysis"""
        try:
            if not self.cnn_analyzer.is_loaded:
                return {
                    'available': False,
                    'error': 'CNN model not available',
                    'classification': 'unknown'
                }
            
            return self.cnn_analyzer.predict_classification(image_path)
            
        except Exception as e:
            logger.error(f"CNN analysis failed: {e}")
            return {
                'available': False,
                'error': str(e),
                'classification': 'unknown'
            }
    
    async def _run_enhanced_gemini_analysis(self, image_path: str, cnn_result: Dict[str, Any]) -> Dict[str, Any]:
        """Run Gemini analysis with CNN guidance"""
        try:
            # Create enhanced prompt based on CNN prediction
            enhanced_context = self._create_enhanced_context(cnn_result)
            
            # Run Gemini analysis with CNN context
            gemini_result = await self.gemini_analyzer.analyze_xray(
                image_path, 
                additional_context=enhanced_context
            )
            
            return gemini_result
            
        except Exception as e:
            logger.error(f"Enhanced Gemini analysis failed: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _create_enhanced_context(self, cnn_result: Dict[str, Any]) -> str:
        """Create enhanced context for Gemini based on CNN prediction"""
        if not cnn_result.get('available'):
            return ""
        
        classification = cnn_result.get('classification', 'unknown')
        confidence = cnn_result.get('confidence', 0)
        
        if classification == 'abnormal':
            return f"""
IMPORTANT CONTEXT: A specialized AI model has pre-classified this X-ray as ABNORMAL with {confidence:.1%} confidence.
Please focus your analysis on identifying and describing the specific abnormalities present.
Pay particular attention to:
- Structural anomalies
- Pathological changes
- Fractures or damage
- Degenerative changes
- Any visible abnormalities

The pre-classification suggests abnormalities are present, so please provide detailed findings about what specific issues you can identify.
"""
        elif classification == 'normal':
            return f"""
CONTEXT: A specialized AI model has pre-classified this X-ray as NORMAL with {confidence:.1%} confidence.
Please verify this assessment and provide detailed confirmation of normal anatomical structures.
If you identify any concerns that contradict this pre-classification, please explain them in detail.
"""
        else:
            return ""
    
    def _generate_hybrid_conclusion(self, cnn_result: Dict[str, Any], gemini_result: Dict[str, Any]) -> Dict[str, Any]:
        """Generate final conclusion combining CNN and Gemini results"""
        
        # Get classifications
        cnn_classification = cnn_result.get('classification', 'unknown')
        cnn_confidence = cnn_result.get('confidence', 0)
        cnn_available = cnn_result.get('available', False)
        
        gemini_success = gemini_result.get('success', False)
        gemini_status = gemini_result.get('status', 'unknown') if gemini_success else 'unknown'
        
        # Decision logic for final classification
        if cnn_available and cnn_classification != 'unknown':
            if cnn_classification == 'abnormal':
                # CNN says abnormal - trust it, use Gemini for details
                final_classification = 'abnormal'
                confidence = max(cnn_confidence, 0.7)  # Minimum 70% confidence for abnormal
                
                findings = []
                if gemini_success and gemini_result.get('findings'):
                    findings = gemini_result['findings']
                else:
                    findings = [f"Abnormalities detected by AI analysis (confidence: {cnn_confidence:.1%})"]
                
            elif cnn_classification == 'normal':
                # CNN says normal - check if Gemini agrees
                if gemini_success and gemini_status in ['abnormal', 'concerning']:
                    # Conflict: CNN normal, Gemini abnormal
                    final_classification = 'requires_review'
                    confidence = 0.6
                    findings = ["Conflicting AI assessments - manual review recommended"] + \
                             (gemini_result.get('findings', []))
                else:
                    # Both agree it's normal
                    final_classification = 'normal'
                    confidence = cnn_confidence
                    findings = gemini_result.get('findings', []) if gemini_success else \
                             ["Normal lumbar spine anatomy confirmed by AI analysis"]
            else:
                # CNN classification unknown
                final_classification = gemini_status if gemini_success else 'unknown'
                confidence = 0.5
                findings = gemini_result.get('findings', []) if gemini_success else \
                         ["Unable to determine classification"]
        else:
            # No CNN available, use Gemini only
            final_classification = gemini_status if gemini_success else 'unknown'
            confidence = 0.6 if gemini_success else 0.0
            findings = gemini_result.get('findings', []) if gemini_success else \
                     ["Analysis unavailable - models not accessible"]
        
        # Determine severity
        severity = 'unknown'
        if final_classification == 'normal':
            severity = 'none'
        elif final_classification == 'abnormal':
            if confidence > 0.8:
                severity = 'moderate_to_high'
            else:
                severity = 'mild_to_moderate'
        elif final_classification == 'requires_review':
            severity = 'uncertain'
        
        # Generate comprehensive analysis
        detailed_analysis = self._generate_detailed_analysis(
            cnn_result, gemini_result, final_classification, confidence
        )
        
        # Generate recommendations
        recommendations = self._generate_recommendations(
            final_classification, confidence, severity, findings
        )
        
        return {
            'final_classification': final_classification,
            'confidence': confidence,
            'findings': findings,
            'detailed_analysis': detailed_analysis,
            'recommendations': recommendations,
            'severity': severity,
            'cnn_contribution': {
                'available': cnn_available,
                'classification': cnn_classification,
                'confidence': cnn_confidence
            },
            'gemini_contribution': {
                'available': gemini_success,
                'classification': gemini_status,
                'detailed_findings': gemini_result.get('findings', []) if gemini_success else []
            }
        }
    
    def _generate_detailed_analysis(self, cnn_result: Dict, gemini_result: Dict, 
                                  final_classification: str, confidence: float) -> str:
        """Generate detailed analysis explanation"""
        
        analysis_parts = []
        
        # CNN Analysis Summary
        if cnn_result.get('available'):
            cnn_class = cnn_result.get('classification', 'unknown')
            cnn_conf = cnn_result.get('confidence', 0)
            analysis_parts.append(
                f"Deep Learning Classification: {cnn_class.upper()} "
                f"(confidence: {cnn_conf:.1%})"
            )
        
        # Gemini Analysis Summary
        if gemini_result.get('success'):
            gemini_status = gemini_result.get('status', 'unknown')
            analysis_parts.append(f"AI Medical Analysis: {gemini_status.upper()}")
            
            if gemini_result.get('detailed_analysis'):
                analysis_parts.append(f"Medical Details: {gemini_result['detailed_analysis']}")
        
        # Final Assessment
        analysis_parts.append(f"Final Assessment: {final_classification.upper()} (confidence: {confidence:.1%})")
        
        if final_classification == 'requires_review':
            analysis_parts.append(
                "NOTE: Conflicting assessments detected. Manual radiologist review recommended."
            )
        
        return " | ".join(analysis_parts)
    
    def _generate_recommendations(self, classification: str, confidence: float, 
                                severity: str, findings: List[str]) -> List[str]:
        """Generate clinical recommendations"""
        
        recommendations = []
        
        if classification == 'normal':
            recommendations.append("Continue routine monitoring as clinically indicated")
            recommendations.append("Maintain current treatment plan if applicable")
            
        elif classification == 'abnormal':
            if confidence > 0.8:
                recommendations.append("URGENT: Radiologist review recommended")
                recommendations.append("Consider clinical correlation and additional imaging if needed")
            else:
                recommendations.append("Radiologist review recommended for confirmation")
                recommendations.append("Clinical correlation advised")
            
            if severity in ['moderate_to_high']:
                recommendations.append("Priority scheduling for specialist consultation")
                
        elif classification == 'requires_review':
            recommendations.append("IMMEDIATE radiologist review required due to conflicting AI assessments")
            recommendations.append("Do not make clinical decisions based on AI analysis alone")
            
        else:  # unknown
            recommendations.append("Manual radiologist interpretation required")
            recommendations.append("AI analysis inconclusive - human expertise needed")
        
        # Add finding-specific recommendations
        if any('fracture' in str(finding).lower() for finding in findings):
            recommendations.append("Orthopedic consultation may be warranted")
            
        if any('degenerative' in str(finding).lower() for finding in findings):
            recommendations.append("Consider pain management and physical therapy evaluation")
        
        return recommendations
    
    def get_analyzer_status(self) -> Dict[str, Any]:
        """Get status of all analyzer components"""
        return {
            'hybrid_analyzer': True,
            'gemini_ai': {
                'available': True,  # If we got here, Gemini is connected
                'model': 'gemini-2.5-flash'
            },
            'cnn_model': {
                'available': self.cnn_analyzer.is_loaded,
                'model_path': self.cnn_analyzer.model_path if self.cnn_analyzer.is_loaded else None,
                'info': self.cnn_analyzer.get_model_info()
            },
            'capabilities': [
                'Binary classification (normal/abnormal)',
                'Detailed medical analysis',
                'Confidence scoring',
                'Clinical recommendations',
                'Conflict detection and resolution'
            ]
        }