import React, { useCallback } from 'react';
import { ProSidebar, Menu, MenuItem, SubMenu, SidebarHeader } from 'react-pro-sidebar';
import Grid from '@mui/material/Grid';
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

window.projectMenu = (data) => {
    // store.dispatch(setTags(existingTags));
    $(window).on('load', function () {
        $("#content").show();
    });

    function redirect(url) {
        window.location = url;
    }


    // console.log(data)
    // console.log(displayMap.urls)



    ReactDOM.render(
        <>
            <Box style={{ marginLeft: '0px', height: '100%', width: '320px' }}>
                <ProSidebar style={{ marginLeft: '-5px', paddingLeft: '0px', width: '320px' }} className="sticky" >
                    <Menu iconShape="square">
                        {data.project.system && <>
                            <SidebarHeader className="sidebardarkheader">
                                <Grid container >
                                    <Grid item xs={12}>
                                        <h2 className="sidebardark-header">
                                            {data.project.root_task.title_override}&nbsp;&nbsp;
                                            <span className="glyphicon glyphicon-pencil" style={{ fontSize: '14px', color: '#aaa', cursor: 'pointer' }}
                                                onClick={() => show_edit_project_modal()}></span>
                                        </h2>
                                        <span className="sidebardark-project-details" title={`${data.project.version_comment}`}> Project ID: {data.project.id}&nbsp;&nbsp;&nbsp;|&nbsp;&nbsp;&nbsp;System ID: {data.project.system.id}&nbsp;&nbsp;&nbsp;|&nbsp;&nbsp;&nbsp;Version: {data.project.version} <br/>{data.project.version_comment}</span>
                                        <br/>
                                        <h3 className="sidebardark-head">Portfolio: <span className="sidebardark-head-title">{data.project.portfolio.title}</span></h3>
                                    </Grid>
                                </Grid>
                            </SidebarHeader>
                            <MenuItem 
                                icon={<HomeIcon />}
                                id="menu-btn-project-home"
                                onClick={() => redirect(`${window.origin}${data.urls.home}`)}
                                onKeyPress={(e) => {
                                    if(e.key === 'Enter'){
                                        redirect(`${window.origin}${data.urls.home}`)
                                    }
                                }}
                            >
                                Project Home
                            </MenuItem>
                            <MenuItem
                                id="menu-btn-project-controls"
                                icon={<ListAltIcon />}
                                onClick={() => redirect(`${window.origin}${data.urls.controls}`)}
                                onKeyPress={(e) => {
                                    if(e.key === 'Enter'){
                                        redirect(`${window.origin}${data.urls.controls}`)
                                    }
                                }}
                            >
                                Controls
                            </MenuItem>
                            <MenuItem
                                id="menu-btn-project-components"
                                icon={<SettingsInputComponentIcon />}
                                onClick={() => redirect(`${window.origin}${data.urls.components}`)}
                                onKeyPress={(e) => {
                                    if(e.key === 'Enter'){
                                        redirect(`${window.origin}${data.urls.components}`)
                                    }
                                }}
                            >
                                Components
                            </MenuItem>
                            <MenuItem
                                id="menu-btn-project-poa_ms"
                                icon={<CheckBoxIcon />}
                                onClick={() => redirect(`${window.origin}${data.urls.poa_ms}`)}
                                onKeyPress={(e) => {
                                    if(e.key === 'Enter'){
                                        redirect(`${window.origin}${data.urls.poa_ms}`)
                                    }
                                }}
                            >
                                POA&Ms
                            </MenuItem>
                            <MenuItem
                                id="menu-btn-project-deployments"
                                icon={<ApiIcon />}
                                onClick={() => redirect(`${window.origin}${data.urls.deployments}`)}
                                onKeyPress={(e) => {
                                    if(e.key === 'Enter'){
                                        redirect(`${window.origin}${data.urls.deployments}`)
                                    }
                                }}
                            >
                                Deployments
                            </MenuItem>
                            <MenuItem
                                id="menu-btn-project-assesments"
                                icon={<AssessmentIcon />}
                                onClick={() => redirect(`${window.origin}${data.urls.assesments}`)}
                                onKeyPress={(e) => {
                                    if(e.key === 'Enter'){
                                        redirect(`${window.origin}${data.urls.assesments}`)
                                    }
                                }}
                            >
                                Assesments
                            </MenuItem>
                            <MenuItem
                                id="menu-btn-project-import"
                                icon={<ArrowUpwardIcon />}
                                onClick={() => {
                                    let m = $('#import_project_modal');
                                    $("#import_loading_spinner").hide();
                                    m.modal();
                                }}
                                onKeyPress={(e) => {
                                    if(e.key === 'Enter'){
                                        let m = $('#import_project_modal');
                                        $("#import_loading_spinner").hide();
                                        m.modal();
                                    }
                                }}
                            >
                                Import Project
                            </MenuItem>
                            <MenuItem
                                id="menu-btn-project-export_project"
                                icon={<ArrowDownward />}
                                onClick={() => redirect(`${window.origin}${data.urls.export_project}`)}
                                onKeyPress={(e) => {
                                    if(e.key === 'Enter'){
                                        redirect(`${window.origin}${data.urls.export_project}`)
                                    }
                                }}
                            >
                                Export Project
                            </MenuItem>
                        </>}
                        {(!data.project.is_account_project || data.project.is_deletable) && <>
                            <MenuItem
                                id="menu-btn-project-is_account_project"
                                icon={<SettingsIcon />}
                                onClick={() => redirect(`${window.origin}${data.urls.settings}`)}
                                onKeyPress={(e) => {
                                    if(e.key === 'Enter'){
                                        redirect(`${window.origin}${data.urls.settings}`)
                                    }
                                }}
                            >
                                Settings
                            </MenuItem>
                        </>}
                        {data.is_project_page && <>
                            <MenuItem
                                icon={<PersonAddAlt1Icon />}
                                id="menu-btn-show-project-invite"
                                onClick={() => {
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
                                }}
                                onKeyPress={(e) => {
                                    if(e.key === 'Enter'){
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
                                    }
                                }}
                            >
                                Invite
                            </MenuItem>
                            <MenuItem
                                id="menu-btn-project-reviews"
                                icon={<PreviewIcon />}
                                onClick={() => redirect(`${window.origin}${data.urls.review}`)}
                                onKeyPress={(e) => {
                                    if(e.key === 'Enter'){
                                        redirect(`${window.origin}${data.urls.review}`)
                                    }
                                }}
                            >
                                Review
                            </MenuItem>
                            <MenuItem
                                id="menu-btn-project-documents"
                                icon={<InsertDriveFileIcon />}
                                onClick={() => redirect(`${window.origin}${data.urls.documents}`)}
                                onKeyPress={(e) => {
                                    if(e.key === 'Enter'){
                                        redirect(`${window.origin}${data.urls.documents}`)
                                    }
                                }}
                            >
                                Documents
                            </MenuItem>
                            <MenuItem
                                id="menu-btn-project-apidocs"
                                icon={<CompareArrowsIcon />}
                                onClick={() => redirect(`${window.origin}${data.urls.apidocs}`)}
                                onKeyPress={(e) => {
                                    if(e.key === 'Enter'){
                                        redirect(`${window.origin}${data.urls.apidocs}`)
                                    }
                                }}
                            >
                                API Docs
                            </MenuItem>
                            <MenuItem
                                id="menu-btn-move_project"
                                icon={<ImportExportIcon />}
                                onClick={() => {
                                    move_project()
                                }}
                                onKeyPress={(e) => {
                                    if(e.key === 'Enter'){
                                        move_project()
                                    }
                                }}
                            >
                                Move Project
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
