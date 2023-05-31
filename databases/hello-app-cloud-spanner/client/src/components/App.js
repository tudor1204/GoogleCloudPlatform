/*
Copyright 2023 Google LLC
Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at
    https://www.apache.org/licenses/LICENSE-2.0
Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
*/
import React, { useState, useEffect } from "react";
import Alert from "@mui/material/Alert";
import Container from "@mui/material/Container";
import CssBaseline from '@mui/material/CssBaseline';
import Divider from "@mui/material/Divider";
import Grid from '@mui/material/Grid';
import Typography from "@mui/material/Typography";
import { LocalizationProvider } from '@mui/x-date-pickers';
import { AdapterDayjs } from '@mui/x-date-pickers/AdapterDayjs'
import { getSingers } from "../services/singers";

import SingerList from "./SingerList";
import CreateSinger from "./CreateSinger";

export default function App() {
    const [error, setError] = useState('');
    const [singers, setSingers] = useState([]);

    useEffect(() => {
        const fetchSingers = async () => {
            try {
                const response = await getSingers();
                setSingers(response.data);
                setError('');
            } catch(error) {
                setError('Error fetching singers from database');
            }
        };
        fetchSingers();
    }, []);

    return <LocalizationProvider dateAdapter={AdapterDayjs}>
        <Container maxWidth="md">
            <CssBaseline />
            <Grid container rowSpacing={2}>
                <Grid container direction="row" justifyContent="center" item xs={12}>
                    <Typography variant="h3">Singers Registry</Typography>
                </Grid>
                <Grid item xs={12}>
                    <Divider />
                </Grid>
                {error !== '' &&
                    <Grid container style={{ marginBottom: "15px" }}>
                        <Grid item xs={12}>
                            <Alert severity="error" onClose={() => setError('')}>{error}</Alert>
                        </Grid>
                    </Grid>
                }
                <Grid item xs={12}>
                    <CreateSinger setError={setError} singers={singers} setSingers={setSingers} />
                </Grid>
                <Grid item xs={12}>
                    <Divider />
                </Grid>
                <Grid item xs={12}>
                    <SingerList setError={setError} singers={singers} setSingers={setSingers} />
                </Grid>
            </Grid>
        </Container>
    </LocalizationProvider>;
}
