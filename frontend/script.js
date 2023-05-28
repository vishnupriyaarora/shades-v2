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
if (regform) regform.addEventListener('submit', createUser, false)

// login page
const loginform = document.getElementById('loginform')
if (loginform) loginform.addEventListener('submit', loginUser, false)

function sleep(duration) {
	return new Promise((resolve) => {
		setTimeout(() => {
			resolve()
		}, duration)
	})
}

async function handleFileSelect(evt) {
	let files = evt.target.files // FileList object
	const file = files[0]
	if (!file) return

	const fileName = file.name.toLowerCase()
	if (
		fileName.endsWith('jpg') ||
		fileName.endsWith('png') ||
		fileName.endsWith('gif')
	) {
		alert('Only .jpg, .png, or .gif file formats are allowed')
		return
	}

	const tempImageSrc = URL.createObjectURL(file)

	imageBox.style.display = 'block'
	imageBox.querySelector('img').setAttribute('src', tempImageSrc)
	uploadStatusH2.innerText = 'Uploading...'

	// TODO: Make a backend call to send this image

	// Create a FormData object to send the file in the request body
	const formData = new FormData()
	formData.append('file', file)
	if (localStorage.getItem('username'))
		formData.append('username', localStorage.getItem('username'))

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

	const isLoggedIn = !!localStorage.getItem('username')

	for (let i = 0; i < els.length; i++) {
		els[i].style.display = isLoggedIn ? 'block' : 'none'
	}
}

function loginUser(e) {
	e.preventDefault()

	// Get the user data from the HTML form
	const username = document.getElementById('pno-address').value
	const password = document.getElementById('password').value

	// Create an object with the user data
	const userData = {
		username: username,
		password: password,
	}

	document
		.querySelector('button[type=submit]')
		.setAttribute('disabled', 'true')

	// Send a POST request to create the user
	fetch('http://146.190.112.143:3000/login', {
		method: 'POST',
		headers: {
			'Content-Type': 'application/json',
		},
		body: JSON.stringify(userData),
	})
		.then((response) => {
			if (!response.ok) return Promise.reject('error')
			response.text()
		})
		.then((data) => {
			if (data === 'not-found-error') {
				alert(
					'Something went wrong logging. Please check your username and password.'
				)
			} else {
				localStorage.setItem('name', data)
				localStorage.setItem('username', username)
				location.href = '/scan.html'
			}
		})
		.catch((error) => {
			console.error('Error:', error)
			alert(
				'Something went wrong logging. Please check your username and password and try again.'
			)
		})
		.finally(() => {
			document
				.querySelector('button[type=submit]')
				.removeAttribute('disabled')
		})
}

function createUser(e) {
	e.preventDefault()

	// Get the user data from the HTML form
	const username = document.getElementById('pno-address').value
	const password = document.getElementById('password').value
	const name = document.getElementById('name').value
	const age = document.getElementById('age').value

	// Create an object with the user data
	const userData = {
		username: username,
		password: password,
		name: name,
		age: age,
	}

	document
		.querySelector('button[type=submit]')
		.setAttribute('disabled', 'true')

	// Send a POST request to create the user
	fetch('http://146.190.112.143:3000/register', {
		method: 'POST',
		headers: {
			'Content-Type': 'application/json',
		},
		body: JSON.stringify(userData),
	})
		.then((response) => response.text())
		.then((data) => {
			if (data === 'ok') {
				localStorage.setItem('username', username)
				location.href = '/scan.html'
			} else if (data === 'exists') {
				alert('User already exists. Please try a different number')
			} else {
				alert('Something went wrong registering. Please try again.')
			}
		})
		.catch((error) => {
			console.error('Error:', error)
			// Handle any errors that occurred during the request
		})
		.finally(() => {
			document
				.querySelector('button[type=submit]')
				.removeAttribute('disabled')
		})
}

setVisibilityOfElementsAccordingToState()
