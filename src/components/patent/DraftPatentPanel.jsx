import { useEffect, useRef, useState } from 'react';
import { useWorkflow } from '../../context/WorkflowContext';
import { generateDraft } from '../../api/drafting';
import styles from './DraftPatentPanel.module.css';

const DraftPatentPanel = () => {
    const { activeProject, draftingTarget, clearDraftingTarget } = useWorkflow();
    const panelRef = useRef(null);
    const [documentId, setDocumentId] = useState('');
    const [inputText, setInputText] = useState('');
    const [status, setStatus] = useState({
        loading: false,
        error: null,
        output: null,
        sections: []
    });

    useEffect(() => {
        if (draftingTarget?.mode === 'patent') {
            panelRef.current?.scrollIntoView({ behavior: 'smooth', block: 'start' });
            clearDraftingTarget();
        }
    }, [draftingTarget, clearDraftingTarget]);

    const handleGenerate = async () => {
        if (!activeProject?.id) {
            setStatus(prev => ({ ...prev, error: 'Select an active project before drafting.' }));
            return;
        }

        setStatus({ loading: true, error: null, output: null, sections: [] });
        const response = await generateDraft({
            projectId: activeProject.id,
            documentId: documentId.trim() || undefined,
            text: inputText.trim() || undefined,
            mode: 'patent'
        });

        if (!response?.success) {
            setStatus({
                loading: false,
                error: response?.error || 'Draft generation failed.',
                output: null,
                sections: []
            });
            return;
        }

        setStatus({
            loading: false,
            error: null,
            output: response.output,
            sections: response.sections || []
        });
    };

    const isBusy = status.loading;

    return (
        <div ref={panelRef} className={styles.panel}>
            <div className={styles.header}>
                <div>
                    <h3 className={styles.title}>Draft Patent</h3>
                    <p className={styles.subtitle}>
                        Generate a structured draft using draft_patentai with project-aware inputs.
                    </p>
                </div>
                <div className={styles.meta}>
                    <span>Project ID: {activeProject?.id ?? '—'}</span>
                </div>
            </div>

            <div className={styles.formGrid}>
                <label className={styles.field}>
                    <span className={styles.label}>Document ID (optional)</span>
                    <input
                        className={styles.input}
                        type="text"
                        value={documentId}
                        placeholder={`project_${activeProject?.id ?? 'id'}`}
                        onChange={(event) => setDocumentId(event.target.value)}
                    />
                </label>

                <label className={styles.field}>
                    <span className={styles.label}>Drafting Input</span>
                    <textarea
                        className={styles.textarea}
                        value={inputText}
                        placeholder="Paste your invention description, system outline, or notes. Leave empty to use stored project text."
                        onChange={(event) => setInputText(event.target.value)}
                    />
                </label>
            </div>

            <div className={styles.actions}>
                <button
                    type="button"
                    className={styles.primaryButton}
                    onClick={handleGenerate}
                    disabled={isBusy}
                >
                    {isBusy ? 'Drafting…' : 'Generate Draft'}
                </button>
                <span className={styles.helper}>
                    Uses extracted text or idea text if input is left blank.
                </span>
            </div>

            {status.error && (
                <div className={styles.error}>
                    {status.error}
                </div>
            )}

            {status.output && (
                <div className={styles.output}>
                    <div className={styles.outputHeader}>Draft Output</div>
                    <pre className={styles.outputText}>{status.output}</pre>
                </div>
            )}

            {status.sections?.length > 0 && (
                <div className={styles.sections}>
                    <div className={styles.outputHeader}>Structured Sections</div>
                    <div className={styles.sectionGrid}>
                        {status.sections.map((section) => (
                            <div key={section.heading} className={styles.sectionCard}>
                                <div className={styles.sectionTitle}>{section.heading}</div>
                                <p className={styles.sectionBody}>{section.content}</p>
                            </div>
                        ))}
                    </div>
                </div>
            )}
        </div>
    );
};

export default DraftPatentPanel;
