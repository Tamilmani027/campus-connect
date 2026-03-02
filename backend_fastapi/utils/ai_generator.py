import google.generativeai as genai
import json
import logging
from ..config import settings

logger = logging.getLogger(__name__)

def configure_genai():
    if not settings.GEMINI_API_KEY:
        logger.warning("GEMINI_API_KEY is not set. AI features will not work.")
        return False
    genai.configure(api_key=settings.GEMINI_API_KEY)
    return True

def generate_study_plan_content(topic: str, duration_days: int, difficulty: str = "Beginner") -> dict:
    """
    Generates a structured study plan using Gemini AI.
    Returns a dictionary matching the StudyPlan schema structure.
    """
    if not configure_genai():
        raise Exception("API Key not configured")

    # Use models that are confirmed to work with generateContent
    model_names = [
        'models/gemini-flash-latest',      # Latest flash (alias)
        'models/gemini-pro-latest',        # Latest pro (alias)
        'models/gemini-2.0-flash-exp',     # Experimental flash
        'models/gemini-exp-1206',          # Experimental model
    ]
    
    last_error = None
    for model_name in model_names:
        try:
            model = genai.GenerativeModel(model_name)
            
            prompt = f"""
    Create a detailed {duration_days}-day structured learning roadmap for "{topic}" at a "{difficulty}" level.
    This should be a professional study plan with clear daily learning objectives.
    
    The response MUST be valid JSON with the following structure:
    {{
        "title": "Professional title for the roadmap (e.g., '{topic} Mastery Roadmap')",
        "description": "Brief overview of what will be learned and the progression",
        "tasks": [
            {{
                "day": 1,
                "title": "Clear learning objective for the day",
                "description": "Detailed explanation of concepts to study and practice",
                "link": "https://example.com/relevant-resource" 
            }},
            ...
        ]
    }}
    
    Guidelines:
    - Focus on structured learning progression from fundamentals to advanced
    - Each day should build upon previous days
    - Include theory, practice, and real-world application
    - Ensure there is at least one task for every day from 1 to {duration_days}
    - For the 'link' field, provide high-quality reference URLs (official docs, tutorials, or courses)
    - Use professional, educational language
    - Avoid gamification terms like "challenge" or "quest"
    
    Do not wrap the JSON in markdown code blocks. Just return the raw JSON.
    """
            
            response = model.generate_content(prompt)
            text = response.text.strip()
            # Cleanup in case the model wraps code in ```json ... ```
            if text.startswith("```"):
                text = text.replace("```json", "").replace("```", "").strip()
                
            data = json.loads(text)
            logger.info(f"Successfully used model: {model_name}")
            return data
            
        except Exception as e:
            last_error = e
            logger.warning(f"Model {model_name} failed: {e}")
            continue
    
    # If all models failed, raise the last error
    logger.error(f"All models failed. Last error: {last_error}")
    raise last_error
