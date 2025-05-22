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

type PreviewDataType = {
    cols: string[];
    data: Array<Record<string, any>>;
};

type NodeDataPreviewProps = {
    show: boolean;
    previewData: PreviewDataType | null;
    setPreviewData: React.Dispatch<React.SetStateAction<PreviewDataType | null>>;
};

const NodeDataPreview: React.FC<NodeDataPreviewProps> = ({ show, previewData, setPreviewData }) => {
    if (!show) return null;

    const cols = previewData?.cols || [];
    const data = previewData?.data || [];

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
                <Button variant="outlined" color="secondary" onClick={() => setPreviewData(null)}>
                    关闭
                </Button>
            </Stack>

            {data.length > 0 && cols.length > 0 ? (
                <Box>
                    <Table size="small">
                        <TableHead>
                            <TableRow>
                                {cols.map((col) => (
                                    <TableCell key={col} sx={{ fontWeight: 'bold' }}>
                                        {col}
                                    </TableCell>
                                ))}
                            </TableRow>
                        </TableHead>
                        <TableBody>
                            {data.map((row, idx) => (
                                <TableRow key={idx} hover>
                                    {cols.map((col) => (
                                        <TableCell key={col}>
                                            {row[col] !== null && row[col] !== undefined ? String(row[col]) : ''}
                                        </TableCell>
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
