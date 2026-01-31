export const AGENT_TYPES = {
    RESEARCH: { id: 'research', name: 'Research Supervisor', color: 'blue' },
    PATENT: { id: 'patent', name: 'Patent Drafter', color: 'purple' },
    NOVELTY: { id: 'novelty', name: 'Novelty Detector', color: 'red' },
    COMPLIANCE: { id: 'compliance', name: 'Risk & Compliance', color: 'orange' },
    KNOWLEDGE: { id: 'knowledge', name: 'Knowledge Graph', color: 'emerald' }
};

export const MOCK_ACTIONS = [
    { type: 'research', action: 'Synthesizing 15 new papers', status: 'processing' },
    { type: 'patent', action: 'Drafting Claim #4 (Method)', status: 'active' },
    { type: 'novelty', action: 'Found 98% similarity with US Patent 2024/012345', status: 'alert' },
    { type: 'knowledge', action: 'Linking "Transformer" to "Attention Mechanism"', status: 'success' },
    { type: 'compliance', action: 'Checking export control regulations', status: 'processing' },
    { type: 'research', action: 'Generating literature review summary', status: 'success' },
    { type: 'novelty', action: 'Novelty check passed for Embodiment 1', status: 'success' }
];

export const generateMockActivity = () => {
    const randomAction = MOCK_ACTIONS[Math.floor(Math.random() * MOCK_ACTIONS.length)];
    const agent = Object.values(AGENT_TYPES).find(a => a.id === randomAction.type);

    return {
        id: Date.now(),
        agent: agent.name,
        action: randomAction.action,
        type: randomAction.status,
        timestamp: new Date().toLocaleTimeString(),
        agentId: agent.id
    };
};
