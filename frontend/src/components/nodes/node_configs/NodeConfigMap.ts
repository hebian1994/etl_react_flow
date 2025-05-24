import AggregateConfig from "./Aggregate/AggregateConfig";
import DataViewerConfig from "./DataViewerConfig";
import FileInputConfig from "./FileInputConfig";
import FilterConfig from "./FilterConfig";
import LeftJoinConfig from "./LeftJoinConfig";



export const NodeConfigComponentMap: Record<string, React.FC<any>> = {
    "File Input": FileInputConfig,
    "Filter": FilterConfig,
    "Data Viewer": DataViewerConfig,
    "Left Join": LeftJoinConfig,
    "Aggregate": AggregateConfig,
};
