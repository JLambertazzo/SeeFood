const handleShowRestRegister = () => {
  document.querySelector('.control').classList.add('hide')
  document.querySelector('.rest-register').classList.remove('hide')
}

const handleHideRestRegister = () => {
  document.querySelector('.control').classList.remove('hide')
  document.querySelector('.rest-register').classList.add('hide')
}

const handleShowRestLogin = () => {
  document.querySelector('.control').classList.add('hide')
  document.querySelector('.rest-login').classList.remove('hide')
}

const handleHideRestLogin = () => {
  document.querySelector('.control').classList.remove('hide')
  document.querySelector('.rest-login').classList.add('hide')
}

const handleShowUserRegister = () => {
  alert('Coming Soon!')
}

document.querySelector('.rest-register').addEventListener('submit', (event) => {
  event.preventDefault()
  const data = new FormData(event.target)
  const request = new Request('/api/restaurants', {
    method: 'post',
    body: JSON.stringify({
      name: data.get('name'),
      description: data.get('description'),
      password: data.get('password')
    }),
    headers: {
      'Content-Type': 'application/json'
    }
  })

  fetch(request).then(res => {
    if (res.ok) {
      window.location.replace('/dashboard')
    } else {
      alert('ERROR WITH REGISTRATION')
    }
  }).catch(error => console.log(error))
})

document.querySelector('.rest-login').addEventListener('submit', (event) => {
  event.preventDefault()
  const data = new FormData(event.target)
  const request = new Request('/api/restaurants', {
    method: 'post',
    body: JSON.stringify({
      name: data.get('name'),
      password: data.get('password')
    }),
    headers: {
      'Content-Type': 'application/json'
    }
  })

  fetch(request).then(res => {
    if (res.ok) {
      window.location.replace('/dashboard')
    } else {
      alert('ERROR WITH LOGIN')
    }
  }).catch(error => console.log(error))
})
