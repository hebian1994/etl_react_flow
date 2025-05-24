import React from 'react';
import { Menu, MenuItem } from '@mui/material';

interface MenuAction {
    label: string;
    onClick: () => void;
}

interface ContextMenuProps {
    visible: boolean;
    x: number;
    y: number;
    onClose: () => void;
    actions: MenuAction[];
}

const ContextMenu: React.FC<ContextMenuProps> = ({ visible, x, y, onClose, actions }) => {
    const [menuPosition, setMenuPosition] = React.useState<null | { top: number; left: number }>(null);

    React.useEffect(() => {
        if (visible) {
            setMenuPosition({ top: y, left: x });
        } else {
            setMenuPosition(null);
        }
    }, [visible, x, y]);

    return (
        <Menu
            open={visible}
            onClose={onClose}
            anchorReference="anchorPosition"
            anchorPosition={menuPosition ? { top: menuPosition.top, left: menuPosition.left } : undefined}
        >
            {actions.map((action, index) => (
                <MenuItem
                    key={index}
                    onClick={() => {
                        action.onClick();
                        onClose();
                    }}
                >
                    {action.label}
                </MenuItem>
            ))}
            <MenuItem onClick={onClose}>取消</MenuItem>
        </Menu>
    );
};

export default ContextMenu;
