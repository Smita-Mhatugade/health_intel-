import type { DiseaseConfig } from "@/lib/api";

export interface ParsedMessage {
  category: string | null;
  parameters: Record<string, any>;
  symptoms: string[];
  rationale: string;
}

const KEYWORDS: Record<string, string[]> = {
  heart_failure: [
    "heart failure", "ejection fraction", "shortness of breath", "swelling", "fatigue",
    "creatinine", "platelets", "anaemia", "anemia",
  ],
  heart_disease: [
    "heart disease", "chest pain", "angina", "cholesterol", "blood pressure",
    "trestbps", "thalach",
  ],
  parkinsons: ["parkinson", "tremor", "voice", "vocal", "jitter", "shimmer"],
  alzheimer: ["alzheimer", "memory loss", "dementia", "cognitive"],
  eye_disease: ["eye", "vision", "retina", "cataract", "glaucoma", "blurred"],
  symptom_prediction: ["symptom", "fever", "cough", "headache", "rash"],
};

export function parseUserMessage(message: string, diseases: DiseaseConfig[] = []): ParsedMessage {
  const text = message.toLowerCase();
  let bestCategory: string | null = null;
  let bestScore = 0;
  for (const [cat, kws] of Object.entries(KEYWORDS)) {
    const score = kws.reduce((acc, kw) => (text.includes(kw) ? acc + 1 : acc), 0);
    if (score > bestScore) {
      bestScore = score;
      bestCategory = cat;
    }
  }

  // If a known disease id matches, prefer it
  for (const d of diseases) {
    const id = (d.id || d.category || d.name || "").toLowerCase();
    if (id && text.includes(id.replace(/_/g, " "))) {
      bestCategory = id;
      break;
    }
  }

  const parameters: Record<string, any> = {};

  const ageMatch = text.match(/(?:age[^\d]{0,5})(\d{1,3})/i) || text.match(/\b(\d{1,3})\s*(?:y(?:ear)?s?[- ]?old|yo)\b/);
  if (ageMatch) parameters.age = Number(ageMatch[1]);

  if (/\bmale\b/.test(text)) parameters.sex = 1;
  else if (/\bfemale\b/.test(text)) parameters.sex = 0;

  if (/\bsmok(?:er|ing|es)\b/.test(text) && !/non[- ]?smok/.test(text)) parameters.smoking = 1;
  else if (/non[- ]?smok|don't smoke|do not smoke/.test(text)) parameters.smoking = 0;

  if (/\bdiabet/.test(text)) parameters.diabetes = 1;
  if (/(high blood pressure|hypertension)/.test(text)) parameters.high_blood_pressure = 1;
  if (/anaem|anem/.test(text)) parameters.anaemia = 1;

  const efMatch = text.match(/ejection fraction[^\d]{0,10}(\d{1,3})/);
  if (efMatch) parameters.ejection_fraction = Number(efMatch[1]);

  // Extract symptoms by simple noun list — common ones
  const commonSymptoms = [
    "fatigue","cough","fever","headache","nausea","chest pain","shortness of breath",
    "dizziness","vomiting","rash","sore throat","runny nose","weakness","sweating",
  ];
  const symptoms = commonSymptoms.filter((s) => text.includes(s));

  return {
    category: bestCategory,
    parameters,
    symptoms,
    rationale: bestCategory
      ? `Detected likely category: ${bestCategory.replace(/_/g, " ")} (${bestScore} keyword matches).`
      : "No clear category detected — please pick one manually.",
  };
}
