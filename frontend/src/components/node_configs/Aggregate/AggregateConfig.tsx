import React from "react";
import {
    Stack,
    TextField,
    Typography,
    IconButton,
    MenuItem,
    Button,
} from "@mui/material";
import { Add, Delete } from "@mui/icons-material";
import { Formik, Form, FieldArray, Field, getIn } from "formik";
import * as Yup from "yup";

export interface Aggregation {
    column: string;
    operation: string;
}

export interface AggregateConfig {
    groupBy: string[];
    aggregations: Aggregation[];
}

interface Props {
    config: AggregateConfig;
    onChange: (key: keyof AggregateConfig, value: any) => void;
}

const aggregationOps = ["sum", "avg", "min", "max", "count"];

const validationSchema = Yup.object().shape({
    groupBy: Yup.array()
        .of(Yup.string().required("列名不能为空"))
        .min(1, "至少添加一个分组列"),
    aggregations: Yup.array().of(
        Yup.object().shape({
            column: Yup.string().required("列名不能为空"),
            operation: Yup.string()
                .oneOf(aggregationOps)
                .required("请选择操作"),
        })
    ),
});

const AggregateConfig: React.FC<Props> = ({ config, onChange }) => {

    console.log("config", config);
    return (
        <Formik
            initialValues={config}
            validationSchema={validationSchema}
            validateOnChange
            validateOnBlur
            onSubmit={(values) => {
                // 通常不需要 submit，直接 onChange 即可
                onChange("groupBy", values.groupBy);
                onChange("aggregations", values.aggregations);
            }}
        >
            {({ values, errors, touched, handleChange, handleBlur }) => (
                <Form>
                    <Stack spacing={2}>
                        {/* Group By Section */}
                        <Typography variant="subtitle1">分组列 (Group By)：</Typography>

                        <FieldArray name="groupBy">
                            {({ push, remove }) => (
                                <>
                                    {values.groupBy.length === 0 && (
                                        <Typography color="text.secondary" variant="body2">
                                            当前未配置分组列，请添加。
                                        </Typography>
                                    )}
                                    {values.groupBy.map((col, index) => {
                                        const error = getIn(errors, `groupBy.${index}`);
                                        const touch = getIn(touched, `groupBy.${index}`);
                                        return (
                                            <Stack
                                                direction="row"
                                                spacing={1}
                                                key={`group-${index}`}
                                                alignItems="center"
                                            >
                                                <TextField
                                                    label="列名"
                                                    name={`groupBy.${index}`}
                                                    value={col}
                                                    onChange={(e) => {
                                                        handleChange(e);
                                                        onChange("groupBy", [
                                                            ...values.groupBy.slice(0, index),
                                                            e.target.value,
                                                            ...values.groupBy.slice(index + 1),
                                                        ]);
                                                    }}
                                                    onBlur={handleBlur}
                                                    size="small"
                                                    error={!!(touch && error)}
                                                    helperText={touch && error}
                                                />
                                                <IconButton onClick={() => {
                                                    remove(index);
                                                    onChange("groupBy", values.groupBy.filter((_, i) => i !== index));
                                                }}>
                                                    <Delete />
                                                </IconButton>
                                            </Stack>
                                        );
                                    })}
                                    <Button
                                        startIcon={<Add />}
                                        onClick={() => {
                                            push("");
                                            onChange("groupBy", [...values.groupBy, ""]);
                                        }}
                                        size="small"
                                    >
                                        添加分组列
                                    </Button>
                                </>
                            )}
                        </FieldArray>

                        {/* Aggregations Section */}
                        <Typography variant="subtitle1">聚合配置：</Typography>
                        <FieldArray name="aggregations">
                            {({ push, remove }) => (
                                <>
                                    {values.aggregations.length === 0 && (
                                        <Typography color="text.secondary" variant="body2">
                                            当前未配置聚合操作，请添加。
                                        </Typography>
                                    )}
                                    {values.aggregations.map((agg, index) => {
                                        const colError = getIn(errors, `aggregations.${index}.column`);
                                        const colTouch = getIn(touched, `aggregations.${index}.column`);
                                        const opError = getIn(errors, `aggregations.${index}.operation`);
                                        const opTouch = getIn(touched, `aggregations.${index}.operation`);

                                        return (
                                            <Stack
                                                direction="row"
                                                spacing={1}
                                                key={`agg-${index}`}
                                                alignItems="center"
                                            >
                                                <TextField
                                                    label="列名"
                                                    name={`aggregations.${index}.column`}
                                                    value={agg.column}
                                                    onChange={(e) => {
                                                        handleChange(e);
                                                        const updated = [...values.aggregations];
                                                        updated[index].column = e.target.value;
                                                        onChange("aggregations", updated);
                                                    }}
                                                    onBlur={handleBlur}
                                                    size="small"
                                                    error={!!(colTouch && colError)}
                                                    helperText={colTouch && colError}
                                                />
                                                <TextField
                                                    label="操作"
                                                    select
                                                    name={`aggregations.${index}.operation`}
                                                    value={agg.operation}
                                                    onChange={(e) => {
                                                        handleChange(e);
                                                        const updated = [...values.aggregations];
                                                        updated[index].operation = e.target.value;
                                                        onChange("aggregations", updated);
                                                    }}
                                                    onBlur={handleBlur}
                                                    size="small"
                                                    error={!!(opTouch && opError)}
                                                    helperText={opTouch && opError}
                                                >
                                                    {aggregationOps.map((op) => (
                                                        <MenuItem key={op} value={op}>
                                                            {op}
                                                        </MenuItem>
                                                    ))}
                                                </TextField>
                                                <IconButton onClick={() => {
                                                    remove(index);
                                                    const updated = values.aggregations.filter((_, i) => i !== index);
                                                    onChange("aggregations", updated);
                                                }}>
                                                    <Delete />
                                                </IconButton>
                                            </Stack>
                                        );
                                    })}
                                    <Button
                                        startIcon={<Add />}
                                        onClick={() => {
                                            push({ column: "", operation: "sum" });
                                            onChange("aggregations", [...values.aggregations, { column: "", operation: "sum" }]);
                                        }}
                                        size="small"
                                    >
                                        添加聚合项
                                    </Button>
                                </>
                            )}
                        </FieldArray>
                    </Stack>
                </Form>
            )}
        </Formik>
    );
};

export default AggregateConfig;
