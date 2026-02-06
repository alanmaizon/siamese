import { GoogleGenAI, Type, Schema } from "@google/genai";
import { FileArtifact, IncidentReport } from '../types';
import { SYSTEM_INSTRUCTION } from '../constants';

const responseSchema: Schema = {
  type: Type.OBJECT,
  properties: {
    summary: { type: Type.STRING, description: "One-paragraph plain-English explanation of what happened" },
    timeline: { type: Type.ARRAY, items: { type: Type.STRING }, description: "Timestamped or ordered sequence of key events" },
    root_causes: { type: Type.ARRAY, items: { type: Type.STRING }, description: "The probable root causes" },
    evidence: { type: Type.ARRAY, items: { type: Type.STRING }, description: "Concrete observations taken directly from logs" },
    mitigations: { type: Type.ARRAY, items: { type: Type.STRING }, description: "Immediate actions taken or recommended" },
    follow_ups: { type: Type.ARRAY, items: { type: Type.STRING }, description: "Long-term fixes and prevention items" },
    confidence: { type: Type.NUMBER, description: "Confidence score between 0.0 and 1.0" },
  },
  // Added mitigations and follow_ups to required to ensure model returns them
  required: ["summary", "timeline", "root_causes", "evidence", "mitigations", "follow_ups", "confidence"],
};

export const analyzeIncident = async (
  apiKey: string,
  modelName: string,
  question: string,
  files: FileArtifact[]
): Promise<{ text: string; json?: IncidentReport }> => {
  
  if (!apiKey) {
    throw new Error("API Key is missing. Please check your environment configuration.");
  }

  const ai = new GoogleGenAI({ apiKey });

  // Build the prompt context from files
  let fileContext = "";
  if (files.length > 0) {
    fileContext = files.map(f => `\n# file: ${f.name}\n\`\`\`\n${f.content}\n\`\`\``).join("\n");
  }

  const prompt = `
Context Artifacts:
${fileContext}

User Question:
${question}
  `.trim();

  try {
    const response = await ai.models.generateContent({
      model: modelName,
      contents: prompt,
      config: {
        systemInstruction: SYSTEM_INSTRUCTION,
        responseMimeType: "application/json",
        responseSchema: responseSchema,
      },
    });

    const text = response.text || "{}";
    let json: IncidentReport | undefined;

    try {
      json = JSON.parse(text);
    } catch (e) {
      console.warn("Failed to parse JSON response", e);
    }

    return { text, json };
  } catch (error: any) {
    console.error("Gemini API Error:", error);
    throw new Error(error.message || "An error occurred during analysis.");
  }
};
