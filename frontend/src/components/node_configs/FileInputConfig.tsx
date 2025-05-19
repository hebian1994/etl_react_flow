// src/components/configs/FileInputConfig.tsx

import React from "react";
import { Stack, TextField, Typography } from "@mui/material";

export const nodeType = "File Input";

interface Props {
    config: { path: string };
    onChange: (key: any, value: string) => void;
}

const FileInputConfig: React.FC<Props> = ({ config, onChange }) => {
    return (
        <Stack direction="row" alignItems="center" spacing={1}>
            <Typography>文件路径：</Typography>
            <TextField
                value={config.path}
                onChange={(e) => onChange("path", e.target.value)}
                size="small"
                // fullWidth
            />
        </Stack>
    );
};

export default FileInputConfig;
