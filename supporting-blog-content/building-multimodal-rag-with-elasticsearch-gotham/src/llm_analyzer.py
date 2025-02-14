import os
from openai import OpenAI
import logging
from dotenv import load_dotenv

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class LLMAnalyzer:
    """Evidence analyzer using GPT-4"""
    
    def __init__(self):
        load_dotenv()
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    
    def analyze_evidence(self, evidence_results):
        """
        Analyzes multimodal search results and generates a report
        
        Args:
            evidence_results: Dict with results by modality
            {
                'vision': [...],
                'audio': [...],
                'text': [...],
                'depth': [...]
            }
        """
        # Format evidence for the prompt
        evidence_summary = self._format_evidence(evidence_results)

        # final prompt
        prompt = f"""
You are a highly experienced forensic detective specializing in multimodal evidence analysis. Your task is to analyze the collected evidence (audio, images, text, depth maps) and conclusively determine the **prime suspect** responsible for the Gotham Central Bank case.

---

### **Collected Evidence:**
{evidence_summary}

### **Task:**
1. **Analyze all the evidence** and identify cross-modal connections.
2. **Determine the exact identity of the criminal** based on behavioral patterns, visual/auditory/textual clues, and symbolic markers.
3. **Justify your conclusion** by explaining why this suspect is definitively responsible.
4. **Assign a confidence score (0-100%)** to your conclusion.

---

### **Final Output Format (Strictly Follow This Format):**
- **Prime Suspect:** [Full Name or Alias]
- **Evidence Supporting Conclusion:** [Detailed breakdown of visual, auditory, textual, and behavioral evidence]
- **Behavioral Patterns:** [Key actions, motives, and criminal signature]
- **Confidence Level:** [0-100%]
- **Next Steps (if any):** [What additional evidence would further confirm the identity? If none, state "No further evidence required."]

If there is **insufficient evidence**, specify exactly what is missing and suggest what additional data would be needed for a conclusive identification.

This report must be **direct and definitive**—avoid speculation and provide a final, actionable determination of the suspect's identity.
"""
        try:
            response = self.client.chat.completions.create(
                model="gpt-4-turbo-preview",
                messages=[
                    {
                        "role": "system",
                        "content": "You are a forensic detective specialized in multimodal evidence analysis."
                    },
                    {"role": "user", "content": prompt}
                ],
                temperature=0.2,
                max_tokens=1000
            )
            
            report = response.choices[0].message.content
            logger.info("\n📋 Forensic Report Generated:")
            logger.info("=" * 50)
            logger.info(report)
            logger.info("=" * 50)
            
            return report
            
        except Exception as e:
            logger.error(f"Error generating report: {str(e)}")
            return None
    
    def _format_evidence(self, evidence_results):
        """Formats evidence for the prompt"""
        formatted = []
        
        for modality, results in evidence_results.items():
            formatted.append(f"\n{modality.upper()}:")
            for i, result in enumerate(results, 1):
                description = result.get('description', 'No description')
                similarity = result.get('score', 0)
                formatted.append(f"{i}. {description} (Similarity: {similarity:.2f})")
        
        return "\n".join(formatted)

    def analyze_cross_modal_connections(self, results_a, modality_a, results_b, modality_b):
        """Analyzes specific connections between two different modalities"""
        prompt = f"""Analyze the relationship between the following evidence from different modalities:

{modality_a.upper()}:
{self._format_evidence({modality_a: results_a})}

{modality_b.upper()}:
{self._format_evidence({modality_b: results_b})}

Please identify:
1. Direct connections between the evidence
2. Patterns suggesting the same suspect
3. Inconsistencies or contradictions
4. Correlation strength (0-100%)

"""

        try:
            response = self.client.chat.completions.create(
                model="gpt-4-turbo-preview",
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert in forensic analysis of multimodal evidence."
                    },
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=500
            )
            
            analysis = response.choices[0].message.content
            logger.info(f"\n🔍 Cross-Modal Analysis ({modality_a} x {modality_b}):")
            logger.info(analysis)
            
            return analysis
            
        except Exception as e:
            logger.error(f"Error: in cross-modal analysis: {str(e)}")
            return None