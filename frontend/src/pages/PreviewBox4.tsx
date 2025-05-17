import React from 'react';

type PreviewBox4Props = {
    show: boolean;
    previewData: Array<Record<string, any>> | null;
    setPreviewData: React.Dispatch<React.SetStateAction<Array<Record<string, any>> | null>>;
};

const PreviewBox4: React.FC<PreviewBox4Props> = ({ show, previewData, setPreviewData }) => {
    if (!show) return null;

    return (
        <div className="box4">
            {previewData && (
                <div>
                    <div>
                        <h3>数据预览1</h3>
                        <button onClick={() => setPreviewData([])}>
                            关闭
                        </button>
                        <div className="p-4 overflow-auto">
                            {previewData.length === 0 ? (
                                <p className="text-gray-500">暂无数据</p>
                            ) : (
                                <table className="text-sm w-full border">
                                    <thead className="bg-white">
                                        <tr>
                                            {Object.keys(previewData[0]).map((col) => (
                                                <th key={col} className="text-left border-b p-1 font-medium">
                                                    {col}
                                                </th>
                                            ))}
                                        </tr>
                                    </thead>
                                    <tbody>
                                        {previewData.map((row, idx) => (
                                            <tr key={idx} className="hover:bg-gray-50">
                                                {Object.values(row).map((val, i) => (
                                                    <td key={i} className="border-b p-1">
                                                        {String(val)}
                                                    </td>
                                                ))}
                                            </tr>
                                        ))}
                                    </tbody>
                                </table>
                            )}
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
};

export default PreviewBox4;
