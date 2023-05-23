const fileUploadInput = document.getElementById('file-upload')
const results = document.getElementById('results')
const uploadStatusH2 = document.getElementById('upload-status')
const imageBox = document.getElementById('image-upload-preview')
const imageBoxIMG = imageBox.querySelector('img')

fileUploadInput.addEventListener('change', handleFileSelect, false)

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

	imageBox.style.display = 'block'
	imageBox.querySelector('img').setAttribute('src', tempImageSrc)
	uploadStatusH2.innerText = 'Uploading...'

	// TODO: Make a backend call to send this image

	// Create a FormData object to send the file in the request body
	const formData = new FormData()
	formData.append('file', file)

	// TODO: Show the backend response data here
	let backendResponse = {}

	try {
		const response = await fetch(
			'http://146.190.112.143:3000/model-output',
			{
				method: 'POST',
				body: formData,
			}
		)
		const data = await response.json()
		backendResponse = data
	} catch (error) {
		console.error(error)
	}

	await sleep(2000)

	uploadStatusH2.innerText = ''
	imageBoxIMG.classList.remove('opacity-40')

	results.innerText = JSON.stringify(backendResponse, null, 4)
}
