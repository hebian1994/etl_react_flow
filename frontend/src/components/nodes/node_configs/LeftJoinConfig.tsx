import { Stack, TextField, Typography } from "@mui/material";

interface Props {
    config: { left_join_on: string };
    onChange: (key: any, value: string) => void;
}

const LeftJoinConfig: React.FC<Props> = ({ config, onChange }) => {
    return (
        <Stack direction="row" alignItems="center" spacing={1}>
            <Typography>JOIN条件：</Typography>
            <TextField
                value={config.left_join_on}
                // fullWidth
                onChange={(e) => onChange("left_join_on", e.target.value)}
                size="small"
            />
        </Stack>
    );
};

export default LeftJoinConfig;
