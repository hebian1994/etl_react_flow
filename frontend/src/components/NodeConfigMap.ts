// components/NodeConfigMap.ts
import DataViewerConfig from "./node_configs/DataViewerConfig";
import FileInputConfig from "./node_configs/FileInputConfig";
import FilterConfig from "./node_configs/FilterConfig";
import LeftJoinConfig from "./node_configs/LeftJoinConfig";

export const NodeConfigComponentMap: Record<string, React.FC<any>> = {
    "File Input": FileInputConfig,
    "Filter": FilterConfig,
    "Data Viewer": DataViewerConfig,
    "Left Join": LeftJoinConfig,
};
