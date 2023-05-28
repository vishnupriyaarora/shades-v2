const results = document.getElementById('results')
const uploadStatusH2 = document.getElementById('upload-status')
const imageBox = document.getElementById('image-upload-preview')
const imageBoxIMG = imageBox ? imageBox.querySelector('img') : null

// scan page
const fileUploadInput = document.getElementById('file-upload')

if (fileUploadInput) {
	fileUploadInput.addEventListener('change', handleFileSelect, false)
}

// register page
const regform = document.getElementById('regform')
regform.addEventListener('submit', createUser, false)

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

async function setVisibilityOfElementsAccordingToState() {
	const els = document.querySelectorAll('.loginlink')

	debugger

	const isLoggedIn = !!localStorage.getItem('username')

	for (let i = 0; i < els.length; i++) {
		els[i].style.display = isLoggedIn ? 'block' : 'none'
	}
}

function createUser(e) {
	e.preventDefault()

	// Get the user data from the HTML form
	const username = document.getElementById('pno-address').value
	const password = document.getElementById('age').value
	const name = document.getElementById('name').value
	const age = document.getElementById('age').value

	// Create an object with the user data
	const userData = {
		username: username,
		password: password,
		name: name,
		age: age,
	}

	// Send a POST request to create the user
	fetch('http://146.190.112.143:3000/register', {
		method: 'POST',
		headers: {
			'Content-Type': 'application/json',
		},
		body: JSON.stringify(userData),
	})
		.then((response) => response.json())
		.then((data) => {
			// Handle the response from the server
			console.log(data) // Display the response data
			// Perform any additional actions after user creation

			if (data.status === 'ok') {
				localStorage.setItem('username', username)
				location.href = '/scan.html'
			} else {
				alert(data.error)
			}
		})
		.catch((error) => {
			console.error('Error:', error)
			// Handle any errors that occurred during the request
		})
}

setVisibilityOfElementsAccordingToState()
