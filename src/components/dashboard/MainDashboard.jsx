import { motion } from 'framer-motion';
import { useWorkflow } from '../../context/WorkflowContext';
import CommandCenter from '../CommandCenter';
import PlatformOverview from '../PlatformOverview';
import ResearchStudio from '../ResearchStudio';
import PatentStudio from '../PatentStudio';
import IntelligenceEngine from '../IntelligenceEngine';
import Analytics from '../Analytics';
import Playground from '../Playground';
import PageTransition from '../PageTransition';

const MainDashboard = () => {
    const { activeProject } = useWorkflow();
    // Temporary: Ensure child components have access to domain context if they rely on it.
    // Ideally, we refactor children to use activeProject.domain directly.

    return (
        <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ duration: 1 }}
            className="pb-20"
        >
            <PageTransition>
                {/* We pass the domain key to force re-render on switch */}
                <CommandCenter key={activeProject?.id} />
            </PageTransition>

            <PageTransition>
                <PlatformOverview />
            </PageTransition>

            <div id="studio">
                <PageTransition>
                    <ResearchStudio />
                </PageTransition>
                <PageTransition>
                    <PatentStudio />
                </PageTransition>
            </div>

            <PageTransition>
                <IntelligenceEngine />
            </PageTransition>

            <PageTransition>
                <Analytics />
            </PageTransition>

            <PageTransition>
                <Playground />
            </PageTransition>
        </motion.div>
    );
};

export default MainDashboard;
