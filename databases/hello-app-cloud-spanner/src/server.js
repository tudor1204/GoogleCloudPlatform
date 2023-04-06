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
const crypto = require('crypto');
const express = require("express");
const path = require('path');
const cors = require('cors');
const app = express();
const port = process.env.PORT || 8080;

app.use(cors(), express.json(), express.static(path.resolve(__dirname, '../client/build')));

// Configures the Cloud Spanner client
const {Spanner} = require('@google-cloud/spanner');
const spanner = new Spanner({projectId: process.env.GOOGLE_CLOUD_PROJECT_ID});
const instance = spanner.instance(process.env.CLOUD_SPANNER_INSTANCE || 'hello-instance');
const database = instance.database(process.env.CLOUD_SPANNER_DATABASE || 'hello-database');

//Get all singers
app.get("/api/v1/singers", async (req, res) => {
  const [rows] = await database.run("SELECT * FROM Singers");
  res.send(rows);
});

// Insert a singer (warning: no validation is done)
app.post("/api/v1/singers", async (req, res) => {
  const { firstName, lastName, birthDate } = req.body;

  const uuid = crypto.randomUUID();
  database.runTransaction(async (error, transaction) => {
    if (error) {
      res.status(500).send({error: error.details});
      return;
    }

    try {
      await transaction.runUpdate({
        sql: `INSERT INTO Singers
          (SingerUuid, FirstName, LastName, BirthDate)
          VALUES (@singerUuid, @firstName, @lastName, @birthDate)`,
        params: {
          singerUuid: uuid,
          firstName,
          lastName,
          birthDate
        }
      });
      await transaction.commit();

      res.status(201).send({
        SingerUuid: uuid,
        FirstName: firstName,
        LastName: lastName,
        BirthDate: birthDate
      });
    } catch (error) {
      res.status(500).send({error: error.details});
    }
  });
});

// Deletes a given singer (warning: no validation is done)
app.delete("/api/v1/singers/:uuid", async (req, res) => {
  const uuid = req.params.uuid;

  database.runTransaction(async (error, transaction) => {
    if (error) {
      res.status(500).send({ error: error.details });
      return;
    }

    try {
      await transaction.runUpdate({
        sql: `DELETE FROM Singers WHERE SingerUuid = @singerUuid`,
        params: { singerUuid: uuid }
      });
      await transaction.commit();

      res.status(204).send();
    } catch (error) {
      res.status(500).send({ error: error.details });
    }
  });
});

app.get("*", (req, res) => {
  res.sendFile(path.resolve(__dirname, "../client/build", "index.html"));
});

//Start the server
app.listen(port, () => console.log(`App listening on port ${port}!`));
