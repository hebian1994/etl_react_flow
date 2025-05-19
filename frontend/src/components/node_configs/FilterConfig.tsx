// components/configs/FilterConfig.tsx
import { Stack, TextField, Typography } from "@mui/material";

interface Props {
    config: { condition: string };
    onChange: (key: any, value: string) => void;
}

const FilterConfig: React.FC<Props> = ({ config, onChange }) => {
    return (
        <Stack direction="row" alignItems="center" spacing={1}>
            <Typography>过滤条件：</Typography>
            <TextField
                value={config.condition}
                // fullWidth
                onChange={(e) => onChange("condition", e.target.value)}
                size="small"
            />
        </Stack>
    );
};

export default FilterConfig;
