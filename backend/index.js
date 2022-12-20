const express = require("express")
const multer = require("multer")
const cors = require("cors")
const tf = require("@tensorflow/tfjs")
const tfn = require("@tensorflow/tfjs-node")
const path = require("path")

const app = express()
const upload = multer()

app.use(cors())

function preprocessImage(imageBuffer) {
	// Convert the image from a binary buffer to a 3-dimensional tensor.
	const imageTensor = tfn.node.decodeImage(imageBuffer)

	// Resize the image to match the input size of the model.
	const resizedImage = tfn.image.resize(imageTensor, [224, 224])

	// Normalize the pixel values in the image.
	const normalizedImage = tfn.image.per_image_standardization(resizedImage)

	// Add a batch dimension to the image so it can be passed to the model.
	const batchedImage = normalizedImage.expandDims(0)

	return batchedImage
}

const model = tf.loadLayersModel("http://localhost:3001/tfjs_model/model.json")

app.post("/model-output", upload.single("file"), async (req, res) => {
	const fileData = req.file?.buffer

	if (!fileData) return res.json({ status: "error", error: "No file found" })

	const preprocessedImage = preprocessImage(fileData)

	// Pass the preprocessed image to the model and get the output.
	const output = model.predict(preprocessedImage)

	console.log({ output })

	res.json({ status: "ok" })
})

app.listen(3000, () => {
	console.log("Server listening on port 3000")
})
