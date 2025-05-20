import React from "react";
import {
    Box,
    Typography,
    IconButton,
    Paper,
    Divider,
    Button,
    FormControl,
    InputLabel,
    Select,
    MenuItem,
    Grid,
} from "@mui/material";
import CloseIcon from "@mui/icons-material/Close";
import { NodeConfigComponentMap } from "../../components/NodeConfigMap";

interface Props {
    selectedNode: { data: { type: string } } | null;
    setSelectedNode: (node: null) => void;
    configForm: any;
    setConfigForm: React.Dispatch<React.SetStateAction<any>>;
    nodeSchema: any[] | null;
    setNodeSchema: React.Dispatch<React.SetStateAction<any[] | null>>;
    setShowBox2: (show: boolean) => void;
    handleSaveConfig: () => void;
}

const dtypeOptions = ["int", "float", "str"];

const NodeConfig: React.FC<Props> = ({
    selectedNode,
    setSelectedNode,
    configForm,
    setConfigForm,
    nodeSchema,
    setNodeSchema,
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

    const handleDtypeChange = (index: number, newType: string) => {
        if (!nodeSchema) return;
        const updated = [...nodeSchema];
        updated[index] = { ...updated[index], dtype: newType };
        setNodeSchema(updated);
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
                    <Box>
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

            {/* Node Schema 编辑 */}
            {nodeSchema && nodeSchema.length > 0 && (
                <Box sx={{ mt: 4, maxHeight: "50%" }}>
                    <Typography variant="h6" gutterBottom align="left">
                        节点字段信息
                    </Typography>
                    <Divider sx={{ mb: 2 }} />

                    <Box
                        sx={{
                            maxHeight: "80%",
                            overflowY: "auto",
                            pr: 1,
                        }}
                    >
                        {nodeSchema.map((item, index) => (
                            <Box
                                key={`${item.name}-${index}`}
                                sx={{
                                    display: "flex",
                                    alignItems: "center",
                                    mb: 0.5,
                                    gap: 1,
                                    px: 0.5,
                                    padding: 1,
                                }}
                            >
                                <Box sx={{ flex: 1 }}>
                                    <Typography variant="body2">{item.name}</Typography>
                                </Box>
                                <Box sx={{ flex: 1 }}>
                                    <FormControl fullWidth size="small">
                                        <InputLabel size="small">类型</InputLabel>
                                        <Select
                                            value={item.dtype}
                                            label="类型"
                                            onChange={(e) => handleDtypeChange(index, e.target.value)}
                                            size="small"
                                        >
                                            {dtypeOptions.map((dtype) => (
                                                <MenuItem key={dtype} value={dtype}>
                                                    {dtype}
                                                </MenuItem>
                                            ))}
                                        </Select>
                                    </FormControl>
                                </Box>
                            </Box>
                        ))}
                    </Box>
                </Box>
            )}




        </Paper>
    );
};

export default NodeConfig;
