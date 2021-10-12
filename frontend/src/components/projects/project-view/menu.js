import React from 'react';
import { ProSidebar, Menu, MenuItem, SubMenu } from 'react-pro-sidebar';
import MenuIcon from '@mui/icons-material/Menu';
import HomeIcon from '@mui/icons-material/Home';
import SettingsInputComponentIcon from '@mui/icons-material/SettingsInputComponent';
import ListAltIcon from '@mui/icons-material/ListAlt';
import CheckBoxIcon from '@mui/icons-material/CheckBox';
import ApiIcon from '@mui/icons-material/Api';
import AssessmentIcon from '@mui/icons-material/Assessment';
import ArrowUpwardIcon from '@mui/icons-material/ArrowUpward';
import ArrowDownward from '@mui/icons-material/ArrowDownward';
import SettingsIcon from '@mui/icons-material/Settings';
import PersonAddAlt1Icon from '@mui/icons-material/PersonAddAlt1';
import PreviewIcon from '@mui/icons-material/Preview';
import InsertDriveFileIcon from '@mui/icons-material/InsertDriveFile';
import CompareArrowsIcon from '@mui/icons-material/CompareArrows';
import CreateIcon from '@mui/icons-material/Create';
import ImportExportIcon from '@mui/icons-material/ImportExport';
import Box from '@mui/material/Box';
import ReactDOM from 'react-dom';
// import { projectTagsStateSlice } from "./slice"
// import { Provider } from "react-redux";
// import store from "../../../store";
// import { TagDropdown } from "../../shared/tag-dropdown";


// const { setTags } = projectTagsStateSlice.actions;

window.projectMenu = () => {
    // store.dispatch(setTags(existingTags));
    $(window).on('load', function () {
        $("#content").show();
    });

    ReactDOM.render(
        // <>Test finally there</>
        // <Provider store={store}>
        //     asdflasdk;fjaslf;jkafdsf

        <>
            <Box >
            <ProSidebar >
                <Menu iconShape="square">
                    <MenuItem icon={<HomeIcon />}>Project Home</MenuItem>
                    {/* <MenuItem >Dashboard</MenuItem> */}
                    <MenuItem icon={<ListAltIcon />}>Controls</MenuItem>
                    <MenuItem icon={< SettingsInputComponentIcon/>}>Components</MenuItem>
                    <MenuItem icon={<CheckBoxIcon />}>POA&Ms</MenuItem>
                    <MenuItem icon={<ApiIcon  />}>Deployments</MenuItem>
                    <MenuItem icon={<AssessmentIcon  />}>Assesments</MenuItem>
                    <MenuItem icon={<ArrowUpwardIcon />}>Import Project</MenuItem>                    
                    <MenuItem icon={<ArrowDownward />}>Export Project</MenuItem>
                    <MenuItem icon={<SettingsIcon />}>Settings</MenuItem>
                    <MenuItem icon={<PersonAddAlt1Icon />}>Invite</MenuItem>
                    <MenuItem icon={<PreviewIcon />}>Review</MenuItem>
                    <MenuItem icon={<InsertDriveFileIcon />}>Documents</MenuItem>
                    <MenuItem icon={<CompareArrowsIcon />}>API Docs</MenuItem>
                    <MenuItem icon={<CreateIcon />}>Authoring Tool</MenuItem>
                    <MenuItem icon={<ImportExportIcon />}>Move Project</MenuItem>



                    {/* <SubMenu title="Components" icon={<MenuIcon />}> */}
                    {/* <SubMenu title="Components" > */}
                        {/* <MenuItem>Component 1</MenuItem> */}
                        {/* <MenuItem>Component 2</MenuItem> */}
                    {/* </SubMenu> */}

                </Menu>
            </ProSidebar>
            </Box>
            
        </>
            


        //   </Provider>, 
        ,
        document.getElementById('menu')
    );

};
