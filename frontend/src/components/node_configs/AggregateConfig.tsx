import { Stack, TextField, Typography, IconButton, MenuItem, Button } from "@mui/material";
import { Add, Delete } from "@mui/icons-material";

interface Aggregation {
    column: string;
    operation: string;
}

interface Config {
    groupBy: string[];
    aggregations: Aggregation[];
}

interface Props {
    config: Config;
    onChange: (key: keyof Config, value: any) => void;
}

const aggregationOps = ["sum", "avg", "min", "max", "count"];

const AggregateConfig: React.FC<Props> = ({ config, onChange }) => {
    const groupBy = config.groupBy || [];
    const aggregations = config.aggregations || [];

    const handleGroupByChange = (index: number, value: string) => {
        const updated = [...groupBy];
        updated[index] = value;
        onChange("groupBy", updated);
    };

    const handleAggregationChange = (index: number, field: keyof Aggregation, value: string) => {
        const updated = [...aggregations];
        updated[index] = { ...updated[index], [field]: value };
        onChange("aggregations", updated);
    };

    return (
        <Stack spacing={2}>
            {/* Group By Section */}
            <Typography variant="subtitle1">分组列 (Group By)：</Typography>
            {groupBy.length === 0 && (
                <Typography color="text.secondary" variant="body2">
                    当前未配置分组列，请添加。
                </Typography>
            )}
            {groupBy.map((col, index) => (
                <Stack direction="row" spacing={1} key={`group-${index}`} alignItems="center">
                    <TextField
                        label="列名"
                        value={col}
                        size="small"
                        onChange={(e) => handleGroupByChange(index, e.target.value)}
                    />
                    <IconButton onClick={() => {
                        const updated = groupBy.filter((_, i) => i !== index);
                        onChange("groupBy", updated);
                    }}>
                        <Delete />
                    </IconButton>
                </Stack>
            ))}
            <Button
                startIcon={<Add />}
                onClick={() => onChange("groupBy", [...groupBy, ""])}
                size="small"
            >
                添加分组列
            </Button>

            {/* Aggregations Section */}
            <Typography variant="subtitle1">聚合配置：</Typography>
            {aggregations.length === 0 && (
                <Typography color="text.secondary" variant="body2">
                    当前未配置聚合操作，请添加。
                </Typography>
            )}
            {aggregations.map((agg, index) => (
                <Stack direction="row" spacing={1} key={`agg-${index}`} alignItems="center">
                    <TextField
                        label="列名"
                        value={agg.column}
                        size="small"
                        onChange={(e) => handleAggregationChange(index, "column", e.target.value)}
                    />
                    <TextField
                        label="操作"
                        select
                        value={agg.operation}
                        size="small"
                        onChange={(e) => handleAggregationChange(index, "operation", e.target.value)}
                    >
                        {aggregationOps.map((op) => (
                            <MenuItem key={op} value={op}>{op}</MenuItem>
                        ))}
                    </TextField>
                    <IconButton onClick={() => {
                        const updated = aggregations.filter((_, i) => i !== index);
                        onChange("aggregations", updated);
                    }}>
                        <Delete />
                    </IconButton>
                </Stack>
            ))}
            <Button
                startIcon={<Add />}
                onClick={() => onChange("aggregations", [...aggregations, { column: "", operation: "sum" }])}
                size="small"
            >
                添加聚合项
            </Button>
        </Stack>
    );
};

export default AggregateConfig;
