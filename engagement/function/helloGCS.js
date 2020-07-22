/**
 * Triggered from a change to a Cloud Storage bucket.
 *
 * @param {!Object} event Event payload.
 * @param {!Object} context Metadata for the event.
 */
const http = require('http')
const Firestore = require('@google-cloud/firestore')
const { FieldValue } = require("@google-cloud/firestore")

const db = new Firestore({
    credentials: {
        client_email: process.env.GCLOUD_DATASTORE_EMAIL,
        private_key: process.env.GCLOUD_PRIVATE_KEY
    }
})

function getFileName(name) {
    const slashIndex = name.indexOf("/")
    const dotIndex = name.lastIndexOf(".")
    const underIndex = name.indexOf("_")

    return {
        parent: name.substring(0, slashIndex),
        uuid: name.substring(slashIndex + 1, underIndex),
        filename: name.substring(slashIndex + 1, dotIndex),
        extension: name.substring(dotIndex + 1)
    }
}

exports.helloGCS = async (event, context) => {
    const gcsEvent = event;
    const fileAttrs = getFileName(gcsEvent.name)
    const collection = db.collection("classroom");
    console.log(`Processing file: ${gcsEvent.name}`);
    console.log(fileAttrs)

    if (fileAttrs.extension === "m4a") {
        http.get(`http://10.128.0.7:5000/ffmpeg/${gcsEvent.name}`, (res) => {
            console.log('statusCode:', res.statusCode);
            console.log('headers:', res.headers);

            res.on('data', (d) => {
                process.stdout.write(d);
            });
        }).on('error', (e) => {
            console.error(e);
        });
    }
    else if (fileAttrs.extension === "mp4" || fileAttrs.extension === "wav") {
        await db.collection("classroom").doc(fileAttrs.uuid).update({
            state: "UPLOADED",
            timestamp: FieldValue.serverTimestamp()
        })
        try {
            const res = await db.runTransaction(async t => {
                const snapshotRef = await db.collection("classroom").where("parent", "==", fileAttrs.parent).where("state", "==", "UPLOADED")
                const classRef = db.collection("classroom").doc(fileAttrs.parent)
                const parent = await t.get(classRef)
                const snapshot = await t.get(snapshotRef)
                const parentData = parent.data()
                const script = parentData.hasOwnProperty('script')
                console.log(parentData.expected, snapshot._size, script)
                if (parentData.expected === snapshot._size && !script) {
                    await t.update(collection.doc(fileAttrs.parent), {
                        script: "SCRIPT_STARTED",
                        timestamp: FieldValue.serverTimestamp()
                    })
                    http.get(`http://10.128.0.7:5000/script/${fileAttrs.parent}`, (res) => {
                        console.log('statusCode:', res.statusCode);
                        console.log('headers:', res.headers);

                        res.on('data', (d) => {
                            process.stdout.write(d);
                        });
                    }).on('error', (e) => {
                        console.error(e);
                    });
                    return 'The transaction suceeded'
                }
                else {
                    throw 'The script has already been ran!'
                }
            })
            console.log("Transacton Succeeded", res)

        } catch (e) {
            console.log('The script has already started')
        }
    }
};
