require("dotenv").config();
const express = require("express"),
  bodyParser = require("body-parser"),
  multer = require("multer"),
  multerGoogleStorage = require("multer-google-storage"),
  uuid = require("uuid").v1,
  cors = require("cors")

const Firestore = require("@google-cloud/firestore");
const { FieldValue } = require("@google-cloud/firestore");

const db = new Firestore({
  projectId: "marble-281321",
  keyFilename: "./Marble-8181cca99a94.json",
});

const upload = multer({
  storage: multerGoogleStorage.storageEngine({
    filename: async (req, file, cb) => {
      const collection = db.collection("classroom");
      const file_uuid = uuid();
      const file_type = file.mimetype.substring(0, file.mimetype.lastIndexOf("/"))
      const record = {
        state: "CREATED",
        timestamp: FieldValue.serverTimestamp()
      }
      console.log(file_uuid)
      if (file_type === "audio" || file_type === "video") {
        if (!req.hasOwnProperty("parentUuid")) {
          req.parentUuid = file_uuid;
          record.expected = 1
          record.parent = file_uuid
        }
        else {
          record.parent = req.parentUuid
          await collection.doc(req.parentUuid).update({
            expected: FieldValue.increment(1),
            timestamp: FieldValue.serverTimestamp()
          }).catch((err) => {
            console.log(err);
          });
        }
        await collection
          .doc(file_uuid).set(record).catch((err) => {
            console.log(err);
          });
      }
      cb(null, req.parentUuid + "/" + file_uuid + "_" + file.originalname);
    },
  }),
});
const app = express();

app.use(express.json());
app.use(bodyParser.urlencoded({ extended: true }));
app.use(cors())

app.post("/upload", upload.array("files"), async function (req, res) {
  console.log(JSON.stringify(req.files));
  if (req.files.length === 0) {
    res.redirect("http://localhost:5500/front-end/index.html");
    return;
  }

  const filenames = req.files.map((value) => {
    return value.filename
  })
  res.redirect("http://localhost:5500/front-end/marble.html");
});

app.get("/data", async function (req, res) {
  const collection = db.collection("classroom").where("state", "==", "POPULATED").orderBy("timestamp", "desc").limit(1);
  const snapshot = await collection.get();
  let data = {};
  snapshot.forEach((doc) => {
    console.log(doc.data())
    const dataList = Object.keys(doc.data().data).map((value) => {
      return doc.data().data[value]
    })
    data["data"] = dataList
  });
  console.log("Data of all classrooms has been sent");
  res.status(200).send(data);
});

app.get("/data/:uuid", async function (req, res) {
  const collection = db.collection("classroom")
  const doc = await collection.doc(req.params.uuid).get()

  console.log("GET " + req.params.uuid)
  if (doc.data().hasOwnProperty('data')) {
    const dataList = Object.keys(doc.data().data).map((value) => {
      return doc.data().data[value]
    })
    res.status(200).send({ data: dataList })
  }
  else {
    res.status(200).send({ data: [] })
  }

})

app.listen(5000);
