import React, { useEffect, useState } from 'react';
import { DataTable } from '../shared/table';
import axios from 'axios';
import moment from 'moment';
import { DataGrid } from '@mui/x-data-grid';
import { v4 as uuid_v4 } from "uuid";
import { Grid, } from '@mui/material';
import {
    Tooltip,
    Button,
    Glyphicon,
    OverlayTrigger,
} from 'react-bootstrap';
import { AsyncPagination } from "../shared/asyncTypeahead";

export const Permissions = ({ elementId }) => {
    const [usersList, setUsersList] = useState([]);
    const [permList, setPermList] = useState([]);
    const [permissibleUsers, setPermissibleUsers] = useState([]);

    useEffect(() => {
        axios(`/api/v2/users/`).then(response => {
            setUsersList(response.data.data);
        });
        axios(`/api/v2/element_permissions/${elementId}/`).then(response => {
            setPermList(response.data);
        })
    }, [])

    useEffect(() => {
        if(usersList.length > 0){
            setPermissibleUsers(getPermissibleUsers(permList));
        }
    }, [permList])

    const editToolTip = (<Tooltip placement="top" id='tooltip-edit'> Edit User Permissions
    </Tooltip>)
    const [records, setRecords] = useState(0);
    const [sortby, setSortBy] = useState(["username", "asc"]);

    const handleAddingNewUserPermissions = async (data) => {
      const permissible = { users_with_permissions: data }
      const response = await axios.put(`/api/v2/element_permissions/${elementId}/assign_role/`, permissible);
      if(response.status === 200){    
          window.location.reload();
      } else{
          console.error("Something went wrong")
      }
    };

    const [columns, setColumns] = useState([
        { field: 'id', headerName: 'ID', width: 90 },
        {
          field: 'userId',
          headerName: 'UserId',
          width: 150,
          editable: false,
          valueGetter: (params) => params.row.user.id,
      },
        {
            field: 'user',
            headerName: 'Username',
            width: 150,
            editable: false,
            valueGetter: (params) => params.row.user.username,
        },
        {
            field: 'email',
            headerName: 'Email',
            width: 150,
            editable: false,
            valueGetter: (params) => params.row.user.email,
        },
        {
          field: 'add',
          headerName: 'Add',
          width: 150,
          editable: false,
          renderCell: (params) => {
            return (
              <div
                style={{ width: "100%" }}
                onClick={(e) => {
                  e.stopPropagation();
                  e.preventDefault();
                }}
              >
                {params.row.add ? <Glyphicon glyph="ok" style={{ color: '#3d3d3d' }} /> : <Glyphicon glyph="remove" style={{ color: '#3d3d3d' }} />}
              </div>
            );
          },
        },
        {
            field: 'change',
            headerName: 'Change',
            width: 150,
            editable: false,
            renderCell: (params) => {
                return (
                  <div
                    style={{ width: "100%" }}
                    onClick={(e) => {
                      e.stopPropagation();
                      e.preventDefault();
                    }}
                  >
                    {params.row.change ? <Glyphicon glyph="ok" style={{ color: '#3d3d3d' }} /> : <Glyphicon glyph="remove" style={{ color: '#3d3d3d' }} />}
                  </div>
                );
              },
        },
        {
            field: 'delete',
            headerName: 'Delete',
            width: 150,
            editable: false,
            renderCell: (params) => {
                return (
                  <div
                    style={{ width: "100%" }}
                    onClick={(e) => {
                      e.stopPropagation();
                      e.preventDefault();
                    }}
                  >
                    {params.row.delete ? <Glyphicon glyph="ok" style={{ color: '#3d3d3d' }} /> : <Glyphicon glyph="remove" style={{ color: '#3d3d3d' }} />}
                  </div>
                );
              },
        },
        {
            field: 'view',
            headerName: 'View',
            width: 150,
            editable: false,
            renderCell: (params) => {
                return (
                  <div
                    style={{ width: "100%" }}
                    onClick={(e) => {
                      e.stopPropagation();
                      e.preventDefault();
                    }}
                  >
                    {params.row.view ? <Glyphicon glyph="ok" style={{ color: '#3d3d3d' }} /> : <Glyphicon glyph="remove" style={{ color: '#3d3d3d' }} />}
                  </div>
                );
              },
        },
    ]);

    const endpoint = (querystrings) => {
        return axios.get(`/api/v2/users/`, { params: querystrings });
    };


    const getPermissibleUsers = (data) => {
      let list = [];
      Object.entries(data.users_with_permissions).forEach(
        ([key, value]) => {
          const getUser = usersList.filter((user) => user.id === parseInt(key));
          const newUser = {
              id: uuid_v4(),
              user: getUser[0],
              view: value.includes('view_element'),
              change: value.includes('change_element'),
              add: value.includes('add_element'),
              delete: value.includes('delete_element'),
          }
          list.push(newUser);
        }
      );
      return list;      
    }

    return (
      <div style={{ maxHeight: '1000px', width: '100%' }}>
      <Grid
        container
        spacing={1}
        alignItems="flex-end"
        style={{ width: "100%" }}
      >
        <Grid item style={{ width: "calc(100% - 1rem - 25px" }}>
            <br />
            <AsyncPagination
                endpoint={endpoint}
                order={"username"}
                onSelect={(selected) => {
                    if (selected.length > 0) {
                        const newUser = selected.map((user) => {
                            return {
                                id: uuid_v4(),
                                user: user,
                                view: true,
                                change: true,
                                add: false,
                                delete: false,
                            };
                        });
                        setPermissibleUsers((prev) => [...prev, newUser[0]]);
                        handleAddingNewUserPermissions(newUser[0]);
                    }
                }}
                excludeIds={permissibleUsers.map((du) => du.user.id)}
            />
          </Grid>
      </Grid>
      <br />
      <Grid sx={{ minHeight: '400px' }}>
        <div style={{width: "calc(100% - 1rem - 25px", marginTop: "1rem" }}>
          <DataGrid
            autoHeight={true}
            density="compact"
            rows={permissibleUsers}
            columns={columns}
            pageSize={25}
            rowsPerPageOptions={[25]}
            checkboxSelection
            // onSelectionModelChange={(selectionModel, details) => {
            //   console.log(selectionModel, details);
            // }}
            // disableSelectionOnClick
          />
        </div>
      </Grid>
      </div>
    )
}
