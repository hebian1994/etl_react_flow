import { AppBar, Toolbar } from '@mui/material';
import React from 'react';
import FlowToolbarControls from '../../components/flow/FlowToolbarControls';
import NodeTypeSelector from '../../components/nodes/NodeTypeSelector';

const TopToolbar = ({
    setShowBox2,
    setShowBox4,
    handleSave,
    flowName,
    setFlowName,
}: {
    setShowBox2: React.Dispatch<React.SetStateAction<boolean>>;
    setShowBox4: React.Dispatch<React.SetStateAction<boolean>>;
    handleSave: () => void;
    flowName: string;
    setFlowName: React.Dispatch<React.SetStateAction<string>>;
}) => {
    return (
        <AppBar position="static" color="default" elevation={1} sx={{ zIndex: 10 }}>
            <Toolbar
                variant="dense"
                sx={{ flexDirection: 'column', alignItems: 'stretch', p: 1, gap: 1 }}
            >
                <FlowToolbarControls
                    flowName={flowName}
                    setFlowName={setFlowName}
                    setShowBox2={setShowBox2}
                    setShowBox4={setShowBox4}
                    handleSave={handleSave}
                />
                <NodeTypeSelector />
            </Toolbar>
        </AppBar>
    );
};

export default TopToolbar;
