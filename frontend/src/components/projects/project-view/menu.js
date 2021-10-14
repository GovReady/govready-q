import React, { useCallback } from 'react';
import { ProSidebar, Menu, MenuItem, SubMenu } from 'react-pro-sidebar';
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

window.projectMenu = (displayMap) => {
    // store.dispatch(setTags(existingTags));
    $(window).on('load', function () {
        $("#content").show();
    });

    function redirect(url) {
        window.location = url;
    }       
    
    // console.log(displayMap);
    console.log(displayMap.system.project);
    // console.log(displayMap.system.urls)

    ReactDOM.render(
        <>
            <Box >
                <ProSidebar style={{ marginLeft: '-15px' }} >
                    <Menu iconShape="square">
                        {displayMap.system.visible && <>
                            <MenuItem ><h2>{displayMap.system.project.title}</h2></MenuItem>
                            <MenuItem icon={<HomeIcon />} onClick={() => redirect(`${window.origin}${displayMap.system.urls.home}`)}> Project Home
                            </MenuItem>
                            <MenuItem icon={<ListAltIcon />} onClick={() => redirect(`${window.origin}${displayMap.system.urls.controls}`)}> Controls
                            </MenuItem>
                            <MenuItem icon={<SettingsInputComponentIcon />} onClick={() => redirect(`${window.origin}${displayMap.system.urls.components}`)}> Components
                            </MenuItem>
                            <MenuItem icon={<CheckBoxIcon />} onClick={() => redirect(`${window.origin}${displayMap.system.urls.poa_ms}`)}> POA&Ms
                            </MenuItem>
                            <MenuItem icon={<ApiIcon />} onClick={() => redirect(`${window.origin}${displayMap.system.urls.deployments}`)}> Deployments
                            </MenuItem>
                            <MenuItem icon={<AssessmentIcon />} onClick={() => redirect(`${window.origin}${displayMap.system.urls.assesments}`)}> Assesments
                            </MenuItem>
                            <MenuItem icon={<ArrowUpwardIcon />} onClick={() => {
                                var m = $('#import_project_modal');
                                $("#import_loading_spinner").hide();
                                m.modal();
                            }}> Import Project
                            </MenuItem>
                            <MenuItem icon={<ArrowDownward />} onClick={() => redirect(`${window.origin}${displayMap.system.urls.export_project}`)}> Export Project
                            </MenuItem>
                        </>}

                        {!displayMap.system.visible || displayMap.system.visible && <>

                            <MenuItem icon={<SettingsIcon />} onClick={() => redirect(`${window.origin}${displayMap.system.urls.settings}`)} >Settings
                            </MenuItem>
                            <MenuItem icon={<PersonAddAlt1Icon />} onClick={() => {
                                var info = project_invitation_info;
                                show_invite_modal(
                                    'Invite To Project Team (' + info.model_title + ')',
                                    'Invite a colleague to join this project team.',
                                    info,
                                    'Please join the project team for ' + info.model_title + '.',
                                    {
                                        project: info.model_id,
                                        add_to_team: "1"
                                    },
                                    function () { window.location.reload() }
                                );
                                return false;
                            }}>Invite
                            </MenuItem>
                            <MenuItem icon={<PreviewIcon />} onClick={() => redirect(`${window.origin}${displayMap.system.urls.review}`)} >Review
                            </MenuItem>
                            <MenuItem icon={<InsertDriveFileIcon />} onClick={() => redirect(`${window.origin}${displayMap.system.urls.documents}`)} >Documents
                            </MenuItem>
                            <MenuItem icon={<CompareArrowsIcon />} onClick={() => redirect(`${window.origin}${displayMap.system.urls.apidocs}`)} >API Docs
                            </MenuItem>
                            <MenuItem icon={<CreateIcon />} onClick={() => {
                                show_authoring_tool_module_editor()
                            }}>Authoring Tool
                            </MenuItem>
                            <MenuItem icon={<ImportExportIcon />} onClick={() => {
                                move_project()
                            }}>Move Project
                            </MenuItem>
                        </>}

                    </Menu>
                </ProSidebar>
            </Box>

        </>
        ,
        document.getElementById('menu')
    );

};
