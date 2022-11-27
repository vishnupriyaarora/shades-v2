const fileUploadInput = document.getElementById("file-upload")
const results = document.getElementById("results")
const uploadStatusH2 = document.getElementById("upload-status")
const imageBox = document.getElementById("image-upload-preview")
const imageBoxIMG = imageBox.querySelector("img")

fileUploadInput.addEventListener("change", handleFileSelect, false)

function sleep(duration) {
	return new Promise((resolve) => {
		setTimeout(() => {
			resolve()
		}, duration)
	})
}

async function handleFileSelect(evt) {
	let files = evt.target.files // FileList object

	// use the 1st file from the list
	let file = files[0]

	const tempImageSrc = URL.createObjectURL(file)

	imageBox.style.display = "block"
	imageBox.querySelector("img").setAttribute("src", tempImageSrc)
	uploadStatusH2.innerText = "Uploading..."

	// TODO: Make a backend call to send this image

	await sleep(2000)

	// TODO: Show the backend response data here
	const backendResponse = {
		diseaseType: "xyz",
		quality: 0.5,
		probability: 0.66,
		name: "XYZ",
		gender: "female",
	}

	uploadStatusH2.innerText = ""
	imageBoxIMG.classList.remove("opacity-40")

	results.innerText = JSON.stringify(backendResponse, null, 4)
}
