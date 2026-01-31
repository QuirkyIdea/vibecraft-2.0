const DEFAULT_BASE_URL = 'http://localhost:8000';

const getApiBaseUrl = () => {
    return import.meta.env.VITE_API_BASE_URL || DEFAULT_BASE_URL;
};

export const generateDraft = async ({ projectId, documentId, text, mode = 'patent' }) => {
    const baseUrl = getApiBaseUrl();
    const response = await fetch(`${baseUrl}/api/v1/drafting`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            project_id: projectId,
            document_id: documentId || null,
            text: text || null,
            mode
        })
    });

    if (!response.ok) {
        let message = 'Drafting request failed.';
        try {
            const errorPayload = await response.json();
            message = errorPayload?.detail || errorPayload?.error || message;
        } catch (error) {
            // Ignore JSON parse errors and keep fallback message.
        }
        return { success: false, error: message };
    }

    const payload = await response.json();
    return payload;
};
