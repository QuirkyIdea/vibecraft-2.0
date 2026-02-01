"use client";

import { useState, useEffect, useRef } from "react";
import { motion, AnimatePresence } from "framer-motion";
import {
    Network,
    Send,
    Loader2,
    AlertTriangle,
    CheckCircle,
    XCircle,
    ZoomIn,
    ZoomOut,
    RotateCcw,
} from "lucide-react";
import PDFUpload from "@/components/PDFUpload";
import styles from "./KnowledgeGraphPanel.module.css";

interface ConceptNode {
    id: string;
    label: string;
    type: string;
    importance: string;
}

interface ConceptEdge {
    source: string;
    target: string;
    relationship: string;
    strength: string;
}

interface Cluster {
    name: string;
    nodes: string[];
    description: string;
}

interface GraphResult {
    topic_summary: string;
    nodes: ConceptNode[];
    edges: ConceptEdge[];
    central_concept: string;
    clusters: Cluster[];
    confidence: string;
    scope_disclaimer: string;
    unknowns: string[];
}

interface CrashLog {
    status: "CRASH";
    error_type: string;
    error_message: string;
    failed_stage: string;
    recommended_action: string;
}

interface NodePosition {
    x: number;
    y: number;
}

export default function KnowledgeGraphPanel() {
    const [topic, setTopic] = useState("");
    const [domain, setDomain] = useState("");
    const [depth, setDepth] = useState("medium");
    const [isGenerating, setIsGenerating] = useState(false);
    const [result, setResult] = useState<GraphResult | null>(null);
    const [error, setError] = useState<CrashLog | null>(null);
    const [selectedNode, setSelectedNode] = useState<ConceptNode | null>(null);
    const [zoom, setZoom] = useState(1);
    const [nodePositions, setNodePositions] = useState<Record<string, NodePosition>>({});

    const svgRef = useRef<SVGSVGElement>(null);

    // Calculate node positions when result changes
    useEffect(() => {
        if (result?.nodes) {
            const positions: Record<string, NodePosition> = {};
            const centerX = 400;
            const centerY = 300;
            const radius = 200;

            result.nodes.forEach((node, index) => {
                const angle = (2 * Math.PI * index) / result.nodes.length - Math.PI / 2;
                const r = node.importance === "HIGH" ? radius * 0.6 : radius;
                positions[node.id] = {
                    x: centerX + r * Math.cos(angle),
                    y: centerY + r * Math.sin(angle),
                };
            });

            setNodePositions(positions);
        }
    }, [result]);

    const generateGraph = async () => {
        if (!topic.trim() || topic.length < 10) return;

        setIsGenerating(true);
        setResult(null);
        setError(null);
        setSelectedNode(null);

        try {
            const response = await fetch("http://localhost:8000/api/knowledge/generate", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    topic: topic,
                    domain: domain || undefined,
                    depth: depth,
                }),
            });

            const data = await response.json();

            if (data.status === "CRASH") {
                setError(data as CrashLog);
            } else {
                setResult(data as GraphResult);
            }
        } catch (err) {
            setError({
                status: "CRASH",
                error_type: "UNKNOWN_FAILURE",
                error_message: "Failed to connect to the API. Is the backend running?",
                failed_stage: "retrieval",
                recommended_action: "system_debug",
            });
        } finally {
            setIsGenerating(false);
        }
    };

    const getNodeColor = (type: string) => {
        const colors: Record<string, string> = {
            concept: "#6366f1",
            technology: "#8b5cf6",
            method: "#22c55e",
            application: "#f59e0b",
            challenge: "#ef4444",
        };
        return colors[type] || "#6366f1";
    };

    const getNodeRadius = (importance: string) => {
        switch (importance) {
            case "HIGH": return 30;
            case "MEDIUM": return 22;
            case "LOW": return 16;
            default: return 22;
        }
    };

    const getEdgeColor = (strength: string) => {
        switch (strength) {
            case "STRONG": return "rgba(99, 102, 241, 0.8)";
            case "MODERATE": return "rgba(99, 102, 241, 0.5)";
            case "WEAK": return "rgba(99, 102, 241, 0.3)";
            default: return "rgba(99, 102, 241, 0.5)";
        }
    };

    const handleZoomIn = () => setZoom(prev => Math.min(prev + 0.2, 2));
    const handleZoomOut = () => setZoom(prev => Math.max(prev - 0.2, 0.5));
    const handleReset = () => setZoom(1);

    return (
        <div className={styles.container}>
            <div className={styles.header}>
                <div className={styles.headerIcon}>
                    <Network size={24} />
                </div>
                <div>
                    <h1>Knowledge Graph</h1>
                    <p>AI-powered concept extraction and relationship visualization</p>
                </div>
            </div>

            <div className={styles.mainContent}>
                <div className={styles.inputSection}>
                    <div className={styles.card}>
                        <h3>Build Knowledge Graph</h3>

                        {/* PDF Upload */}
                        <div className={styles.inputGroup}>
                            <label className="label">Upload PDF (optional)</label>
                            <PDFUpload
                                onTextExtracted={(text) => {
                                    setTopic(prev => prev + (prev ? "\n\n" : "") + text);
                                }}
                                compact
                            />
                        </div>

                        <div className={styles.divider}>
                            <span>or enter topic manually</span>
                        </div>

                        <div className={styles.inputGroup}>
                            <label className="label">Topic *</label>
                            <textarea
                                className={`input ${styles.topicInput}`}
                                placeholder="Describe the topic you want to map. Be specific about the concepts and domain."
                                value={topic}
                                onChange={(e) => setTopic(e.target.value)}
                            />
                            <span className={styles.charCount}>{topic.length} characters (min 10)</span>
                        </div>

                        <div className={styles.inputRow}>
                            <div className={styles.inputGroup}>
                                <label className="label">Domain</label>
                                <input
                                    className="input"
                                    placeholder="e.g., AI, Biotech"
                                    value={domain}
                                    onChange={(e) => setDomain(e.target.value)}
                                />
                            </div>
                            <div className={styles.inputGroup}>
                                <label className="label">Graph Depth</label>
                                <select
                                    className="input"
                                    value={depth}
                                    onChange={(e) => setDepth(e.target.value)}
                                >
                                    <option value="shallow">Shallow (6 nodes)</option>
                                    <option value="medium">Medium (10 nodes)</option>
                                    <option value="deep">Deep (15 nodes)</option>
                                </select>
                            </div>
                        </div>

                        <button
                            className={`btn btn-primary ${styles.generateBtn}`}
                            onClick={generateGraph}
                            disabled={isGenerating || topic.length < 10}
                        >
                            {isGenerating ? (
                                <>
                                    <Loader2 size={18} className={styles.spinner} />
                                    Generating...
                                </>
                            ) : (
                                <>
                                    <Network size={18} />
                                    Generate Graph
                                </>
                            )}
                        </button>
                    </div>

                    {/* Legend */}
                    {result && (
                        <div className={styles.card}>
                            <h4>Node Types</h4>
                            <div className={styles.legend}>
                                <div className={styles.legendItem}>
                                    <span className={styles.legendDot} style={{ background: "#6366f1" }} />
                                    <span>Concept</span>
                                </div>
                                <div className={styles.legendItem}>
                                    <span className={styles.legendDot} style={{ background: "#8b5cf6" }} />
                                    <span>Technology</span>
                                </div>
                                <div className={styles.legendItem}>
                                    <span className={styles.legendDot} style={{ background: "#22c55e" }} />
                                    <span>Method</span>
                                </div>
                                <div className={styles.legendItem}>
                                    <span className={styles.legendDot} style={{ background: "#f59e0b" }} />
                                    <span>Application</span>
                                </div>
                                <div className={styles.legendItem}>
                                    <span className={styles.legendDot} style={{ background: "#ef4444" }} />
                                    <span>Challenge</span>
                                </div>
                            </div>
                            <div className={styles.legendSection}>
                                <h5>Importance</h5>
                                <div className={styles.importanceLegend}>
                                    <span>Large = High</span>
                                    <span>Medium = Medium</span>
                                    <span>Small = Low</span>
                                </div>
                            </div>
                        </div>
                    )}

                    {/* Selected Node Details */}
                    {selectedNode && (
                        <motion.div
                            initial={{ opacity: 0, y: 10 }}
                            animate={{ opacity: 1, y: 0 }}
                            className={`${styles.card} ${styles.selectedCard}`}
                        >
                            <h4>Selected Node</h4>
                            <div className={styles.nodeDetails}>
                                <div className={styles.nodeLabel} style={{ borderColor: getNodeColor(selectedNode.type) }}>
                                    {selectedNode.label}
                                </div>
                                <div className={styles.nodeInfo}>
                                    <span>Type: <code>{selectedNode.type}</code></span>
                                    <span>Importance: <code>{selectedNode.importance}</code></span>
                                </div>
                                {result && (
                                    <div className={styles.connections}>
                                        <span>Connections:</span>
                                        <ul>
                                            {result.edges
                                                .filter(e => e.source === selectedNode.id || e.target === selectedNode.id)
                                                .map((e, i) => {
                                                    const otherId = e.source === selectedNode.id ? e.target : e.source;
                                                    const otherNode = result.nodes.find(n => n.id === otherId);
                                                    return (
                                                        <li key={i}>
                                                            {e.relationship} → {otherNode?.label || otherId}
                                                        </li>
                                                    );
                                                })}
                                        </ul>
                                    </div>
                                )}
                            </div>
                        </motion.div>
                    )}
                </div>

                <div className={styles.graphSection}>
                    <AnimatePresence mode="wait">
                        {isGenerating && (
                            <motion.div
                                key="loading"
                                initial={{ opacity: 0 }}
                                animate={{ opacity: 1 }}
                                exit={{ opacity: 0 }}
                                className={styles.loadingState}
                            >
                                <motion.div
                                    className={styles.loadingGraph}
                                    animate={{ rotate: 360 }}
                                    transition={{ duration: 3, repeat: Infinity, ease: "linear" }}
                                >
                                    <Network size={64} />
                                </motion.div>
                                <p>Extracting concepts and relationships...</p>
                            </motion.div>
                        )}

                        {error && !isGenerating && (
                            <motion.div
                                key="error"
                                initial={{ opacity: 0, y: 20 }}
                                animate={{ opacity: 1, y: 0 }}
                                exit={{ opacity: 0 }}
                                className={`${styles.card} ${styles.errorCard}`}
                            >
                                <div className={styles.errorHeader}>
                                    <XCircle size={24} />
                                    <h3>Generation Failed</h3>
                                </div>
                                <p>{error.error_message}</p>
                            </motion.div>
                        )}

                        {result && !isGenerating && (
                            <motion.div
                                key="result"
                                initial={{ opacity: 0 }}
                                animate={{ opacity: 1 }}
                                exit={{ opacity: 0 }}
                                className={styles.graphContainer}
                            >
                                {/* Graph Header */}
                                <div className={styles.graphHeader}>
                                    <div>
                                        <h3>
                                            <CheckCircle size={18} className={styles.successIcon} />
                                            Knowledge Graph Generated
                                        </h3>
                                        <p>{result.topic_summary}</p>
                                    </div>
                                    <div className={styles.graphControls}>
                                        <button onClick={handleZoomOut} className={styles.controlBtn}>
                                            <ZoomOut size={18} />
                                        </button>
                                        <span>{Math.round(zoom * 100)}%</span>
                                        <button onClick={handleZoomIn} className={styles.controlBtn}>
                                            <ZoomIn size={18} />
                                        </button>
                                        <button onClick={handleReset} className={styles.controlBtn}>
                                            <RotateCcw size={18} />
                                        </button>
                                    </div>
                                </div>

                                {/* SVG Graph */}
                                <div className={styles.graphViewer}>
                                    <svg
                                        ref={svgRef}
                                        viewBox="0 0 800 600"
                                        className={styles.graphSvg}
                                        style={{ transform: `scale(${zoom})` }}
                                    >
                                        {/* Edges */}
                                        {result.edges.map((edge, i) => {
                                            const sourcePos = nodePositions[edge.source];
                                            const targetPos = nodePositions[edge.target];
                                            if (!sourcePos || !targetPos) return null;

                                            return (
                                                <g key={`edge-${i}`}>
                                                    <line
                                                        x1={sourcePos.x}
                                                        y1={sourcePos.y}
                                                        x2={targetPos.x}
                                                        y2={targetPos.y}
                                                        stroke={getEdgeColor(edge.strength)}
                                                        strokeWidth={edge.strength === "STRONG" ? 3 : edge.strength === "MODERATE" ? 2 : 1}
                                                    />
                                                    {/* Relationship label */}
                                                    <text
                                                        x={(sourcePos.x + targetPos.x) / 2}
                                                        y={(sourcePos.y + targetPos.y) / 2 - 5}
                                                        fill="var(--text-muted)"
                                                        fontSize="10"
                                                        textAnchor="middle"
                                                    >
                                                        {edge.relationship}
                                                    </text>
                                                </g>
                                            );
                                        })}

                                        {/* Nodes */}
                                        {result.nodes.map((node) => {
                                            const pos = nodePositions[node.id];
                                            if (!pos) return null;
                                            const radius = getNodeRadius(node.importance);
                                            const isSelected = selectedNode?.id === node.id;

                                            return (
                                                <g
                                                    key={node.id}
                                                    onClick={() => setSelectedNode(isSelected ? null : node)}
                                                    style={{ cursor: "pointer" }}
                                                >
                                                    {/* Glow effect for selected */}
                                                    {isSelected && (
                                                        <circle
                                                            cx={pos.x}
                                                            cy={pos.y}
                                                            r={radius + 8}
                                                            fill="none"
                                                            stroke={getNodeColor(node.type)}
                                                            strokeWidth="2"
                                                            opacity="0.5"
                                                        />
                                                    )}
                                                    <circle
                                                        cx={pos.x}
                                                        cy={pos.y}
                                                        r={radius}
                                                        fill={getNodeColor(node.type)}
                                                        opacity="0.9"
                                                    />
                                                    <text
                                                        x={pos.x}
                                                        y={pos.y + radius + 15}
                                                        fill="var(--text-primary)"
                                                        fontSize="11"
                                                        textAnchor="middle"
                                                        fontWeight="500"
                                                    >
                                                        {node.label.length > 15
                                                            ? node.label.substring(0, 15) + "..."
                                                            : node.label}
                                                    </text>
                                                </g>
                                            );
                                        })}
                                    </svg>
                                </div>

                                {/* Stats */}
                                <div className={styles.graphStats}>
                                    <div className={styles.statItem}>
                                        <span className={styles.statValue}>{result.nodes.length}</span>
                                        <span className={styles.statLabel}>Nodes</span>
                                    </div>
                                    <div className={styles.statItem}>
                                        <span className={styles.statValue}>{result.edges.length}</span>
                                        <span className={styles.statLabel}>Edges</span>
                                    </div>
                                    <div className={styles.statItem}>
                                        <span className={styles.statValue}>{result.clusters.length}</span>
                                        <span className={styles.statLabel}>Clusters</span>
                                    </div>
                                    <div className={styles.statItem}>
                                        <span className={styles.statValue}>{result.central_concept}</span>
                                        <span className={styles.statLabel}>Central Concept</span>
                                    </div>
                                </div>

                                {/* Clusters */}
                                {result.clusters.length > 0 && (
                                    <div className={styles.clustersSection}>
                                        <h4>Concept Clusters</h4>
                                        <div className={styles.clusterList}>
                                            {result.clusters.map((cluster, i) => (
                                                <div key={i} className={styles.clusterItem}>
                                                    <span className={styles.clusterName}>{cluster.name}</span>
                                                    <span className={styles.clusterDesc}>{cluster.description}</span>
                                                    <div className={styles.clusterNodes}>
                                                        {cluster.nodes.map((nodeId, j) => {
                                                            const node = result.nodes.find(n => n.id === nodeId);
                                                            return (
                                                                <span key={j} className={styles.clusterNode}>
                                                                    {node?.label || nodeId}
                                                                </span>
                                                            );
                                                        })}
                                                    </div>
                                                </div>
                                            ))}
                                        </div>
                                    </div>
                                )}

                                {/* Disclaimer */}
                                <div className={`${styles.card} ${styles.disclaimerBox}`}>
                                    <AlertTriangle size={16} />
                                    <p>{result.scope_disclaimer}</p>
                                </div>
                            </motion.div>
                        )}

                        {!isGenerating && !result && !error && (
                            <motion.div
                                key="empty"
                                initial={{ opacity: 0 }}
                                animate={{ opacity: 1 }}
                                className={styles.emptyState}
                            >
                                <Network size={64} className={styles.emptyIcon} />
                                <h3>Ready to Map Knowledge</h3>
                                <p>Enter a topic to generate a concept graph with relationships</p>
                            </motion.div>
                        )}
                    </AnimatePresence>
                </div>
            </div>
        </div>
    );
}
