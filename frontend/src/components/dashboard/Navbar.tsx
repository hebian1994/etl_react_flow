import { AppBar, Toolbar, Typography, Button, IconButton } from '@mui/material';
import MenuIcon from '@mui/icons-material/Menu';
import { Link } from 'react-router-dom';

export const Navbar = () => {
    return (
        <AppBar position="static">
            <Toolbar>
                <IconButton edge="start" color="inherit" aria-label="menu" sx={{ mr: 2 }}>
                    <MenuIcon />
                </IconButton>
                <Typography variant="h6" sx={{ flexGrow: 1 }}>
                    ETL Tool
                </Typography>
                <Button color="inherit" component={Link} to="/">Flows</Button>
                <Button color="inherit" component={Link} to="/history">History</Button>
                <Button color="inherit" component={Link} to="/components">Components</Button>
            </Toolbar>
        </AppBar>
    );
};
