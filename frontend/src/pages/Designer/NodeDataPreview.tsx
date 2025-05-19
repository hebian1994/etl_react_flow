import React from 'react';
import {
    Paper,
    Typography,
    Button,
    Table,
    TableHead,
    TableRow,
    TableCell,
    TableBody,
    Box,
    Stack
} from '@mui/material';

type NodeDataPreviewProps = {
    show: boolean;
    previewData: Array<Record<string, any>> | null;
    setPreviewData: React.Dispatch<React.SetStateAction<Array<Record<string, any>> | null>>;
};

const NodeDataPreview: React.FC<NodeDataPreviewProps> = ({ show, previewData, setPreviewData }) => {
    if (!show) return null;

    return (
        <Paper
            elevation={3}
            sx={{
                p: 2,
                position: 'relative',
                borderTop: '1px solid #ddd',
                maxHeight: '300px',
                overflow: 'auto',
                backgroundColor: '#fafafa'
            }}
        >
            <Stack direction="row" justifyContent="space-between" alignItems="center" mb={2}>
                <Typography variant="h6" component="div">
                    数据预览
                </Typography>
                <Button variant="outlined" color="secondary" onClick={() => setPreviewData([])}>
                    关闭
                </Button>
            </Stack>

            {previewData && previewData.length > 0 ? (
                <Box>
                    <Table size="small">
                        <TableHead>
                            <TableRow>
                                {Object.keys(previewData[0]).map((col) => (
                                    <TableCell key={col} sx={{ fontWeight: 'bold' }}>
                                        {col}
                                    </TableCell>
                                ))}
                            </TableRow>
                        </TableHead>
                        <TableBody>
                            {previewData.map((row, idx) => (
                                <TableRow key={idx} hover>
                                    {Object.values(row).map((val, i) => (
                                        <TableCell key={i}>{String(val)}</TableCell>
                                    ))}
                                </TableRow>
                            ))}
                        </TableBody>
                    </Table>
                </Box>
            ) : (
                <Typography variant="body2" color="text.secondary">
                    暂无数据
                </Typography>
            )}
        </Paper>
    );
};

export default NodeDataPreview;
