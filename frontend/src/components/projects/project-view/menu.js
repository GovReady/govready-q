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


    console.log(data)
    // console.log(displayMap.urls)

    ReactDOM.render(
        <>
            <Box style={{ marginLeft: '0px', height: '100%', width: '320px' }}>
                <ProSidebar style={{ marginLeft: '-5px', paddingLeft: '0px', width: '320px' }} >
                    <Menu iconShape="square">
                        {data.project.system && <>
                            <SidebarHeader>
                                <Grid container >
                                    <Grid item xs={12}>
                                        <h1 style={{ marginLeft: '20px', marginTop: '40px', color: 'white' }}>
                                            {data.project.root_task.title_override}&nbsp;&nbsp;
                                            <span className="glyphicon glyphicon-pencil" style={{ fontSize: '14px', color: '#aaa', cursor: 'pointer' }}
                                                onClick={() => show_edit_project_modal()}></span>
                                        </h1>

                                    </Grid>
                                    <Grid item xs={12}>
                                        <h3 style={{ marginLeft: '20px', color: '#ADADAD' }}>Other: {data.project.portfolio.version}</h3>
                                    </Grid>
                                    <Grid item xs={12}>
                                        <h3 style={{ marginLeft: '20px', color: '#ADADAD'  }}>{data.project.root_task.module.spec.title}</h3>
                                    </Grid>
                                    <Grid item xs={12}>
                                        <h3 style={{ marginLeft: '20px', color: '#ADADAD'  }}>Portfolio: {data.project.portfolio.title}</h3>
                                    </Grid>
                                </Grid>
                                <Grid container spacing={.5}>
                                    <Grid item xs={6}>
                                        <h3 style={{ marginLeft: '20px', color: '#ADADAD'  }}>Project ID: {data.project.id}</h3>
                                    </Grid>
                                    <Grid item xs={6}>
                                        <h3 style={{ marginLeft: '20px', color: '#ADADAD'  }}>System ID: {data.project.system.id}</h3>
                                    </Grid>
                                </Grid>

                            </SidebarHeader>
                            <MenuItem icon={<HomeIcon />} id="btn-project-home" onClick={() => redirect(`${window.origin}${data.urls.home}`)}> <button class="button-sidebar-react">Project Home</button>
                            </MenuItem>
                            <MenuItem icon={<ListAltIcon />} id="btn-controls" onClick={() => redirect(`${window.origin}${data.urls.controls}`)}> <button class="button-sidebar-react">Controls</button>
                            </MenuItem>
                            <MenuItem icon={<SettingsInputComponentIcon />} id="btn-components" onClick={() => redirect(`${window.origin}${data.urls.components}`)}> <button class="button-sidebar-react">Components</button>
                            </MenuItem>
                            <MenuItem icon={<CheckBoxIcon />} id="btn-poams" onClick={() => redirect(`${window.origin}${data.urls.poa_ms}`)}> <button class="button-sidebar-react">POA&Ms</button>
                            </MenuItem>
                            <MenuItem icon={<ApiIcon />} id="btn-deployments" onClick={() => redirect(`${window.origin}${data.urls.deployments}`)}> <button class="button-sidebar-react">Deployments</button>
                            </MenuItem>
                            <MenuItem icon={<AssessmentIcon />} id="btn-assessments" onClick={() => redirect(`${window.origin}${data.urls.assesments}`)}> <button class="button-sidebar-react">Assesments</button>
                            </MenuItem>
                            <MenuItem icon={<ArrowUpwardIcon />} id="btn-import-project" onClick={() => {
                                var m = $('#import_project_modal');
                                $("#import_loading_spinner").hide();
                                m.modal();
                            }}> <button class="button-sidebar-react">Import Project</button>
                            </MenuItem>
                            <MenuItem icon={<ArrowDownward />} onClick={() => redirect(`${window.origin}${data.urls.export_project}`)}> <button class="button-sidebar-react">Export Project</button>
                            </MenuItem>
                        </>}
                        {(!data.project.is_account_project || data.project.is_deletable) && <>
                            <MenuItem icon={<SettingsIcon />} id="btn-settings" onClick={() => redirect(`${window.origin}${data.urls.settings}`)} ><button class="button-sidebar-react"> Settings</button>
                            </MenuItem>
                        </>}
                        {data.is_project_page && <>
                            <MenuItem icon={<PersonAddAlt1Icon />} id="btn-show-project-invite" onClick={() => {
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
                            }}> <button class="button-sidebar-react">Invite</button>
                            </MenuItem>
                            <MenuItem icon={<PreviewIcon />} id="btn-review" onClick={() => redirect(`${window.origin}${data.urls.review}`)} ><button class="button-sidebar-react">Review</button>
                            </MenuItem>
                            <MenuItem icon={<InsertDriveFileIcon />} id="btn-documents" onClick={() => redirect(`${window.origin}${data.urls.documents}`)} ><button class="button-sidebar-react">Documents</button>
                            </MenuItem>
                            <MenuItem icon={<CompareArrowsIcon />} id="btn-apidocs" onClick={() => redirect(`${window.origin}${data.urls.apidocs}`)} ><button class="button-sidebar-react">API Docs</button>
                            </MenuItem>
                            <MenuItem icon={<CreateIcon />} id="btn-authoring-tool" onClick={() => {
                                show_authoring_tool_module_editor()
                            }}><button class="button-sidebar-react">Authoring Tool</button>
                            </MenuItem>
                            <MenuItem icon={<ImportExportIcon />} id="btn-move-project" onClick={() => {
                                move_project()
                            }}><button class="button-sidebar-react">Move Project</button>
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
