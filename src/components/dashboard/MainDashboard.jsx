/**
 * Inventix AI - Main Dashboard
 * 
 * REFACTORED: Shows relevant components based on project type.
 * Removed component spam - now context-aware.
 */
import { motion } from 'framer-motion';
import { useWorkflow } from '../../context/WorkflowContext';
import CommandCenter from '../CommandCenter';
import ResearchStudio from '../ResearchStudio';
import PatentStudio from '../PatentStudio';
import PageTransition from '../PageTransition';

const MainDashboard = () => {
    const { activeProject } = useWorkflow();

    return (
        <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ duration: 0.5 }}
            className="pb-20"
        >
            {/* Command Center - Always shown */}
            <PageTransition>
                <CommandCenter key={activeProject?.id} />
            </PageTransition>

            {/* Research Studio - Only for RESEARCH projects */}
            {(!activeProject || activeProject.type === 'RESEARCH') && (
                <PageTransition>
                    <ResearchStudio />
                </PageTransition>
            )}

            {/* Patent Studio - Only for PATENT projects */}
            {(!activeProject || activeProject.type === 'PATENT') && (
                <PageTransition>
                    <PatentStudio />
                </PageTransition>
            )}
        </motion.div>
    );
};

export default MainDashboard;
