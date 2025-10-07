import os
import io
import base64
import logging
import google.generativeai as genai
from PIL import Image
import json
from typing import Dict, List, Optional, Tuple
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class GeminiXrayAnalyzer:
    """Real X-ray analyzer using Google Gemini AI for medical image analysis"""
    
    def __init__(self, api_key: str, model_name: str = "gemini-2.5-flash"):
        """Initialize the Gemini analyzer with API key"""
        self.api_key = api_key
        self.model_name = model_name
        self.datasets_path = Path("datasets")
        
        # Configure Gemini
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(model_name)
        
        # Load reference images for comparison
        self.reference_images = self._load_reference_images()
        
        logger.info(f"Initialized Gemini analyzer with model: {model_name}")
    
    def _load_reference_images(self) -> Dict[str, List[str]]:
        """Load reference images from datasets folder"""
        references = {"normal": [], "abnormal": []}
        
        for category in ["normal", "abnormal"]:
            category_path = self.datasets_path / category
            if category_path.exists():
                for img_file in category_path.glob("*"):
                    if img_file.suffix.lower() in ['.jpg', '.jpeg', '.png']:
                        references[category].append(str(img_file))
        
        logger.info(f"Loaded {len(references['normal'])} normal and {len(references['abnormal'])} abnormal reference images")
        return references
    
    def _prepare_image_for_gemini(self, image_data: bytes) -> Image.Image:
        """Prepare image for Gemini analysis"""
        try:
            image = Image.open(io.BytesIO(image_data))
            
            # Convert to RGB if needed
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            # Resize if too large (Gemini has size limits)
            max_size = 1024
            if max(image.size) > max_size:
                image.thumbnail((max_size, max_size), Image.Resampling.LANCZOS)
            
            return image
        
        except Exception as e:
            logger.error(f"Error preparing image: {str(e)}")
            raise
    
    def _create_analysis_prompt(self) -> str:
        """Create detailed prompt for X-ray analysis"""
        return """
You are an expert radiologist analyzing a lumbar spine X-ray image. Provide a detailed medical analysis in JSON format.

CRITICAL: Be very careful about the overall_status determination. If you detect ANY abnormalities, fractures, degenerative changes, misalignments, or concerning findings, the overall_status MUST be "abnormal". Only use "normal" if the spine appears completely healthy with no pathological findings.

Analyze the image for:
1. Overall spine alignment and structure
2. Vertebral body integrity (L1-L5) - look for fractures, compression, deformity
3. Disc space heights and degenerative changes
4. Joint spaces and arthritis
5. Bone density and fractures
6. Soft tissue abnormalities
7. Any signs of pathology, degeneration, or trauma

IMPORTANT CLASSIFICATION RULES:
- "normal": Only if ALL structures appear completely healthy with no pathological findings
- "abnormal": If ANY abnormality is detected (fractures, degeneration, misalignment, etc.)

Return your analysis in this exact JSON format:
{
    "overall_status": "normal" or "abnormal",
    "confidence_score": 0.0-1.0,
    "findings": [
        {
            "vertebra": "L1-L5 or overall",
            "finding": "description of finding",
            "severity": "mild/moderate/severe",
            "status": "normal/abnormal"
        }
    ],
    "vertebrae_analysis": {
        "L1": {"status": "normal/abnormal", "confidence": 0.0-1.0, "findings": "description"},
        "L2": {"status": "normal/abnormal", "confidence": 0.0-1.0, "findings": "description"},
        "L3": {"status": "normal/abnormal", "confidence": 0.0-1.0, "findings": "description"},
        "L4": {"status": "normal/abnormal", "confidence": 0.0-1.0, "findings": "description"},
        "L5": {"status": "normal/abnormal", "confidence": 0.0-1.0, "findings": "description"}
    },
    "measurements": {
        "disc_heights": {
            "L1_L2": {"height_mm": 10.5, "status": "normal/reduced"},
            "L2_L3": {"height_mm": 11.2, "status": "normal/reduced"},
            "L3_L4": {"height_mm": 10.8, "status": "normal/reduced"},
            "L4_L5": {"height_mm": 12.1, "status": "normal/reduced"}
        },
        "vertebral_heights": {
            "L1": 25.3, "L2": 26.1, "L3": 27.2, "L4": 28.5, "L5": 29.1
        }
    },
    "clinical_impression": "Summary of findings and recommendations",
    "recommendations": [
        "Follow-up recommendations",
        "Additional imaging if needed",
        "Clinical correlation suggestions"
    ]
}

Remember: Be conservative but accurate. If you see ANY pathological changes, degenerative findings, fractures, or abnormalities, classify as "abnormal". Only use "normal" for truly healthy spines.
"""
    
    async def analyze_xray(self, image_data: bytes, filename: str) -> Dict:
        """Analyze X-ray image using Gemini AI"""
        try:
            logger.info(f"Starting Gemini analysis for: {filename}")
            
            # Prepare image
            image = self._prepare_image_for_gemini(image_data)
            
            # Create prompt
            prompt = self._create_analysis_prompt()
            
            # Generate analysis
            response = self.model.generate_content([prompt, image])
            
            # Parse JSON response
            try:
                # Clean the response text
                response_text = response.text.strip()
                
                # Remove markdown code blocks if present
                if response_text.startswith("```json"):
                    response_text = response_text[7:]
                if response_text.endswith("```"):
                    response_text = response_text[:-3]
                
                analysis_result = json.loads(response_text.strip())
                
                # Validate required fields
                required_fields = ["overall_status", "confidence_score", "findings", "vertebrae_analysis"]
                for field in required_fields:
                    if field not in analysis_result:
                        raise ValueError(f"Missing required field: {field}")
                
                logger.info(f"Successfully analyzed {filename}: {analysis_result['overall_status']} ({analysis_result['confidence_score']:.2f})")
                
                return analysis_result
                
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse JSON response: {str(e)}")
                logger.error(f"Response text: {response.text}")
                
                # Return fallback analysis
                return self._create_fallback_analysis(filename)
                
        except Exception as e:
            logger.error(f"Error in Gemini analysis: {str(e)}")
            return self._create_fallback_analysis(filename, error=str(e))
    
    def _create_fallback_analysis(self, filename: str, error: str = None) -> Dict:
        """Create fallback analysis when Gemini fails"""
        return {
            "overall_status": "abnormal",
            "confidence_score": 0.3,
            "findings": [
                {
                    "vertebra": "overall",
                    "finding": f"Analysis incomplete due to technical issue: {error}" if error else "Unable to complete automated analysis",
                    "severity": "unknown",
                    "status": "abnormal"
                }
            ],
            "vertebrae_analysis": {
                f"L{i}": {
                    "status": "unknown",
                    "confidence": 0.3,
                    "findings": "Manual review required"
                } for i in range(1, 6)
            },
            "measurements": {
                "disc_heights": {
                    f"L{i}_L{i+1}": {"height_mm": 0.0, "status": "unknown"}
                    for i in range(1, 5)
                },
                "vertebral_heights": {f"L{i}": 0.0 for i in range(1, 6)}
            },
            "clinical_impression": "Automated analysis failed. Manual radiologist review required.",
            "recommendations": [
                "Manual review by qualified radiologist required",
                "Consider retaking image if quality issues present",
                "Clinical correlation with patient symptoms"
            ]
        }

def test_gemini_connection(api_key: str) -> bool:
    """Test if Gemini API connection works"""
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel("gemini-2.5-flash")
        
        # Simple test
        response = model.generate_content("Hello, can you analyze medical images?")
        
        if response and response.text:
            logger.info("Gemini API connection successful!")
            return True
        else:
            logger.error("Gemini API connection failed - no response")
            return False
            
    except Exception as e:
        logger.error(f"Gemini API connection failed: {str(e)}")
        return False