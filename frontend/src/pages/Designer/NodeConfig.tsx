import React from "react";
import {
    Box,
    Typography,
    IconButton,
    Paper,
    Divider,
    Button,
} from "@mui/material";
import CloseIcon from "@mui/icons-material/Close";
import { NodeConfigComponentMap } from "../../components/NodeConfigMap";

interface Props {
    selectedNode: { data: { type: string } } | null;
    configForm: any;
    setConfigForm: React.Dispatch<React.SetStateAction<any>>;
    setSelectedNode: (node: null) => void;
    setShowBox2: (show: boolean) => void;
    handleSaveConfig: () => void;
}

const NodeConfig: React.FC<Props> = ({
    selectedNode,
    configForm,
    setConfigForm,
    setSelectedNode,
    setShowBox2,
    handleSaveConfig,
}) => {
    const nodeType = selectedNode?.data.type ?? "";
    const ConfigComponent = NodeConfigComponentMap[nodeType];

    const handleFieldChange = (key: string, value: string) => {
        setConfigForm((prev: any) => ({
            ...prev,
            [key]: value,
        }));
    };

    return (
        <Paper
            elevation={3}
            sx={{
                p: 3,
                borderRadius: 3,
                width: "100%",
                height: "100%",
                display: "flex",
                flexDirection: "column",
                boxSizing: "border-box",
                overflow: "hidden",
            }}
        >
            {/* Header */}
            <Box sx={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                <Typography variant="h6">节点配置：{nodeType}</Typography>
                <IconButton
                    aria-label="关闭配置栏"
                    onClick={() => {
                        setSelectedNode(null);
                        setShowBox2(false);
                    }}
                >
                    <CloseIcon />
                </IconButton>
            </Box>

            <Divider sx={{ my: 2 }} />

            <Box sx={{ flex: 1, overflowY: "auto", pr: 1 }}>
                {ConfigComponent ? (
                    <Box sx={{ flex: 1, overflowY: "auto", pr: 1 }}>
                        <Typography><br /></Typography>
                        <ConfigComponent config={configForm} onChange={handleFieldChange} />
                    </Box>
                ) : (
                    <Typography>该节点不需要配置。</Typography>
                )}
            </Box>

            <Box sx={{ mt: 2 }}>
                <Button variant="contained" color="primary" fullWidth onClick={handleSaveConfig}>
                    保存配置
                </Button>
            </Box>
        </Paper>
    );
};

export default NodeConfig;
